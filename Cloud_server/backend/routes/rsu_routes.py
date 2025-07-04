from flask import Blueprint, request, jsonify
from services.rsu_service import RsuService
from utils.helpers import get_client_ip

rsu_bp = Blueprint('rsu', __name__)

@rsu_bp.route('/register-camera', methods=['POST'])
def register_camera():
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')
    ip = data.get('ip')
    message, status = RsuService.register_camera(lat, lon, ip)
    return jsonify(message), status 

@rsu_bp.route('update_rsu', methods=['POST'])
def update_rsu():
    data = request.get_json()
    required_fields = ["rsu_id", "country", "county", "city", "entered", "exited", "ip"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    rsu_id = data['rsu_id']
    country = data['country']
    county = data['county']
    city = data['city']
    ip = data['ip']
    entered = data['entered']
    exited = data['exited']
    
    message, status = RsuService.update_rsu(rsu_id, country, county, city, entered, exited,ip)
    return jsonify(message), status