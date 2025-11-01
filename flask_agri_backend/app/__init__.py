import logging
import os
from flask import Flask, send_from_directory, jsonify
from flasgger import Swagger
from .config import Config
from .extensions import db, api, migrate, cors, jwt,redis_client
from .resources import register_resources
from dotenv import load_dotenv
from flask_jwt_extended import get_jwt
import traceback

load_dotenv()

# 配置日志
logging.getLogger('').handlers = []
logging.getLogger('flasgger').setLevel(logging.DEBUG)
logging.getLogger('yaml').setLevel(logging.DEBUG)
logging.getLogger('werkzeug').setLevel(logging.DEBUG)

def register_restful_routes(api, app, logger):
    """封装 Flask-RESTful 路由手动绑定到 Flask 的 app.url_map"""
    try:
        for resource, urls, kwargs in api.resources:
            for url in urls:
                endpoint = resource.__name__.lower()
                view_func = resource.as_view(endpoint)
                methods = [method.upper() for method in resource.methods] if hasattr(resource, 'methods') else ['GET', 'POST']
                app.add_url_rule(url, endpoint=endpoint, view_func=view_func, methods=methods)
                logger.debug(f"Manually added route: {endpoint} at {url} with methods {methods}")
    except Exception as e:
        logger.error(f"Failed to register routes: {str(e)}\n{traceback.format_exc()}")
        raise

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['DEBUG'] = True

    # 配置日志
    handler = logging.FileHandler('app.log', encoding='utf-8')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    if not root_logger.handlers:
        root_logger.addHandler(handler)

    for logger_name in ('flasgger', 'yaml', 'werkzeug', __name__):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = True

    logger = logging.getLogger(__name__)
    logger.info("Starting Flask application initialization")

    # 初始化扩展
    db.init_app(app)
    logger.info("Database initialized successfully")
    migrate.init_app(app, db)
    logger.info("Migrate initialized successfully")
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    logger.info("CORS initialized successfully")
    api.init_app(app)
    logger.info("Flask-RESTful API initialized successfully")
    jwt.init_app(app)
    logger.info("Flask-JWT-Extended initialized successfully")

    # 注册资源并手动绑定路由
    with app.app_context():
        try:
            register_resources(api)
            logger.info("API resources registered successfully")
            for resource, urls, kwargs in api.resources:
                logger.info(f"API registered: {resource.__name__} at {urls}")
            register_restful_routes(api, app, logger)
            logger.debug(f"Flask URL map after resource registration: {app.url_map}")
        except Exception as e:
            logger.error(f"Resource registration failed: {str(e)}\n{traceback.format_exc()}")
            raise

    # 初始化 Flasgger
    swagger_config = {
        "openapi": "3.0.3",
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec_1",
                "route": "/apispec_1.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
        "parse": True
    }
    swagger_template = {
        "openapi": "3.0.3",
        "info": {
            "title": "天视无人机平台",
            "description": "基于 Flask-RESTful 的无人机平台 API 文档",
            "version": "1.0"
        },
        "servers": [
            {"url": "http://localhost:5000", "description": "本地开发环境"}
        ]
    }
    try:
        swagger = Swagger(app, config=swagger_config, template=swagger_template)
        logger.info("Flasgger initialized successfully")
        with app.app_context():
            specs = swagger.get_apispecs()
            logger.debug(f"Swagger specs: {specs}")
            if not specs.get('paths'):
                logger.warning("No paths found in Swagger specs")
    except Exception as e:
        logger.error(f"Flasgger initialization failed: {str(e)}\n{traceback.format_exc()}")
        raise

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return  redis_client.get(f"blacklist:{jti}") is not None

    @jwt.unauthorized_loader
    def unauthorized_callback(error_string):
        return jsonify({"message": "请先登录"}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "请先登录"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return jsonify({"message": "请先登录"}), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "请先登录"}), 401

    with app.app_context():
        db.create_all()
        logger.info("Database tables created successfully")

    @app.route('/export_swagger')
    def export_swagger():
        return jsonify(swagger.get_apispecs())

    @app.route('/swagger-ui/<path:path>')
    def serve_swagger_ui(path):
        return send_from_directory('static/swagger-ui', path)

    with app.app_context():
        logger.info("\nFlask 应用已启动，路由如下：\n")
        for rule in app.url_map.iter_rules():
            methods = ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            logger.info(f"{rule.endpoint:>30} [{methods:<15}] {rule}")
        logger.info(f"\nSwagger UI: http://localhost:{app.config.get('PORT', 5000)}/apidocs\n")
        logger.debug(f"Flask URL map: {app.url_map}")

    logger.info("Flask application initialization completed")
    return app