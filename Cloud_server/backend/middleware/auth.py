from flask_jwt_extended import JWTManager

def setup_jwt(app):
    """Setup JWT manager"""
    jwt = JWTManager(app)
    return jwt
