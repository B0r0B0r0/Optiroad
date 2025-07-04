from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from services.id_card_service import id_card_service

id_card_bp = Blueprint('id_card_bp', __name__)


@id_card_bp.route('/<path:filename>', methods=["GET"])
@jwt_required()
def get_id_card(filename):
    id_card, message = id_card_service.get_id_card_by_id(filename)

    if not id_card:
        return jsonify({'message': message}), 404 if message == "ID card not found" else 500

    return id_card, 200