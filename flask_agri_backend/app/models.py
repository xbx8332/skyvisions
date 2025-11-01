from datetime import datetime
from sqlalchemy.dialects.mysql import JSON, ENUM
from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

def default_datetime():
    return db.func.current_timestamp()

def iso_format(dt):
    return dt.isoformat() if dt else None

class BaseModel(db.Model):
    __abstract__ = True

    def to_dict(self):
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat() if value else None
            elif column.name in ('metadata', 'tags', 'geojson', 'stats', 'style') and value is not None:
                result[column.name] = value  # JSON 兼容的字段直接返回
            else:
                result[column.name] = value
        return result

class Imagery(BaseModel):
    __tablename__ = 'imagery'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    description = db.Column(db.Text)
    file_path = db.Column(db.Text)
    geom = db.Column(db.Text, comment='原 GEOMETRY，影像覆盖范围')
    srid = db.Column(db.Integer)
    red_band_index = db.Column(db.Integer)
    nir_band_index = db.Column(db.Integer)
    metadata_info = db.Column(JSON)
    status = db.Column(ENUM('active', 'deleted'))
    capture_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=default_datetime())
    updated_at = db.Column(db.DateTime, server_default=default_datetime(), server_onupdate=default_datetime())
    tags = db.Column(JSON)

class FlightPath(BaseModel):
    __tablename__ = 'flight_paths'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    description = db.Column(db.Text)
    geojson = db.Column(JSON)
    bbox = db.Column(db.Text, comment='原 GEOMETRY，航线范围')
    altitude = db.Column(db.Float)
    speed = db.Column(db.Float)
    task_type = db.Column(db.String(64))
    metadata_info = db.Column(JSON)
    created_at = db.Column(db.DateTime, server_default=default_datetime())
    updated_at = db.Column(db.DateTime, server_default=default_datetime(), server_onupdate=default_datetime())
    tags = db.Column(JSON)

class Task(BaseModel):
    __tablename__ = 'tasks'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    description = db.Column(db.Text)
    type = db.Column(ENUM('mapping', 'spraying'))
    field_id = db.Column(db.BigInteger)
    path_id = db.Column(db.BigInteger)
    status = db.Column(ENUM('pending', 'running', 'done'))
    volume = db.Column(db.Float)
    schedule_at = db.Column(db.DateTime)
    metadata_info = db.Column(JSON)
    created_at = db.Column(db.DateTime, server_default=default_datetime())
    updated_at = db.Column(db.DateTime, server_default=default_datetime(), server_onupdate=default_datetime())

class AnalysisResult(BaseModel):
    __tablename__ = 'analysis_results'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    description = db.Column(db.Text)
    type = db.Column(db.String(64))
    result_path = db.Column(db.Text)
    field_id = db.Column(db.BigInteger)
    imagery_id = db.Column(db.BigInteger)
    bbox = db.Column(db.Text, comment='原 GEOMETRY，分析区域范围')
    stats = db.Column(JSON)
    style = db.Column(JSON)
    created_at = db.Column(db.DateTime, server_default=default_datetime())
    updated_at = db.Column(db.DateTime, server_default=default_datetime(), server_onupdate=default_datetime())

class MapObject3D(BaseModel):
    __tablename__ = 'map_objects_3d'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    type = db.Column(db.String(64))
    style = db.Column(JSON)
    geom = db.Column(db.Text, comment='原 GEOMETRY，空间范围')
    related_id = db.Column(db.BigInteger)
    metadata_info = db.Column(JSON)
    created_at = db.Column(db.DateTime, server_default=default_datetime())
    updated_at = db.Column(db.DateTime, server_default=default_datetime(), server_onupdate=default_datetime())

class Plot(BaseModel):
    __tablename__ = 'plots'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    owner_id = db.Column(db.BigInteger)
    geom = db.Column(db.Text, comment='原 GEOMETRY，地块边界')
    area = db.Column(db.Float)
    soil_type = db.Column(db.String(128))
    crop_type = db.Column(db.String(128))
    metadata_info = db.Column(JSON)
    created_at = db.Column(db.DateTime, server_default=default_datetime())
    updated_at = db.Column(db.DateTime, server_default=default_datetime(), server_onupdate=default_datetime())

class SystemMenu(BaseModel):
    __tablename__ = 'system_menus'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    parent_id = db.Column(db.BigInteger)
    name = db.Column(db.String(255))
    path = db.Column(db.String(255))
    icon = db.Column(db.String(64))
    order_num = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=default_datetime())
    updated_at = db.Column(db.DateTime, server_default=default_datetime(), server_onupdate=default_datetime())

class SystemRole(BaseModel):
    __tablename__ = 'system_roles'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=default_datetime())
    updated_at = db.Column(db.DateTime, server_default=default_datetime(), server_onupdate=default_datetime())

class SystemUser(BaseModel):
    __tablename__ = 'system_users'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    status = db.Column(ENUM('active', 'disabled'), default='active')
    created_at = db.Column(db.DateTime, server_default=default_datetime())
    updated_at = db.Column(db.DateTime, server_default=default_datetime(), server_onupdate=default_datetime())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class SystemPermission(BaseModel):
    __tablename__ = 'system_permissions'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    code = db.Column(db.String(64), unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=default_datetime())
    updated_at = db.Column(db.DateTime, server_default=default_datetime(), server_onupdate=default_datetime())

class RolePermission(BaseModel):
    __tablename__ = 'role_permissions'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    role_id = db.Column(db.BigInteger)
    permission_id = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime, server_default=default_datetime())
    updated_at = db.Column(db.DateTime, server_default=default_datetime(), server_onupdate=default_datetime())

class UserRole(BaseModel):
    __tablename__ = 'user_roles'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger)
    role_id = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime, server_default=default_datetime())
    updated_at = db.Column(db.DateTime, server_default=default_datetime(), server_onupdate=default_datetime())
