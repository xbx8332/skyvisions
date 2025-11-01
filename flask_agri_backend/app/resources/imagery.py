from flask_restful import Resource, reqparse
from flasgger import swag_from
from ..models import Imagery
from ..extensions import db
from datetime import datetime
import json
from app.config import ERROR_CODES
from werkzeug.exceptions import BadRequest

def handle_request_parse_error(error):
    """自定义 reqparse 错误处理，返回标准化的中文错误响应"""
    message = str(error)
    if hasattr(error, 'data') and error.data and 'message' in error.data:
        for param, msg in error.data['message'].items():
            return {'message': msg, 'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']}, 400
    param = message.split(':')[-1].strip() if ':' in message else 'unknown'
    return {'message': f'参数不能为空：{param}', 'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']}, 400

class ImageryResource(Resource):
    @swag_from('docs/imagery/get_imagery.yml')
    def get(self, imagery_id):
        try:
            imagery = Imagery.query.get(imagery_id)
            if not imagery:
                return {
                    'message': f'记录不存在：ID={imagery_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            return {
                'message': '影像获取成功',
                'data': imagery.to_dict()
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class ImageryCreateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help='参数不能为空：name', location='form')
    parser.add_argument('description', type=str, required=False, location='form')
    parser.add_argument('file_path', type=str, required=True, help='参数不能为空：file_path', location='form')
    parser.add_argument('geom', type=str, required=False, location='form')
    parser.add_argument('srid', type=int, required=False, location='form')
    parser.add_argument('red_band_index', type=int, required=False, location='form')
    parser.add_argument('nir_band_index', type=int, required=False, location='form')
    parser.add_argument('metadata', type=str, required=False, location='form', help='元数据需为JSON字符串')
    parser.add_argument('status', type=str, required=False, choices=('active', 'deleted'), help="无效的状态值：必须为 'active' 或 'deleted'", location='form')
    parser.add_argument('capture_time', type=str, required=False, location='form', help='拍摄时间需为ISO格式')
    parser.add_argument('tags', type=str, required=False, location='form', help='标签需为JSON字符串')

    @swag_from('docs/imagery/create_imagery.yml')
    def post(self):
        try:
            args = self.parser.parse_args()
            capture_time = None
            if args['capture_time']:
                try:
                    capture_time = datetime.fromisoformat(args['capture_time'].replace('Z', '+00:00'))
                except ValueError as ve:
                    return {
                        'message': f'无效的时间格式：{str(ve)}',
                        'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']
                    }, 400
            metadata = json.loads(args['metadata']) if args['metadata'] else None
            tags = json.loads(args['tags']) if args['tags'] else None

            imagery = Imagery(
                name=args['name'],
                description=args['description'],
                file_path=args['file_path'],
                geom=args['geom'],
                srid=args['srid'],
                red_band_index=args['red_band_index'],
                nir_band_index=args['nir_band_index'],
                metadata=metadata,
                status= 'active',
                capture_time=capture_time,
                tags=tags
            )
            db.session.add(imagery)
            db.session.commit()
            return {'message': '影像创建成功', 'id': imagery.id}, 201
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

class ImageryUpdateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=False, location='form')
    parser.add_argument('description', type=str, required=False, location='form')
    parser.add_argument('file_path', type=str, required=False, location='form')
    parser.add_argument('geom', type=str, required=False, location='form')
    parser.add_argument('srid', type=int, required=False, location='form')
    parser.add_argument('red_band_index', type=int, required=False, location='form')
    parser.add_argument('nir_band_index', type=int, required=False, location='form')
    parser.add_argument('metadata', type=str, required=False, location='form', help='元数据需为JSON字符串')
    parser.add_argument('status', type=str, required=False, choices=('active', 'deleted'), help="无效的状态值：必须为 'active' 或 'deleted'", location='form')
    parser.add_argument('capture_time', type=str, required=False, location='form', help='拍摄时间需为ISO格式')
    parser.add_argument('tags', type=str, required=False, location='form', help='标签需为JSON字符串')

    @swag_from('docs/imagery/update_imagery.yml')
    def put(self, imagery_id):
        try:
            args = self.parser.parse_args()
            imagery = Imagery.query.get(imagery_id)
            if not imagery:
                return {
                    'message': f'记录不存在：ID={imagery_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            if args['capture_time'] is not None:
                try:
                    imagery.capture_time = datetime.fromisoformat(args['capture_time'].replace('Z', '+00:00')) if args['capture_time'] else None
                except ValueError as ve:
                    return {
                        'message': f'无效的时间格式：{str(ve)}',
                        'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']
                    }, 400
            if args['metadata'] is not None:
                imagery.metadata = json.loads(args['metadata']) if args['metadata'] else None
            if args['tags'] is not None:
                imagery.tags = json.loads(args['tags']) if args['tags'] else None
            if args['name'] is not None:
                imagery.name = args['name']
            if args['description'] is not None:
                imagery.description = args['description']
            if args['file_path'] is not None:
                imagery.file_path = args['file_path']
            if args['geom'] is not None:
                imagery.geom = args['geom']
            if args['srid'] is not None:
                imagery.srid = args['srid']
            if args['red_band_index'] is not None:
                imagery.red_band_index = args['red_band_index']
            if args['nir_band_index'] is not None:
                imagery.nir_band_index = args['nir_band_index']
            if args['status'] is not None:
                imagery.status = args['status']
            db.session.commit()
            return {
                'message': '影像更新成功',
                'id': imagery_id
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

class ImageryDeleteResource(Resource):
    @swag_from('docs/imagery/delete_imagery.yml')
    def delete(self, imagery_id):
        try:
            imagery = Imagery.query.get(imagery_id)
            if not imagery:
                return {
                    'message': f'记录不存在：ID={imagery_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            db.session.delete(imagery)
            db.session.commit()
            return {
                'message': '影像删除成功',
                'id': imagery_id
            }, 200
        except Exception as e:
            db.session.rollback()
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class ImageryListResource(Resource):
    @swag_from('docs/imagery/list_imagery.yml')
    def get(self):
        try:
            imageries = Imagery.query.all()
            return {
                'message': '影像列表获取成功',
                'data': [imagery.to_dict() for imagery in imageries]
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class ImageryPageResource(Resource):
    @swag_from('docs/imagery/page_imagery.yml')
    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int, default=1, location='args', help='页码必须为正整数')
            parser.add_argument('page_size', type=int, default=200, location='args', help='页面大小必须为正整数')
            args = self.parser.parse_args()
            if args['page'] < 1 or args['page_size'] < 1:
                return {
                    'message': '页码和页面大小必须为正整数',
                    'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']
                }, 400
            pagination = Imagery.query.paginate(page=args['page'], per_page=args['page_size'], error_out=False)
            return {
                'message': '分页影像获取成功',
                'data': [imagery.to_dict() for imagery in pagination.items],
                'total': pagination.total,
                'page': args['page'],
                'page_size': args['page_size']
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500