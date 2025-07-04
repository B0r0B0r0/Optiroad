from flask import Blueprint, request, jsonify, make_response, session
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from services.auth_service import AuthService
from utils.helpers import get_client_ip
from config.settings import Config
import secrets

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    source_ip = get_client_ip()

    if not username or not password or not source_ip:
        return jsonify({'message': 'Invalid request'}), 400
    
    is_valid, message = AuthService.verify_password(username, password, source_ip)
    if not is_valid:
        return jsonify({'message': message}), 401

    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)

    response = make_response(jsonify({'message': 'Login successful'}), 200)
    response.set_cookie('access_token', access_token, httponly=True, secure=Config.TEMP, 
                       samesite='Strict', max_age=Config.ACCESS_EXP_TIME)
    response.set_cookie('refresh_token', refresh_token, httponly=True, secure=Config.TEMP, 
                       samesite='Strict', max_age=Config.REFRESH_EXP_TIME)

    return response

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    key = data.get('key')
    source_ip = get_client_ip()

    if not username or not password or not email or not key or not source_ip:
        return jsonify({'message': 'Invalid request'}), 400

    success, message = AuthService.register_user(username, password, email, key, source_ip)
    
    if success:
        return jsonify({'message': 'Register successful'}), 200
    else:
        return jsonify({'message': message}), 401

@auth_bp.route("/logout", methods=["POST"])
@jwt_required(refresh=True)  
def logout():
    response = make_response(jsonify({"message": "Logged out"}), 200)
    response.set_cookie("access_token", "", expires=0, httponly=True, samesite="Strict")
    response.set_cookie("refresh_token", "", expires=0, httponly=True, samesite="Strict")
    response.set_cookie("session", "", expires=0, httponly=True, samesite="Strict")
    response.set_cookie("csrf_token", "", expires=0, httponly=True, samesite="Strict")
    return response

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True, locations=["cookies"])
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    response = make_response(jsonify({'message': 'Refresh successful'}), 200)
    response.set_cookie('access_token', access_token, httponly=True, secure=Config.TEMP, 
                       samesite='Strict', max_age=Config.ACCESS_EXP_TIME)
    return response

@auth_bp.route("/csrf-token", methods=["GET"])
def get_csrf_token():
    session["csrf_token"] = secrets.token_hex(32)
    response = jsonify({"msg": "CSRF token generated"})
    response.set_cookie("csrf_token", session["csrf_token"], httponly=False, secure=Config.TEMP, 
                       samesite="Strict", max_age=Config.ACCESS_EXP_TIME)
    return response
