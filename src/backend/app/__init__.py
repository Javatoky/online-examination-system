from flask import Flask, jsonify

from .api import register_blueprints
from .cli import register_cli
from .config import Config
from .extensions import cors, db, jwt


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    register_blueprints(app)
    register_cli(app)
    _register_error_handlers(app)
    _register_jwt_handlers(app)
    return app


def _register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"code": 404, "msg": "资源不存在", "data": None}), 404

    @app.errorhandler(405)
    def method_not_allowed(_):
        return jsonify({"code": 405, "msg": "请求方法不被允许", "data": None}), 405

    @app.errorhandler(500)
    def server_error(_):
        return jsonify({"code": 500, "msg": "服务器内部错误", "data": None}), 500


def _register_jwt_handlers(app):
    @jwt.unauthorized_loader
    def missing_token(_):
        return jsonify({"code": 401, "msg": "未登录或登录已过期", "data": None}), 401

    @jwt.invalid_token_loader
    def invalid_token(_):
        return jsonify({"code": 401, "msg": "身份凭证无效", "data": None}), 401

    @jwt.expired_token_loader
    def expired_token(_, __):
        return jsonify({"code": 401, "msg": "登录已过期，请重新登录", "data": None}), 401
