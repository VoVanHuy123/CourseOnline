from flask import Flask
from .extensions import db, migrate, login_manager
# from .routes import main_bp, auth_bp

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app import models

    # Register blueprints
    # app.register_blueprint(main_bp)
    # app.register_blueprint(auth_bp)

    return app
