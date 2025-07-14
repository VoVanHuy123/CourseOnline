from flask import Flask

from .extensions import db, migrate, login_manager, jwt
from .routes.auth.auth import auth_bp,user_register_docs
from .routes.course.course import course_bp,course_register_docs
from .admin.admin import init_admin
from .routes.learning.learning import learning_bp, learning_register_docs

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_cors import CORS
from config import Config

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)
    init_admin(app)
    Config.init_cloudinary()

    # Cho phép frontend React truy cập Flask
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

    from app import models

    # Đăng  blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(learning_bp)

    # Flask-APISpec config
    app.config.update({
        # 'APISPEC_SPEC': 'apispec.APISpec',
        'APISPEC_SPEC': APISpec(
            title='Course API',
            version='v1',
            openapi_version='2.0',
            plugins=[MarshmallowPlugin()],
        ),
        'APISPEC_SWAGGER_URL': '/swagger/',  # đường dẫn JSON schema
        'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # Giao diện Swagger UI
    })


    from flask_apispec.extension import FlaskApiSpec
    docs = FlaskApiSpec(app)

    # đăng ký route với docs
    user_register_docs(docs)
    course_register_docs(docs)
    learning_register_docs(docs)


    return app
