import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-default-secret-key')  # Flask 应用密钥
    # 数据库连接
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:d9c567c57a14ade0@106.52.168.64:3306/sky_vision?charset=utf8mb4')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'e005885972875e2c0fbe3daf82b3db21dd045702404cf482c5527a4a1d4f1108')  # JWT 签名密钥
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15) # 令牌有效期1小时
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
    REDIS_URL = os.getenv("REDIS_URL", "redis://106.52.168.64:6379/0")
    PORT = 5000

# 自定义错误码
ERROR_CODES = {
    "MISSING_REQUIRED_PARAM": '4001',
    "INVALID_PARAM_FORMAT": '4002',
    "DATABASE_ERROR": '5001',
    "NOT_FOUND": '4041',
    "INVALID_CREDENTIALS": '2',  # 新增：无效凭证
    "USER_NOT_ACTIVE": '3'   # 新增：用户未激活
}