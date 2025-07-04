from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from services.auth_service import AuthService
from services.user_service import UserService
from utils.helpers import get_client_ip

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    username = get_jwt_identity()
    source_ip = get_client_ip()
    
    profile, message = AuthService.get_user_profile(username, source_ip)
    
    if not profile:
        return jsonify({'message': message}), 404 if message == "User not found" else 500

    return jsonify({
        'username': profile['username'],
        'role': profile['role']
    }), 200

@user_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    data = request.get_json()
    username = get_jwt_identity()
    source_ip = get_client_ip()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'message': 'Missing required fields'}), 400

    success, message = AuthService.update_password(username, old_password, new_password, source_ip)
    
    if success:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'message': message}), 400 if "Incorrect" in message else 500

@user_bp.route("/add-user", methods=["POST"])
def add_user():
    success, message = UserService.add_user_with_id_cards(request.form, request.files, get_client_ip())
    return jsonify({"message": message}), 200 if success else 400

@user_bp.route("/pending-users", methods=["GET"])
@jwt_required()
def fetch_pending_users():
    username = get_jwt_identity()
    source_ip = get_client_ip()
    
    data, msg = UserService.get_pending_users(username, source_ip)
    if data is None:
        return jsonify({"message": msg}), 403 if "Invalid" in msg else 500
    return jsonify(data), 200

@user_bp.route("/deny-user", methods=["POST"])
@jwt_required()
def deny_pending_user():
    data = request.get_json()
    username = get_jwt_identity()
    ip = get_client_ip()
    user_id = data.get('user_id')
    id_front = data.get('id_front')
    id_back = data.get('id_back')
    fname = data.get('fname')
    lname = data.get('lname')
    email = data.get('email')
    message, status = UserService.deny_pending_user (username,user_id, ip, id_front, id_back, fname + " " + lname, email)
    return jsonify({"message": message}), status 

@user_bp.route("/approve-user", methods=["POST"])
@jwt_required()
def approve_pending_user():
    data = request.get_json()
    username = get_jwt_identity()
    ip = get_client_ip()
    user_id = data.get('user_id')
    fname = data.get('fname')
    lname = data.get('lname')
    email = data.get('email')
    
    message, status = UserService.approve_pending_user(username, user_id, ip, fname, lname, email)
    
    return jsonify({"message": message}), status