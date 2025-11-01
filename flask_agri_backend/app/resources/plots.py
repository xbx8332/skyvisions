from flask_restful import Resource, reqparse
from flasgger import swag_from
from flask import jsonify
from ..models import Plot
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

class PlotResource(Resource):
    @swag_from('docs/plots/get_plot.yml')
    def get(self, plot_id):
        try:
            plot = Plot.query.get(plot_id)
            if not plot:
                return {
                    'message': f'记录不存在：ID={plot_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            return {
                'message': '地块获取成功',
                'data': plot.to_dict()
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class PlotCreateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help='参数不能为空：name', location='form')
    parser.add_argument('owner_id', type=int, required=False, location='form')
    parser.add_argument('geom', type=str, required=True, help='参数不能为空：geom', location='form')
    parser.add_argument('area', type=float, required=False, location='form')
    parser.add_argument('soil_type', type=str, required=False, location='form')
    parser.add_argument('crop_type', type=str, required=False, location='form')
    parser.add_argument('metadata', type=str, required=False, help='元数据需为JSON字符串', location='form')

    @swag_from('docs/plots/create_plot.yml')
    def post(self):
        try:
            args = self.parser.parse_args()
            metadata = json.loads(args['metadata']) if args['metadata'] else None
            plot = Plot(
                name=args['name'],
                owner_id=args['owner_id'],
                geom=args['geom'],
                area=args['area'],
                soil_type=args['soil_type'],
                crop_type=args['crop_type'],
                metadata=metadata
            )
            db.session.add(plot)
            db.session.commit()
            return {'message': '地块创建成功', 'id': plot.id}, 201
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

class PlotUpdateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=False, help='参数不能为空：name', location='form')
    parser.add_argument('owner_id', type=int, required=False, location='form')
    parser.add_argument('geom', type=str, required=False, help='参数不能为空：geom', location='form')
    parser.add_argument('area', type=float, required=False, location='form')
    parser.add_argument('soil_type', type=str, required=False, location='form')
    parser.add_argument('crop_type', type=str, required=False, location='form')
    parser.add_argument('metadata', type=str, required=False, help='元数据需为JSON字符串', location='form')

    @swag_from('docs/plots/update_plot.yml')
    def put(self, plot_id):
        try:
            args = self.parser.parse_args()
            plot = Plot.query.get(plot_id)
            if not plot:
                return {
                    'message': f'记录不存在：ID={plot_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            if args['name'] is not None:
                plot.name = args['name']
            if args['owner_id'] is not None:
                plot.owner_id = args['owner_id']
            if args['geom'] is not None:
                plot.geom = args['geom']
            if args['area'] is not None:
                plot.area = args['area']
            if args['soil_type'] is not None:
                plot.soil_type = args['soil_type']
            if args['crop_type'] is not None:
                plot.crop_type = args['crop_type']
            if args['metadata'] is not None:
                plot.metadata = json.loads(args['metadata']) if args['metadata'] else None
            db.session.commit()
            return {
                'message': '地块更新成功',
                'id': plot_id
            }, 200
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

class PlotDeleteResource(Resource):
    @swag_from('docs/plots/delete_plot.yml')
    def delete(self, plot_id):
        try:
            plot = Plot.query.get(plot_id)
            if not plot:
                return {
                    'message': f'记录不存在：ID={plot_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            db.session.delete(plot)
            db.session.commit()
            return {
                'message': '地块删除成功',
                'id': plot_id
            }, 200
        except Exception as e:
            db.session.rollback()
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class PlotListResource(Resource):
    @swag_from('docs/plots/list_plots.yml')
    def get(self):
        try:
            plots = Plot.query.all()
            return {
                'message': '地块列表获取成功',
                'data': [plot.to_dict() for plot in plots]
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class PlotPageResource(Resource):
    @swag_from('docs/plots/page_plots.yml')
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
            pagination = Plot.query.paginate(page=args['page'], per_page=args['page_size'], error_out=False)
            return {
                'message': '分页地块获取成功',
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