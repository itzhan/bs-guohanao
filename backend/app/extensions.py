"""
Flask 扩展实例化（延迟初始化）
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_redis import FlaskRedis

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
redis_client = FlaskRedis()


class MongoDB:
    """MongoDB 连接管理"""

    def __init__(self):
        self._client = None
        self._db = None

    def init_app(self, app):
        from pymongo import MongoClient
        self._client = MongoClient(app.config.get('MONGO_URI', 'mongodb://localhost:27017/'))
        self._db = self._client[app.config.get('MONGO_DB_NAME', 'music_recommend')]

    @property
    def client(self):
        return self._client

    @property
    def db(self):
        return self._db

    def get_collection(self, name):
        return self._db[name]


mongo = MongoDB()
