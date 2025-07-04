from flask import request, jsonify, session
import secrets

def setup_csrf_protection(app):
    """Setup CSRF protection middleware"""
    @app.before_request
    def check_csrf_token():
        if request.method in ["POST", "PUT", "DELETE"] and request.endpoint not in ['get_csrf_token', 'auth.login', 'auth.register', 'auth.logout', 'auth.refresh','rsu.register_camera', 'rsu.update_rsu']:
            csrf_token_from_session = session.get("csrf_token")
            csrf_token_from_request = request.headers.get("X-CSRF-Token")

            if not csrf_token_from_request or csrf_token_from_request != csrf_token_from_session:
                return jsonify({"error": "Invalid CSRF Token!"}), 400
