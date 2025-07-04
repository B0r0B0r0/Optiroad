from flask import Blueprint, request, jsonify
from services.mail_service import MailService

mail_bp = Blueprint('mail', __name__)

@mail_bp.route("/contact-mail", methods=["POST"])
def send_contact_mail():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    if not name or not email or not message:
        return jsonify({'message': 'Missing required fields'}), 400

    success, response_message = MailService.send_contact_email(name, email, message)
    
    if success:
        return jsonify({'message': response_message}), 200
    else:
        return jsonify({'message': response_message}), 500

