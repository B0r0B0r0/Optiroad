from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from services.city_service import CityService
from utils.helpers import get_client_ip

city_bp = Blueprint('city', __name__)

@city_bp.route('/add', methods=['POST'])
@jwt_required()
def add_city():
    data = request.get_json()
    country = data.get("country")
    county = data.get("county")
    city = data.get("city")
    source_ip = get_client_ip()
    username = get_jwt_identity()

    if not country or not county or not city:
        return jsonify({'message': 'Missing required fields'}), 400

    success, message = CityService.add_city(username, country, county, city, source_ip)
    
    if success:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'message': message}), 400

@city_bp.route('/get-cities', methods=['GET'])
@jwt_required()
def get_my_cities():
    username = get_jwt_identity()
    source_ip = get_client_ip()
    
    cities, message = CityService.get_managed_cities(username, source_ip)
    
    if cities is not None:
        return jsonify(cities), 200
    else:
        return jsonify({'message': message}), 500

@city_bp.route('/coordinates', methods=['POST'])
@jwt_required()
def get_city_coordinates_from_body():
    data = request.get_json()
    source_ip = get_client_ip()

    city = data.get("city")
    county = data.get("county")
    country = data.get("country")

    if not city or not county or not country:
        return jsonify({"error": "Missing city, county or country"}), 400

    coordinates, message = CityService.get_city_coordinates(city, county, country, source_ip)
    
    if coordinates is not None:
        return jsonify(coordinates), 200
    else:
        return jsonify({"message": message}), 500

@city_bp.route('/devices', methods=['POST'])
@jwt_required()
def get_city_devices():
    username = get_jwt_identity()
    source_ip = get_client_ip()
    data = request.get_json()
    city = data.get("city")
    county = data.get("county")
    country = data.get("country")
    devices, message = CityService.get_city_devices(city, county, country, username, source_ip)

    if devices is not None:
        return jsonify({"devices": devices}), 200
    else:
        return jsonify({"message": message}), 500