from flask_restful import Resource, reqparse
from flasgger import swag_from
from ..models import AnalysisResult
from ..extensions import db
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

class AnalysisResultResource(Resource):
    @swag_from('docs/analysis_results/get_result.yml')
    def get(self, result_id):
        try:
            result = AnalysisResult.query.get(result_id)
            if not result:
                return {
                    'message': f'记录不存在：ID={result_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            return {
                'message': '分析结果获取成功',
                'data': result.to_dict()
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class AnalysisResultCreateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help='参数不能为空：name', location='form')
    parser.add_argument('description', type=str, required=False, location='form')
    parser.add_argument('type', type=str, required=False, location='form')
    parser.add_argument('result_path', type=str, required=True, help='参数不能为空：result_path', location='form')
    parser.add_argument('field_id', type=int, required=False, location='form')
    parser.add_argument('imagery_id', type=int, required=False, location='form')
    parser.add_argument('bbox', type=str, required=False, location='form')
    parser.add_argument('stats', type=str, required=False, location='form', help='统计数据需为JSON字符串')
    parser.add_argument('style', type=str, required=False, location='form', help='样式需为JSON字符串')

    @swag_from('docs/analysis_results/create_result.yml')
    def post(self):
        try:
            args = self.parser.parse_args()
            stats = json.loads(args['stats']) if args['stats'] else None
            style = json.loads(args['style']) if args['style'] else None

            result = AnalysisResult(
                name=args['name'],
                description=args['description'],
                type=args['type'],
                result_path=args['result_path'],
                field_id=args['field_id'],
                imagery_id=args['imagery_id'],
                bbox=args['bbox'],
                stats=stats,
                style=style
            )
            db.session.add(result)
            db.session.commit()
            return {'message': '分析结果创建成功', 'id': result.id}, 201
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

class AnalysisResultUpdateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=False, location='form')
    parser.add_argument('description', type=str, required=False, location='form')
    parser.add_argument('type', type=str, required=False, location='form')
    parser.add_argument('result_path', type=str, required=False, location='form')
    parser.add_argument('field_id', type=int, required=False, location='form')
    parser.add_argument('imagery_id', type=int, required=False, location='form')
    parser.add_argument('bbox', type=str, required=False, location='form')
    parser.add_argument('stats', type=str, required=False, location='form', help='统计数据需为JSON字符串')
    parser.add_argument('style', type=str, required=False, location='form', help='样式需为JSON字符串')

    @swag_from('docs/analysis_results/update_result.yml')
    def put(self, result_id):
        try:
            args = self.parser.parse_args()
            result = AnalysisResult.query.get(result_id)
            if not result:
                return {
                    'message': f'记录不存在：ID={result_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            if args['name'] is not None:
                result.name = args['name']
            if args['description'] is not None:
                result.description = args['description']
            if args['type'] is not None:
                result.type = args['type']
            if args['result_path'] is not None:
                result.result_path = args['result_path']
            if args['field_id'] is not None:
                result.field_id = args['field_id']
            if args['imagery_id'] is not None:
                result.imagery_id = args['imagery_id']
            if args['bbox'] is not None:
                result.bbox = args['bbox']
            if args['stats'] is not None:
                result.stats = json.loads(args['stats']) if args['stats'] else None
            if args['style'] is not None:
                result.style = json.loads(args['style']) if args['style'] else None
            db.session.commit()
            return {
                'message': '分析结果更新成功',
                'id': result_id
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

class AnalysisResultDeleteResource(Resource):
    @swag_from('docs/analysis_results/delete_result.yml')
    def delete(self, result_id):
        try:
            result = AnalysisResult.query.get(result_id)
            if not result:
                return {
                    'message': f'记录不存在：ID={result_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            db.session.delete(result)
            db.session.commit()
            return {
                'message': '分析结果删除成功',
                'id': result_id
            }, 200
        except Exception as e:
            db.session.rollback()
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class AnalysisResultListResource(Resource):
    @swag_from('docs/analysis_results/list_results.yml')
    def get(self):
        try:
            results = AnalysisResult.query.all()
            return {
                'message': '分析结果列表获取成功',
                'data': [result.to_dict() for result in results]
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class AnalysisResultPageResource(Resource):
    @swag_from('docs/analysis_results/page_results.yml')
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
            pagination = AnalysisResult.query.paginate(page=args['page'], per_page=args['page_size'], error_out=False)
            return {
                'message': '分页分析结果获取成功',
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