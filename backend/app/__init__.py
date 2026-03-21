"""
基于大数据的音乐推荐与数据分析系统 - Flask 应用工厂
"""
from flask import Flask
from flask_cors import CORS

from app.extensions import db, migrate, jwt, redis_client, mongo
from app.config import Config


def create_app(config_class=Config):
    """Flask 应用工厂"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, supports_credentials=True)

    # 初始化 Redis
    redis_client.init_app(app)

    # 初始化 MongoDB
    mongo.init_app(app)

    # 注册蓝图
    _register_blueprints(app)

    # 注册全局错误处理
    _register_error_handlers(app)

    # 注册 JWT 回调
    _register_jwt_callbacks(app)

    # 创建数据库表
    with app.app_context():
        from app import models  # noqa: F401
        db.create_all()

    return app


def _register_blueprints(app):
    """注册所有蓝图"""
    from app.api.auth import auth_bp
    from app.api.user import user_bp
    from app.api.song import song_bp
    from app.api.interact import interact_bp
    from app.api.recommend import recommend_bp
    from app.api.stats import stats_bp
    from app.api.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(song_bp, url_prefix='/api/songs')
    app.register_blueprint(interact_bp, url_prefix='/api/interact')
    app.register_blueprint(recommend_bp, url_prefix='/api/recommend')
    app.register_blueprint(stats_bp, url_prefix='/api/stats')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')


def _register_error_handlers(app):
    """注册全局错误处理"""
    from app.utils.response import error_response

    @app.errorhandler(400)
    def bad_request(e):
        return error_response(400, str(e.description) if hasattr(e, 'description') else '请求参数错误')

    @app.errorhandler(401)
    def unauthorized(e):
        return error_response(401, '未授权，请先登录')

    @app.errorhandler(403)
    def forbidden(e):
        return error_response(403, '权限不足')

    @app.errorhandler(404)
    def not_found(e):
        return error_response(404, '资源不存在')

    @app.errorhandler(500)
    def internal_error(e):
        return error_response(500, '服务器内部错误')


def _register_jwt_callbacks(app):
    """注册 JWT 相关回调"""
    from app.utils.response import error_response

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return error_response(401, 'Token 已过期，请重新登录')

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return error_response(401, '无效的 Token')

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return error_response(401, '缺少认证 Token')
