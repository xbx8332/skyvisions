from flask_restful import Resource, reqparse
from flasgger import swag_from
from flask import jsonify
from ..models import SystemPermission
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

class SystemPermissionResource(Resource):
    @swag_from('docs/system_permissions/get_system_permission.yml')
    def get(self, permission_id):
        try:
            permission = SystemPermission.query.get(permission_id)
            if not permission:
                return {
                    'message': f'记录不存在：ID={permission_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            return {
                'message': '系统权限获取成功',
                'data': permission.to_dict()
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class SystemPermissionCreateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help='参数不能为空：name', location='form')
    parser.add_argument('code', type=str, required=True, help='参数不能为空：code', location='form')
    parser.add_argument('description', type=str, required=False, location='form')

    @swag_from('docs/system_permissions/create_system_permission.yml')
    def post(self):
        try:
            args = self.parser.parse_args()
            if SystemPermission.query.filter_by(code=args['code']).first():
                return {
                    'message': f'权限代码已存在：code={args["code"]}',
                    'error_code': ERROR_CODES['INVALID_PARAM_KEY']
                }, 400
            permission = SystemPermission(
                name=args['name'],
                code=args['code'],
                description=args['description']
            )
            db.session.add(permission)
            db.session.commit()
            return {'message': '系统权限创建成功', 'id': permission.id}, 201
        except IntegrityError:
            db.session.rollback()
            return {
                'message': f'权限代码已存在：code={args["code"]}',
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

class SystemPermissionUpdateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=False, help='参数不能为空：name', location='form')
    parser.add_argument('code', type=str, required=False, help='参数不能为空：code', location='form')
    parser.add_argument('description', type=str, required=False, location='form')

    @swag_from('docs/system_permissions/update_system_permission.yml')
    def put(self, permission_id):
        try:
            args = self.parser.parse_args()
            permission = SystemPermission.query.get(permission_id)
            if not permission:
                return {
                    'message': f'记录不存在：ID={permission_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            if args['code'] is not None:
                existing = SystemPermission.query.filter_by(code=args['code']).first()
                if existing and existing.id != permission_id:
                    return {
                        'message': f'权限代码已存在：code={args["code"]}',
                        'error_code': ERROR_CODES['INVALID_PARAM_KEY']
                    }, 400
            if args['name'] is not None:
                permission.name = args['name']
            if args['code'] is not None:
                permission.code = args['code']
            if args['description'] is not None:
                permission.description = args['description']
            db.session.commit()
            return {
                'message': '系统权限更新成功',
                'id': permission_id
            }, 200
        except IntegrityError:
            db.session.rollback()
            return {
                'message': f'权限代码已存在：code={args["code"]}',
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

class SystemPermissionDeleteResource(Resource):
    @swag_from('docs/system_permissions/delete_system_permission.yml')
    def delete(self, permission_id):
        try:
            permission = SystemPermission.query.get(permission_id)
            if not permission:
                return {
                    'message': f'记录不存在：ID={permission_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            db.session.delete(permission)
            db.session.commit()
            return {
                'message': '系统权限删除成功',
                'id': permission_id
            }, 200
        except IntegrityError:
            db.session.rollback()
            return {
                'message': '无法删除：权限被其他记录引用',
                'error_code': ERROR_CODES['INVALID_PARAM_KEY']
            }, 400
        except Exception as e:
            db.session.rollback()
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class SystemPermissionListResource(Resource):
    @swag_from('docs/system_permissions/list_system_permissions.yml')
    def get(self):
        try:
            permissions = SystemPermission.query.all()
            return {
                'message': '系统权限列表获取成功',
                'data': [permission.to_dict() for permission in permissions]
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class SystemPermissionPageResource(Resource):
    @swag_from('docs/system_permissions/page_system_permissions.yml')
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
            pagination = SystemPermission.query.paginate(page=args['page'], per_page=args['page_size'], error_out=False)
            return {
                'message': '分页系统权限获取成功',
                'data': [item.to_dict() for item in pagination.items],
                'total': pagination.total,
                'page': args['page'],
                'page_size': args['page_size']
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500