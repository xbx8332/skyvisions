from flask_restful import Resource, reqparse
from flasgger import swag_from
from flask import jsonify
from ..models import UserRole
from ..extensions import db
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import IntegrityError
from app.config import ERROR_CODES

def handle_request_parse_error(error):
    """处理 reqparse 验证错误"""
    message = str(error)
    if hasattr(error, 'data') and error.data and 'message' in error.data:
        for param, msg in error.data['message'].items():
            return {'message': msg, 'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']}, 400
    param = message.split(':')[-1].strip() if ':' in message else 'unknown'
    return {
        'message': f'参数错误：{param}' if ':' in message else message,
        'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']
    }, 400

class UserRoleResource(Resource):
    @swag_from('docs/user_roles/get_user_role.yml')
    def get(self, ur_id):
        try:
            user_role = UserRole.query.get(ur_id)
            if not user_role:
                return {
                    'message': f'记录不存在：ID={ur_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            return {
                'message': '用户角色关联获取成功',
                'data': user_role.to_dict()
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class UserRoleCreateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('user_id', type=int, required=True, help='参数不能为空：user_id', location='form')
    parser.add_argument('role_id', type=int, required=True, help='参数不能为空：role_id', location='form')

    @swag_from('docs/user_roles/create_user_role.yml')
    def post(self):
        try:
            args = self.parser.parse_args()
            if UserRole.query.filter_by(user_id=args['user_id'], role_id=args['role_id']).first():
                return {
                    'message': f'用户角色关联已存在：user_id={args["user_id"]}, role_id={args["role_id"]}',
                    'error_code': ERROR_CODES['INVALID_PARAM_KEY']
                }, 400
            user_role = UserRole(
                user_id=args['user_id'],
                role_id=args['role_id']
            )
            db.session.add(user_role)
            db.session.commit()
            return {'message': '用户角色关联创建成功', 'id': user_role.id}, 201
        except IntegrityError:
            db.session.rollback()
            return {
                'message': f'用户角色关联已存在：user_id={args["user_id"]}, role_id={args["role_id"]}',
                'error_code': ERROR_CODES['INVALID_PARAM_KEY']
            }, 400
        except BadRequest as e:
            return handle_request_parse_error(e)
        except Exception as e:
            db.session.rollback()
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class UserRoleUpdateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('user_id', type=int, required=False, help='参数不能为空：user_id', location='form')
    parser.add_argument('role_id', type=int, required=False, help='参数不能为空：role_id', location='form')

    @swag_from('docs/user_roles/update_user_role.yml')
    def put(self, ur_id):
        try:
            args = self.parser.parse_args()
            user_role = UserRole.query.get(ur_id)
            if not user_role:
                return {
                    'message': f'记录不存在：ID={ur_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            if args['user_id'] is not None and args['role_id'] is not None:
                existing = UserRole.query.filter_by(user_id=args['user_id'], role_id=args['role_id']).first()
                if existing and existing.id != ur_id:
                    return {
                        'message': f'用户角色关联已存在：user_id={args["user_id"]}, role_id={args["role_id"]}',
                        'error_code': ERROR_CODES['INVALID_PARAM_KEY']
                    }, 400
            if args['user_id'] is not None:
                user_role.user_id = args['user_id']
            if args['role_id'] is not None:
                user_role.role_id = args['role_id']
            db.session.commit()
            return {
                'message': '用户角色关联更新成功',
                'id': ur_id
            }, 200
        except IntegrityError:
            db.session.rollback()
            return {
                'message': f'用户角色关联已存在：user_id={args["user_id"]}, role_id={args["role_id"]}',
                'error_code': ERROR_CODES['INVALID_PARAM_KEY']
            }, 400
        except BadRequest as e:
            return handle_request_parse_error(e)
        except Exception as e:
            db.session.rollback()
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class UserRoleDeleteResource(Resource):
    @swag_from('docs/user_roles/delete_user_role.yml')
    def delete(self, ur_id):
        try:
            user_role = UserRole.query.get(ur_id)
            if not user_role:
                return {
                    'message': f'记录不存在：ID={ur_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            db.session.delete(user_role)
            db.session.commit()
            return {
                'message': '用户角色关联删除成功',
                'id': ur_id
            }, 200
        except IntegrityError:
            db.session.rollback()
            return {
                'message': '无法删除：用户角色关联被其他记录引用',
                'error_code': ERROR_CODES['INVALID_PARAM_KEY']
            }, 400
        except Exception as e:
            db.session.rollback()
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class UserRoleListResource(Resource):
    @swag_from('docs/user_roles/list_user_roles.yml')
    def get(self):
        try:
            user_roles = UserRole.query.all()
            return {
                'message': '用户角色关联列表获取成功',
                'data': [ur.to_dict() for ur in user_roles]
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class UserRolePageResource(Resource):
    @swag_from('docs/user_roles/page_user_roles.yml')
    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int, default=1, location='args', help='页码必须为正整数')
            parser.add_argument('page_size', type=int, default=10, location='args', help='页面大小必须为正整数')
            args = parser.parse_args()
            if args['page'] < 1 or args['page_size'] < 1:
                return {
                    'message': '页码和页面大小必须为正整数',
                    'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']
                }, 400
            pagination = UserRole.query.paginate(page=args['page'], per_page=args['page_size'], error_out=False)
            return {
                'message': '分页用户角色关联获取成功',
                'data': [item.to_dict() for item in pagination.items],
                'total': pagination.total,
                'page': args['page'],
                'page_size': args['page_size']
            }, 200
        except BadRequest as e:
            return handle_request_parse_error(e)
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500