import logging
from logging.config import fileConfig

from flask import current_app

from alembic import context

from sqlalchemy import event
from geoalchemy2 import Geometry
from sqlalchemy.schema import Table

# Alembic 配置对象，读取 .ini 文件
config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

def get_engine():
    try:
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        return current_app.extensions['migrate'].db.engine

def get_engine_url():
    engine = get_engine()
    url = getattr(engine, "url", None)

    if url is None:
        raise RuntimeError("数据库引擎未初始化，无法获取 URL。")

    # SQLAlchemy 1.4+ 使用 str(url) 即可；老版本用 render_as_string
    try:
        # SQLAlchemy >=1.4 没有 render_as_string
        return str(url).replace('%', '%%')
    except Exception:
        return url.render_as_string(hide_password=False).replace('%', '%%')

# 配置数据库连接 URL 到 Alembic
config.set_main_option('sqlalchemy.url', get_engine_url())

# 获取 Flask-SQLAlchemy 的 db 对象
target_db = current_app.extensions['migrate'].db

# 获取 metadata，支持多数据库或默认
def get_metadata():
    if hasattr(target_db, 'metadatas'):
        return target_db.metadatas[None]
    return target_db.metadata

# geo 字段比较
def include_object(obj, name, type_, reflected, compare_to):
    return True  # 不要跳过 geom

# 避免反射 geometry 报错
@event.listens_for(Table, "column_reflect")
def geometry_column_reflect(inspector, table, column_info):
    if isinstance(column_info['type'], Geometry):
        # 若需要，你可以强制 srid 设置为 4326（MySQL 一般不强制要求）
        column_info['type'].srid = 4326

def run_migrations_offline():
    """离线模式迁移"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=get_metadata(),
        literal_binds=True,
        compare_type=True,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """在线模式迁移"""

    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    conf_args = current_app.extensions['migrate'].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            include_object=include_object,
            **conf_args
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
