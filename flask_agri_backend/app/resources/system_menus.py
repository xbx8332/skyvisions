from flask_restful import Resource, reqparse
from flasgger import swag_from
from flask import jsonify
from ..models import SystemMenu
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

class SystemMenuResource(Resource):
    @swag_from('docs/system_menus/get_system_menu.yml')
    def get(self, menu_id):
        try:
            menu = SystemMenu.query.get(menu_id)
            if not menu:
                return {
                    'message': f'记录不存在：ID={menu_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            return {
                'message': '系统菜单获取成功',
                'data': menu.to_dict()
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class SystemMenuCreateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('parent_id', type=int, required=False, location='form')
    parser.add_argument('name', type=str, required=True, help='参数不能为空：name', location='form')
    parser.add_argument('path', type=str, required=True, help='参数不能为空：path', location='form')
    parser.add_argument('icon', type=str, required=False, location='form')
    parser.add_argument('order_num', type=int, required=False, location='form')

    @swag_from('docs/system_menus/create_system_menu.yml')
    def post(self):
        try:
            args = self.parser.parse_args()
            menu = SystemMenu(
                parent_id=args['parent_id'],
                name=args['name'],
                path=args['path'],
                icon=args['icon'],
                order_num=args['order_num']
            )
            db.session.add(menu)
            db.session.commit()
            return {'message': '系统菜单创建成功', 'id': menu.id}, 201
        except IntegrityError:
            db.session.rollback()
            return {
                'message': '记录已存在：菜单名称或路径重复',
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

class SystemMenuUpdateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('parent_id', type=int, required=False, location='form')
    parser.add_argument('name', type=str, required=False, help='参数不能为空：name', location='form')
    parser.add_argument('path', type=str, required=False, help='参数不能为空：path', location='form')
    parser.add_argument('icon', type=str, required=False, location='form')
    parser.add_argument('order_num', type=int, required=False, location='form')

    @swag_from('docs/system_menus/update_system_menu.yml')
    def put(self, menu_id):
        try:
            args = self.parser.parse_args()
            menu = SystemMenu.query.get(menu_id)
            if not menu:
                return {
                    'message': f'记录不存在：ID={menu_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            if args['parent_id'] is not None:
                menu.parent_id = args['parent_id']
            if args['name'] is not None:
                menu.name = args['name']
            if args['path'] is not None:
                menu.path = args['path']
            if args['icon'] is not None:
                menu.icon = args['icon']
            if args['order_num'] is not None:
                menu.order_num = args['order_num']
            db.session.commit()
            return {
                'message': '系统菜单更新成功',
                'id': menu_id
            }, 200
        except IntegrityError:
            db.session.rollback()
            return {
                'message': '记录已存在：菜单名称或路径重复',
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

class SystemMenuDeleteResource(Resource):
    @swag_from('docs/system_menus/delete_system_menu.yml')
    def delete(self, menu_id):
        try:
            menu = SystemMenu.query.get(menu_id)
            if not menu:
                return {
                    'message': f'记录不存在：ID={menu_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            db.session.delete(menu)
            db.session.commit()
            return {
                'message': '系统菜单删除成功',
                'id': menu_id
            }, 200
        except IntegrityError:
            db.session.rollback()
            return {
                'message': '无法删除：菜单被其他记录引用',
                'error_code': ERROR_CODES['INVALID_PARAM_KEY']
            }, 400
        except Exception as e:
            db.session.rollback()
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class SystemMenuListResource(Resource):
    @swag_from('docs/system_menus/list_system_menus.yml')
    def get(self):
        try:
            menus = SystemMenu.query.all()
            return {
                'message': '系统菜单列表获取成功',
                'data': [menu.to_dict() for menu in menus]
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class SystemMenuPageResource(Resource):
    @swag_from('docs/system_menus/page_system_menus.yml')
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
            pagination = SystemMenu.query.paginate(page=args['page'], per_page=args['page_size'], error_out=False)
            return {
                'message': '分页系统菜单获取成功',
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