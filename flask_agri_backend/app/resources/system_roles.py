from flask_restful import Resource, reqparse
from flasgger import swag_from
from flask import jsonify
from ..models import SystemRole
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

class SystemRoleResource(Resource):
    @swag_from('docs/system_roles/get_system_role.yml')
    def get(self, role_id):
        try:
            role = SystemRole.query.get(role_id)
            if not role:
                return {
                    'message': f'记录不存在：ID={role_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            return {
                'message': '系统角色获取成功',
                'data': role.to_dict()
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class SystemRoleCreateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help='参数不能为空：name', location='form')
    parser.add_argument('description', type=str, required=False, location='form')

    @swag_from('docs/system_roles/create_system_role.yml')
    def post(self):
        try:
            args = self.parser.parse_args()
            if SystemRole.query.filter_by(name=args['name']).first():
                return {
                    'message': f'角色名称已存在：name={args["name"]}',
                    'error_code': ERROR_CODES['INVALID_PARAM_KEY']
                }, 400
            role = SystemRole(
                name=args['name'],
                description=args['description']
            )
            db.session.add(role)
            db.session.commit()
            return {'message': '系统角色创建成功', 'id': role.id}, 201
        except IntegrityError:
            db.session.rollback()
            return {
                'message': f'角色名称已存在：name={args["name"]}',
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

class SystemRoleUpdateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=False, help='参数不能为空：name', location='form')
    parser.add_argument('description', type=str, required=False, location='form')

    @swag_from('docs/system_roles/update_system_role.yml')
    def put(self, role_id):
        try:
            args = self.parser.parse_args()
            role = SystemRole.query.get(role_id)
            if not role:
                return {
                    'message': f'记录不存在：ID={role_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            if args['name'] is not None:
                existing = SystemRole.query.filter_by(name=args['name']).first()
                if existing and existing.id != role_id:
                    return {
                        'message': f'角色名称已存在：name={args["name"]}',
                        'error_code': ERROR_CODES['INVALID_PARAM_KEY']
                    }, 400
            if args['name'] is not None:
                role.name = args['name']
            if args['description'] is not None:
                role.description = args['description']
            db.session.commit()
            return {
                'message': '系统角色更新成功',
                'id': role_id
            }, 200
        except IntegrityError:
            db.session.rollback()
            return {
                'message': f'角色名称已存在：name={args["name"]}',
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

class SystemRoleDeleteResource(Resource):
    @swag_from('docs/system_roles/delete_system_role.yml')
    def delete(self, role_id):
        try:
            role = SystemRole.query.get(role_id)
            if not role:
                return {
                    'message': f'记录不存在：ID={role_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            db.session.delete(role)
            db.session.commit()
            return {
                'message': '系统角色删除成功',
                'id': role_id
            }, 200
        except IntegrityError:
            db.session.rollback()
            return {
                'message': '无法删除：角色被其他记录引用',
                'error_code': ERROR_CODES['INVALID_PARAM_KEY']
            }, 400
        except Exception as e:
            db.session.rollback()
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class SystemRoleListResource(Resource):
    @swag_from('docs/system_roles/list_system_roles.yml')
    def get(self):
        try:
            roles = SystemRole.query.all()
            return {
                'message': '系统角色列表获取成功',
                'data': [role.to_dict() for role in roles]
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class SystemRolePageResource(Resource):
    @swag_from('docs/system_roles/page_system_roles.yml')
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
            pagination = SystemRole.query.paginate(page=args['page'], per_page=args['page_size'], error_out=False)
            return {
                'message': '分页系统角色获取成功',
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