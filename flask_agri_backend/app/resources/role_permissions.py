from flask_restful import Resource, reqparse
from flasgger import swag_from
from flask import jsonify
from ..models import RolePermission
from ..extensions import db
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import IntegrityError
from app.config import ERROR_CODES

def handle_request_parse_error(error):
    """自定义 reqparse 错误处理，返回标准化的中文错误响应"""
    message = str(error)
    if hasattr(error, 'data') and error.data and 'message' in error.data:
        for param, msg in error.data['message'].items():
            return {'message': msg, 'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']}, 400
    param = message.split(':')[-1].strip() if ':' in message else 'unknown'
    return {'message': f'参数不能为空：{param}', 'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']}, 400

class RolePermissionResource(Resource):
    @swag_from('docs/role_permissions/get_role_permission.yml')
    def get(self, rp_id):
        try:
            role_permission = RolePermission.query.get(rp_id)
            if not role_permission:
                return {
                    'message': f'记录不存在：ID={rp_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            return {
                'message': '角色权限关联获取成功',
                'data': role_permission.to_dict()
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class RolePermissionCreateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('role_id', type=int, required=True, help='参数不能为空：role_id', location='form')
    parser.add_argument('permission_id', type=int, required=True, help='参数不能为空：permission_id', location='form')

    @swag_from('docs/role_permissions/create_role_permission.yml')
    def post(self):
        try:
            args = self.parser.parse_args()
            if RolePermission.query.filter_by(role_id=args['role_id'], permission_id=args['permission_id']).first():
                return {
                    'message': f'记录已存在：role_id={args["role_id"]}, permission_id={args["permission_id"]}',
                    'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']
                }, 400
            role_permission = RolePermission(
                role_id=args['role_id'],
                permission_id=args['permission_id']
            )
            db.session.add(role_permission)
            db.session.commit()
            return {'message': '角色权限关联创建成功', 'id': role_permission.id}, 201
        except IntegrityError:
            db.session.rollback()
            return {
                'message': f'记录已存在：role_id={args["role_id"]}, permission_id={args["permission_id"]}',
                'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']
            }, 400
        except BadRequest as e:
            return handle_request_parse_error(e)
        except Exception as e:
            db.session.rollback()
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class RolePermissionUpdateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('role_id', type=int, required=False, help='参数不能为空：role_id', location='form')
    parser.add_argument('permission_id', type=int, required=False, help='参数不能为空：permission_id', location='form')

    @swag_from('docs/role_permissions/update_role_permission.yml')
    def put(self, rp_id):
        try:
            args = self.parser.parse_args()
            role_permission = RolePermission.query.get(rp_id)
            if not role_permission:
                return {
                    'message': f'记录不存在：ID={rp_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            if args['role_id'] is not None and args['permission_id'] is not None:
                existing = RolePermission.query.filter_by(role_id=args['role_id'], permission_id=args['permission_id']).first()
                if existing and existing.id != rp_id:
                    return {
                        'message': f'记录已存在：role_id={args["role_id"]}, permission_id={args["permission_id"]}',
                        'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']
                    }, 400
            if args['role_id'] is not None:
                role_permission.role_id = args['role_id']
            if args['permission_id'] is not None:
                role_permission.permission_id = args['permission_id']
            db.session.commit()
            return {
                'message': '角色权限关联更新成功',
                'id': rp_id
            }, 200
        except IntegrityError:
            db.session.rollback()
            return {
                'message': f'记录已存在：role_id={args["role_id"]}, permission_id={args["permission_id"]}',
                'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']
            }, 400
        except BadRequest as e:
            return handle_request_parse_error(e)
        except Exception as e:
            db.session.rollback()
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class RolePermissionDeleteResource(Resource):
    @swag_from('docs/role_permissions/delete_role_permission.yml')
    def delete(self, rp_id):
        try:
            role_permission = RolePermission.query.get(rp_id)
            if not role_permission:
                return {
                    'message': f'记录不存在：ID={rp_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            db.session.delete(role_permission)
            db.session.commit()
            return {
                'message': '角色权限关联删除成功',
                'id': rp_id
            }, 200
        except Exception as e:
            db.session.rollback()
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class RolePermissionListResource(Resource):
    @swag_from('docs/role_permissions/list_role_permissions.yml')
    def get(self):
        try:
            role_permissions = RolePermission.query.all()
            return {
                'message': '角色权限关联列表获取成功',
                'data': [rp.to_dict() for rp in role_permissions]
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class RolePermissionPageResource(Resource):
    @swag_from('docs/role_permissions/page_role_permissions.yml')
    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int, default=1, location='args', help='页码必须为正整数')
            parser.add_argument('page_size', type=int, default=200, location='args', help='页面大小必须为正整数')
            args = parser.parse_args()
            if args['page'] < 1 or args['page_size'] < 1:
                return {
                    'message': '页码和页面大小必须为正整数',
                    'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']
                }, 400
            pagination = RolePermission.query.paginate(page=args['page'], per_page=args['page_size'], error_out=False)
            return {
                'message': '分页角色权限关联获取成功',
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