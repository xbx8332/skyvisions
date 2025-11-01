from flask_restful import Resource, reqparse
from flasgger import swag_from
from ..models import FlightPath
from ..extensions import db
import json
from app.config import ERROR_CODES
from werkzeug.exceptions import BadRequest

def handle_request_parse_error(error):
    """自定义 reqparse 错误处理，返回标准化的中文错误响应"""
    # 提取错误信息
    message = str(error)
    # 默认消息为 help 参数的内容
    if hasattr(error, 'data') and error.data and 'message' in error.data:
        for param, msg in error.data['message'].items():
            return {
                'message': msg,
                'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']
            }, 400
    # 回退到通用消息
    param = message.split(':')[-1].strip() if ':' in message else 'unknown'
    return {
        'message': f'参数不能为空：{param}',
        'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']
    }, 400

class FlightPathResource(Resource):
    @swag_from('docs/flight_paths/get_path.yml')
    def get(self, flight_path_id):
        try:
            flight_path = FlightPath.query.get(flight_path_id)
            if not flight_path:
                return {
                    'message': f'记录不存在：ID={flight_path_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            return {
                'message': '飞行路径获取成功',
                'data': flight_path.to_dict()
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class FlightPathCreateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help='参数不能为空：name', location='form')
    parser.add_argument('description', type=str, required=False, location='form')
    parser.add_argument('geojson', type=str, required=False, location='form', help='GeoJSON必须为有效的JSON字符串')
    parser.add_argument('bbox', type=str, required=False, location='form')
    parser.add_argument('altitude', type=float, required=False, location='form')
    parser.add_argument('speed', type=float, required=False, location='form')
    parser.add_argument('task_type', type=str, required=False, location='form')
    parser.add_argument('metadata', type=str, required=False, location='form', help='元数据必须为有效的JSON字符串')
    parser.add_argument('tags', type=str, required=False, location='form', help='标签必须为有效的JSON字符串')

    @swag_from('docs/flight_paths/create_path.yml')
    def post(self):
        try:
            args = self.parser.parse_args()
            geojson = json.loads(args['geojson']) if args['geojson'] else None
            metadata = json.loads(args['metadata']) if args['metadata'] else None
            tags = json.loads(args['tags']) if args['tags'] else None

            flight_path = FlightPath(
                name=args['name'],
                description=args['description'],
                geojson=geojson,
                bbox=args['bbox'],
                altitude=args['altitude'],
                speed=args['speed'],
                task_type=args['task_type'],
                metadata=metadata,
                tags=tags
            )
            db.session.add(flight_path)
            db.session.commit()
            return {'message': '飞行路径创建成功', 'id': flight_path.id}, 201
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

class FlightPathUpdateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=False, location='form')
    parser.add_argument('description', type=str, required=False, location='form')
    parser.add_argument('geojson', type=str, required=False, location='form', help='GeoJSON必须为有效的JSON字符串')
    parser.add_argument('bbox', type=str, required=False, location='form')
    parser.add_argument('altitude', type=float, required=False, location='form')
    parser.add_argument('speed', type=float, required=False, location='form')
    parser.add_argument('task_type', type=str, required=False, location='form')
    parser.add_argument('metadata', type=str, required=False, location='form', help='元数据必须为有效的JSON字符串')
    parser.add_argument('tags', type=str, required=False, location='form', help='标签必须为有效的JSON字符串')

    @swag_from('docs/flight_paths/update_path.yml')
    def put(self, flight_path_id):
        try:
            args = self.parser.parse_args()
            flight_path = FlightPath.query.get(flight_path_id)
            if not flight_path:
                return {
                    'message': f'记录不存在：ID={flight_path_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            if args['name'] is not None:
                flight_path.name = args['name']
            if args['description'] is not None:
                flight_path.description = args['description']
            if args['geojson'] is not None:
                flight_path.geojson = json.loads(args['geojson']) if args['geojson'] else None
            if args['bbox'] is not None:
                flight_path.bbox = args['bbox']
            if args['altitude'] is not None:
                flight_path.altitude = args['altitude']
            if args['speed'] is not None:
                flight_path.speed = args['speed']
            if args['task_type'] is not None:
                flight_path.task_type = args['task_type']
            if args['metadata'] is not None:
                flight_path.metadata = json.loads(args['metadata']) if args['metadata'] else None
            if args['tags'] is not None:
                flight_path.tags = json.loads(args['tags']) if args['tags'] else None
            db.session.commit()
            return {
                'message': '飞行路径更新成功',
                'id': flight_path_id
            }, 200
        except json.JSONDecodeError as je:
            db.session.rollback()
            return {
                'message': f'JSON格式错误：{str(je)}',
                'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']
            }, 400
        except Exception as e:
            db.session.rollback()
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class FlightPathDeleteResource(Resource):
    @swag_from('docs/flight_paths/delete_path.yml')
    def delete(self, flight_path_id):
        try:
            flight_path = FlightPath.query.get(flight_path_id)
            if not flight_path:
                return {
                    'message': f'记录不存在：ID={flight_path_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            db.session.delete(flight_path)
            db.session.commit()
            return {
                'message': '飞行路径删除成功',
                'id': flight_path_id
            }, 200
        except Exception as e:
            db.session.rollback()
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class FlightPathListResource(Resource):
    @swag_from('docs/flight_paths/list_paths.yml')
    def get(self):
        try:
            flight_paths = FlightPath.query.all()
            return {
                'message': '飞行路径列表获取成功',
                'data': [flight_path.to_dict() for flight_path in flight_paths]
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class FlightPathPageResource(Resource):
    @swag_from('docs/flight_paths/page_paths.yml')
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
            pagination = FlightPath.query.paginate(page=args['page'], per_page=args['page_size'], error_out=False)
            return {
                'message': '分页飞行路径获取成功',
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