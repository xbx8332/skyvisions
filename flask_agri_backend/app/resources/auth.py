from flasgger import swag_from
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity,get_jwt
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import SystemUser
from app.config import ERROR_CODES
import re
from ..extensions import db,redis_client
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

def handle_request_parse_error(error):
    """处理 reqparse 验证错误"""
    message = str(error)
    if hasattr(error, 'data') and error.data and 'message' in error.data:
        for param, msg in error.data['message'].items():
            return {'message': f'参数错误：{msg}', 'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']}, 400
    return {
        'message': f'参数错误：{message}',
        'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']
    }, 400

def parse_email(value):
    """验证邮箱格式"""
    if value and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
        raise ValueError('无效的邮箱格式')
    return value

class LoginResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help='用户名不能为空')
    parser.add_argument('password', type=str, required=True, help='密码不能为空')

    @swag_from('docs/auth/login.yml')
    def post(self):
        args = self.parser.parse_args()
        user = SystemUser.query.filter_by(username=args['username']).first()
        if not user or not user.check_password(args['password']):
            return {"message": "用户名或密码错误"}, 401
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return {
            "code": 200,
            "message": "登录成功",
            "data": {
                "access_token": access_token,
                "refresh_token": refresh_token
            }
            
        }, 200

class RegisterResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help='用户名不能为空', location='form')
    parser.add_argument('email', type=parse_email, required=False, help='邮箱格式无效', location='form')
    parser.add_argument('password', type=str, required=True, help='密码不能为空', location='form')

    @swag_from('docs/auth/register.yml')
    def post(self):
        try:
            args = self.parser.parse_args()
            username = args['username']
            if SystemUser.query.filter_by(username=username).first():
                return {
                    'message': f'用户已存在：username={username}',
                    'error_code': ERROR_CODES.get('INVALID_PARAM_KEY', '1')
                }, 400
            user = SystemUser(
                username=username,
                email=args['email'],
                password_hash=generate_password_hash(args['password']),
                status='active'
            )
            db.session.add(user)
            db.session.commit()
            logger.info(f"用户注册成功：username={username}, id={user.id}")
            return {'code': 200,'message': '用户注册成功', 'id': user.id}, 201
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"用户注册失败：username={username}, 数据库错误：{str(e)}")
            return {
                'message': f'用户已存在：username={username}',
                'error_code': ERROR_CODES.get('INVALID_PARAM_KEY', '1')
            }, 400
        except BadRequest as e:
            logger.error(f"用户注册失败：参数解析错误：{str(e)}")
            return handle_request_parse_error(e)
        except Exception as e:
            db.session.rollback()
            logger.error(f"用户注册失败：username={username}, 错误：{str(e)}")
            return {
                'message': f'服务器错误：{str(e)}',
                'error_code': ERROR_CODES.get('DATABASE_ERROR', '5001')
            }, 500

class RefreshResource(Resource):
    @jwt_required(refresh=True)
    @swag_from('docs/auth/refresh.yml')
    def post(self):
        current_user = get_jwt_identity()
        jti = get_jwt()['jti']
        # 将 refresh_token 的 jti 加入黑名单，设置过期时间
        redis_client.setex(f"blacklist:{jti}", timedelta(days=30), "revoked")
        new_access_token = create_access_token(identity=current_user)
        return {'code': 200, "message":"令牌刷新成功","data":{ "access_token": new_access_token }}, 200

class LogoutResource(Resource):
    @jwt_required()
    @swag_from('docs/auth/logout.yml')
    def post(self):
        jti = get_jwt()['jti']
        # 将 access_token 的 jti 加入黑名单，设置过期时间
        redis_client.setex(f"blacklist:{jti}", timedelta(minutes=15), "revoked")
        return {'code': 200, "message": "注销成功"}, 200