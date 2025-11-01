from flask_restful import Resource, reqparse
from flasgger import swag_from
from flask import jsonify
from ..models import MapObject3D
from ..extensions import db
from werkzeug.exceptions import BadRequest
import json
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

class MapObject3DResource(Resource):
    @swag_from('docs/map_objects_3d/get_map_object_3d.yml')
    def get(self, object_id):
        try:
            map_object = MapObject3D.query.get(object_id)
            if not map_object:
                return {
                    'message': f'记录不存在：ID={object_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            return {
                'message': '获取3D地图对象成功',
                'data': map_object.to_dict()
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class MapObject3DCreateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help='参数不能为空：name', location='form')
    parser.add_argument('type', type=str, required=True, help='参数不能为空：type', location='form')
    parser.add_argument('style', type=str, required=False, help='样式需为JSON字符串', location='form')
    parser.add_argument('geom', type=str, required=False, location='form')
    parser.add_argument('related_id', type=int, required=False, location='form')
    parser.add_argument('metadata', type=str, required=False, help='元数据需为JSON字符串', location='form')

    @swag_from('docs/map_objects_3d/create_map_object_3d.yml')
    def post(self):
        try:
            args = self.parser.parse_args()
            style = json.loads(args['style']) if args['style'] else None
            metadata = json.loads(args['metadata']) if args['metadata'] else None
            map_object = MapObject3D(
                name=args['name'],
                type=args['type'],
                style=style,
                geom=args['geom'],
                related_id=args['related_id'],
                metadata=metadata
            )
            db.session.add(map_object)
            db.session.commit()
            return {'message': '3D地图对象创建成功', 'id': map_object.id}, 201
        except json.JSONDecodeError as je:
            db.session.rollback()
            return {
                'message': f'JSON格式错误：{str(je)}',
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

class MapObject3DUpdateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=False, help='参数不能为空：name', location='form')
    parser.add_argument('type', type=str, required=False, help='参数不能为空：type', location='form')
    parser.add_argument('style', type=str, required=False, help='样式需为JSON字符串', location='form')
    parser.add_argument('geom', type=str, required=False, location='form')
    parser.add_argument('related_id', type=int, required=False, location='form')
    parser.add_argument('metadata', type=str, required=False, help='元数据需为JSON字符串', location='form')

    @swag_from('docs/map_objects_3d/update_map_object_3d.yml')
    def put(self, object_id):
        try:
            args = self.parser.parse_args()
            map_object = MapObject3D.query.get(object_id)
            if not map_object:
                return {
                    'message': f'记录不存在：ID={object_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            if args['name'] is not None:
                map_object.name = args['name']
            if args['type'] is not None:
                map_object.type = args['type']
            if args['style'] is not None:
                map_object.style = json.loads(args['style']) if args['style'] else None
            if args['geom'] is not None:
                map_object.geom = args['geom']
            if args['related_id'] is not None:
                map_object.related_id = args['related_id']
            if args['metadata'] is not None:
                map_object.metadata = json.loads(args['metadata']) if args['metadata'] else None
            db.session.commit()
            return {
                'message': '3D地图对象更新成功',
                'id': object_id
            }, 200
        except json.JSONDecodeError as je:
            db.session.rollback()
            return {
                'message': f'JSON格式错误：{str(je)}',
                'error_code': ERROR_CODES['INVALID_PARAM']
            }, 400
        except BadRequest as e:
            return handle_request_parse_error(e)
        except Exception as e:
            db.session.rollback()
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class MapObject3DDeleteResource(Resource):
    @swag_from('docs/map_objects_3d/delete_map_object_3d.yml')
    def delete(self, object_id):
        try:
            map_object = MapObject3D.query.get(object_id)
            if not map_object:
                return {
                    'message': f'记录不存在：ID={object_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            db.session.delete(map_object)
            db.session.commit()
            return {
                'message': '3D地图对象删除成功',
                'id': object_id
            }, 200
        except Exception as e:
            db.session.rollback()
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class MapObject3DListResource(Resource):
    @swag_from('docs/map_objects_3d/list_map_objects_3d.yml')
    def get(self):
        try:
            map_objects = MapObject3D.query.all()
            return {
                'message': '3D地图对象列表获取成功',
                'data': [map_object.to_dict() for map_object in map_objects]
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['ERROR']
            }, 500

class MapObject3DPageResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int, default=1, location='args', help='页码必须为正整数')
    parser.add_argument('page_size', type=int, default=200, location='args', help='页面大小必须为正整数')

    @swag_from('docs/map_objects_3d/page_map_objects_3d.yml')
    def get(self):
        try:
            args = self.parser.parse_args()
            if args['page'] < 1 or args['page_size'] < 1:
                return {
                    'message': '页码和页面大小必须为正整数',
                    'error_code': ERROR_CODES['INVALID_PAGE']
                }, 400
            pagination = MapObject3D.query.paginate(page=args['page'], per_page=args['page_size'], error_out=False)
            return {
                'message': '分页3D地图对象获取成功',
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