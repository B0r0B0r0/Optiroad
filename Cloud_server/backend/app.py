from flask import Flask
from flask_cors import CORS
from config.settings import Config
from middleware.csrf import setup_csrf_protection
from middleware.auth import setup_jwt
from routes.auth_routes import auth_bp
from routes.cities_routes import city_bp
from routes.mail_routes import mail_bp
from routes.rsu_routes import rsu_bp
from routes.user_routes import user_bp
from routes.id_card_routes import id_card_bp
from services.mail_service import setup_mail

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    setup_csrf_protection(app)
    # Setup CORS
    CORS(app, 
         origins=app.config['NGINX_URL'], 
         methods=["POST", "GET", "OPTIONS"], 
         allow_headers=["Authorization", "X-CSRF-Token"], 
         supports_credentials=True)
    
    # Setup services
    setup_mail(app)
    setup_jwt(app)
    
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(city_bp, url_prefix='/api/cities')
    app.register_blueprint(mail_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(id_card_bp, url_prefix='/id-cards')
    app.register_blueprint(rsu_bp, url_prefix='/rsu')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
