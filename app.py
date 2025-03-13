"""
Application factory module.
"""
import os
from flask import Flask, render_template
from flask_cors import CORS

from src.extensions import db, migrate, login_manager
from src.routes import auth_bp, survey_bp, main_bp


def create_app(config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                template_folder='src/templates',
                static_folder='src/static')
    
    # Configure the app
    app_settings = os.getenv('APP_SETTINGS', 'config.DevelopmentConfig')
    app.config.from_object(app_settings)
    
    # Allow for override of config
    if config:
        app.config.update(config)
    
    # Ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Set up database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 
        f"sqlite:///{os.path.join(app.instance_path, 'customer_feedback.db')}"
    )
    
    # Initialize extensions
    initialize_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Enable CORS
    CORS(app)
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500
    
    return app


def initialize_extensions(app):
    """Initialize Flask extensions."""
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Initialize Flask-Migrate
    migrate.init_app(app, db)
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(auth_bp)
    app.register_blueprint(survey_bp)
    app.register_blueprint(main_bp)


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)