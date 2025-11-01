from flask_restful import Resource, reqparse
from flasgger import swag_from
from flask import jsonify
from ..models import Task
from ..extensions import db
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import IntegrityError
from app.config import ERROR_CODES
import json
from datetime import datetime

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

def parse_datetime(value):
    """解析日期时间字符串"""
    if value:
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('无效的日期时间格式')
    return None

class TaskResource(Resource):
    @swag_from('docs/tasks/get_task.yml')
    def get(self, task_id):
        try:
            task = Task.query.get(task_id)
            if not task:
                return {
                    'message': f'记录不存在：ID={task_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            return {
                'message': '任务获取成功',
                'data': task.to_dict()
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class TaskCreateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help='参数不能为空：name', location='form')
    parser.add_argument('description', type=str, required=False, location='form')
    parser.add_argument('type', type=str, required=True, choices=('mapping', 'spraying'), help='无效的任务类型', location='form')
    parser.add_argument('field_id', type=int, required=True, help='参数不能为空：field_id', location='form')
    parser.add_argument('path_id', type=int, required=False, location='form')
    parser.add_argument('status', type=str, required=True, choices=('pending', 'running', 'done'), help='无效的状态', location='form')
    parser.add_argument('volume', type=float, required=False, location='form')
    parser.add_argument('schedule_at', type=str, required=False, location='form')
    parser.add_argument('metadata', type=str, required=False, help='元数据需为 JSON 字符串', location='form')

    @swag_from('docs/tasks/create_task.yml')
    def post(self):
        try:
            args = self.parser.parse_args()
            metadata = json.loads(args['metadata']) if args['metadata'] else None
            schedule_at = parse_datetime(args['schedule_at'])
            task = Task(
                name=args['name'],
                description=args['description'],
                type=args['type'],
                field_id=args['field_id'],
                path_id=args['path_id'],
                status=args['status'],
                volume=args['volume'],
                schedule_at=schedule_at,
                metadata=metadata
            )
            db.session.add(task)
            db.session.commit()
            return {'message': '任务创建成功', 'id': task.id}, 201
        except json.JSONDecodeError as je:
            db.session.rollback()
            return {
                'message': f'JSON 格式错误：{str(je)}',
                'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']
            }, 400
        except ValueError as ve:
            db.session.rollback()
            return {
                'message': f'参数错误：{str(ve)}',
                'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']
            }, 400
        except IntegrityError:
            db.session.rollback()
            return {
                'message': '记录已存在：任务数据重复',
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

class TaskUpdateResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=False, help='参数不能为空：name', location='form')
    parser.add_argument('description', type=str, required=False, location='form')
    parser.add_argument('type', type=str, required=False, choices=('mapping', 'spraying'), help='无效的任务类型', location='form')
    parser.add_argument('field_id', type=int, required=False, help='参数不能为空：field_id', location='form')
    parser.add_argument('path_id', type=int, required=False, location='form')
    parser.add_argument('status', type=str, required=False, choices=('pending', 'running', 'done'), help='无效的状态', location='form')
    parser.add_argument('volume', type=float, required=False, location='form')
    parser.add_argument('schedule_at', type=str, required=False, location='form')
    parser.add_argument('metadata', type=str, required=False, help='元数据需为 JSON 字符串', location='form')

    @swag_from('docs/tasks/update_task.yml')
    def put(self, task_id):
        try:
            args = self.parser.parse_args()
            task = Task.query.get(task_id)
            if not task:
                return {
                    'message': f'记录不存在：ID={task_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            if args['name'] is not None:
                task.name = args['name']
            if args['description'] is not None:
                task.description = args['description']
            if args['type'] is not None:
                task.type = args['type']
            if args['field_id'] is not None:
                task.field_id = args['field_id']
            if args['path_id'] is not None:
                task.path_id = args['path_id']
            if args['status'] is not None:
                task.status = args['status']
            if args['volume'] is not None:
                task.volume = args['volume']
            if args['schedule_at'] is not None:
                task.schedule_at = parse_datetime(args['schedule_at'])
            if args['metadata'] is not None:
                task.metadata = json.loads(args['metadata']) if args['metadata'] else None
            db.session.commit()
            return {
                'message': '任务更新成功',
                'id': task_id
            }, 200
        except json.JSONDecodeError as je:
            db.session.rollback()
            return {
                'message': f'JSON 格式错误：{str(je)}',
                'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']
            }, 400
        except ValueError as ve:
            db.session.rollback()
            return {
                'message': f'参数错误：{str(ve)}',
                'error_code': ERROR_CODES['INVALID_PARAM_FORMAT']
            }, 400
        except IntegrityError:
            db.session.rollback()
            return {
                'message': '记录已存在：任务数据重复',
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

class TaskDeleteResource(Resource):
    @swag_from('docs/tasks/delete_task.yml')
    def delete(self, task_id):
        try:
            task = Task.query.get(task_id)
            if not task:
                return {
                    'message': f'记录不存在：ID={task_id}',
                    'error_code': ERROR_CODES['NOT_FOUND']
                }, 404
            db.session.delete(task)
            db.session.commit()
            return {
                'message': '任务删除成功',
                'id': task_id
            }, 200
        except IntegrityError:
            db.session.rollback()
            return {
                'message': '无法删除：任务被其他记录引用',
                'error_code': ERROR_CODES['INVALID_PARAM_KEY']
            }, 400
        except Exception as e:
            db.session.rollback()
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class TaskListResource(Resource):
    @swag_from('docs/tasks/list_tasks.yml')
    def get(self):
        try:
            tasks = Task.query.all()
            return {
                'message': '任务列表获取成功',
                'data': [task.to_dict() for task in tasks]
            }, 200
        except Exception as e:
            return {
                'message': f'数据库错误：{str(e)}',
                'error_code': ERROR_CODES['DATABASE_ERROR']
            }, 500

class TaskPageResource(Resource):
    @swag_from('docs/tasks/page_tasks.yml')
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
            pagination = Task.query.paginate(page=args['page'], per_page=args['page_size'], error_out=False)
            return {
                'message': '分页任务获取成功',
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