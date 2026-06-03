from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
import os

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    app = Flask(__name__,
                static_folder='static',
                template_folder='frontend/pages')
    
    app.config.from_object(config[config_name])
    
    # Extensions
    CORS(app)
    JWTManager(app)
    
    # Register Blueprints
    from backend.routes.auth_routes import auth_bp
    from backend.routes.mood_routes import mood_bp
    from backend.routes.journal_routes import journal_bp
    from backend.routes.ai_routes import ai_bp
    from backend.routes.report_routes import report_bp
    from backend.routes.emergency_routes import emergency_bp
    from backend.routes.admin_routes import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(mood_bp, url_prefix='/api/mood')
    app.register_blueprint(journal_bp, url_prefix='/api/journal')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(report_bp, url_prefix='/api/reports')
    app.register_blueprint(emergency_bp, url_prefix='/api/emergency')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
