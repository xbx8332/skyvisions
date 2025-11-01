from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api
from flask_jwt_extended import JWTManager
import redis
import os

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
api = Api()
jwt = JWTManager()
# 初始化 Redis 客户端，支持密码和 SSL
redis_client = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    decode_responses=True  # 自动解码字符串响应
    # ssl_cert_reqs=None if os.getenv("REDIS_URL", "").startswith("rediss://") else None,  # SSL 支持
    # ssl_ca_certs="/path/to/ca-cert.pem"
)