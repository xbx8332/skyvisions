from flask_restful import Resource, reqparse
from flasgger import swag_from
from ..models import SystemUser
from ..extensions import db
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import jwt_required
from app.config import ERROR_CODES
import re
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

class SystemUserResource(Resource):
    @swag_from('docs/system_users/get_user.yml')
    def get(self, user_id):
        try:
            user = SystemUser.query.get(user_id)
            if not user:
                return {
                    'message': f'记录不存在：user_id={user_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            return {
                'message': '用户获取成功',
                'data': user.to_dict()
            }, 200
        except Exception as e:
            logger.error(f"获取用户失败：user_id={user_id}, 错误：{str(e)}")
            return {
                'message': f'服务器错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class SystemUserCreateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help='用户名不能为空', location='form')
    parser.add_argument('email', type=parse_email, required=False, location='form')
    parser.add_argument('password_hash', type=str, required=True, help='密码不能为空', location='form')
    parser.add_argument('status', type=str, required=False, choices=('active', 'disabled'), help='状态必须为 "active" 或 "disabled"', location='form')

    @jwt_required()
    @swag_from('docs/system_users/create_user.yml')
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
                password_hash=generate_password_hash(args['password_hash']),
                status=args['status'] or 'active'
            )
            db.session.add(user)
            db.session.commit()
            logger.info(f"创建用户成功：username={username}, id={user.id}")
            return {'message': '用户创建成功', 'id': user.id}, 201
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"创建用户失败：username={username}, 数据库错误：{str(e)}")
            return {
                'message': f'用户已存在：username={username}',
                'error_code': ERROR_CODES.get('INVALID_PARAM_KEY', '1')
            }, 400
        except BadRequest as e:
            logger.error(f"创建用户失败：参数解析错误：{str(e)}")
            return handle_request_parse_error(e)
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建用户失败：username={username}, 错误：{str(e)}")
            return {
                'message': f'服务器错误：{str(e)}',
                'error_code': ERROR_CODES.get('DATABASE_ERROR', '5001')
            }, 500


class SystemUserUpdateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=False, location='form')
    parser.add_argument('email', type=parse_email, required=False, location='form')
    parser.add_argument('password_hash', type=str, required=False, location='form')
    parser.add_argument('status', type=str, required=False, choices=('active', 'disabled'), help='状态必须为 "active" 或 "disabled"', location='form')

    @jwt_required()
    @swag_from('docs/system_users/update_user.yml')
    def put(self, user_id):
        try:
            args = self.parser.parse_args()
            user = SystemUser.query.get(user_id)
            if not user:
                return {
                    'message': f'记录不存在：user_id={user_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            if args['username'] is not None:
                existing_user = SystemUser.query.filter_by(username=args['username']).first()
                if existing_user and existing_user.id != user_id:
                    return {
                        'message': f'用户已存在：username={args["username"]}',
                        'error_code': ERROR_CODES.get('INVALID_PARAM_KEY', '1')
                    }, 400
            if args['username'] is not None:
                user.username = args['username']
            if args['email'] is not None:
                user.email = args['email']
            if args['password_hash'] is not None:
                user.password_hash = generate_password_hash(args['password_hash'])
            if args['status'] is not None:
                user.status = args['status']
            db.session.commit()
            logger.info(f"更新用户成功：user_id={user_id}, username={user.username}")
            return {
                'message': '用户更新成功',
                'id': user_id
            }, 200
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"更新用户失败：user_id={user_id}, username={args.get('username')}, 数据库错误：{str(e)}")
            return {
                'message': f'用户已存在：username={args.get("username", "未知")}',
                'error_code': ERROR_CODES.get('INVALID_PARAM_KEY', '1')
            }, 400
        except BadRequest as e:
            logger.error(f"更新用户失败：user_id={user_id}, 参数解析错误：{str(e)}")
            return handle_request_parse_error(e)
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新用户失败：user_id={user_id}, 错误：{str(e)}")
            return {
                'message': f'服务器错误：{str(e)}',
                'error_code': ERROR_CODES.get('DATABASE_ERROR', '5001')
            }, 500

class SystemUserDeleteResource(Resource):
    @jwt_required()
    @swag_from('docs/system_users/delete_user.yml')
    def delete(self, user_id):
        try:
            user = SystemUser.query.get(user_id)
            if not user:
                return {
                    'message': f'记录不存在：user_id={user_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            db.session.delete(user)
            db.session.commit()
            logger.info(f"删除用户成功：user_id={user_id}")
            return {
                'message': '用户删除成功',
                'id': user_id
            }, 200
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"删除用户失败：user_id={user_id}, 数据库错误：{str(e)}")
            return {
                'message': '无法删除：用户被其他记录引用',
                'error_code': ERROR_CODES.get('INVALID_PARAM_KEY', '1')
            }, 400
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除用户失败：user_id={user_id}, 错误：{str(e)}")
            return {
                'message': f'服务器错误：{str(e)}',
                'error_code': ERROR_CODES.get('DATABASE_ERROR', '5001')
            }, 500

class SystemUserListResource(Resource):
    @jwt_required()
    @swag_from('docs/system_users/list_users.yml')
    def get(self):
        try:
            users = SystemUser.query.all()
            return {
                'message': '用户列表获取成功',
                'data': [user.to_dict() for user in users]
            }, 200
        except Exception as e:
            logger.error(f"获取用户列表失败：错误：{str(e)}")
            return {
                'message': f'服务器错误：{str(e)}',
                'error_code': ERROR_CODES.get('DATABASE_ERROR', '5001')
            }, 500

class SystemUserPageResource(Resource):
    @jwt_required()
    @swag_from('docs/system_users/page_users.yml')
    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int, default=1, location='args', help='页码必须为正整数')
            parser.add_argument('page_size', type=int, default=10, location='args', help='页面大小必须为正整数')
            args = parser.parse_args()
            if args['page'] < 1 or args['page_size'] < 1:
                return {
                    'message': '页码和页面大小必须为正整数',
                    'error_code': ERROR_CODES.get('INVALID_PARAM_FORMAT', '1')
                }, 400
            pagination = SystemUser.query.paginate(page=args['page'], per_page=args['page_size'], error_out=False)
            return {
                'message': '分页用户获取成功',
                'data': [user.to_dict() for user in pagination.items],
                'total': pagination.total,
                'page': args['page'],
                'page_size': args['page_size']
            }, 200
        except BadRequest as e:
            logger.error(f"获取分页用户失败：参数解析错误：{str(e)}")
            return handle_request_parse_error(e)
        except Exception as e:
            logger.error(f"获取分页用户失败：错误：{str(e)}")
            return {
                'message': f'服务器错误：{str(e)}',
                'error_code': ERROR_CODES.get('DATABASE_ERROR', '5001')
            }, 500