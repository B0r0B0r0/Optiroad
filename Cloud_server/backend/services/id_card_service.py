from storage.minio_client import send_file
from flask import jsonify

class id_card_service:
    @staticmethod
    def get_id_card_by_id(link):
        try:
            return send_file(link), None
        except Exception as e:
            print(f"[ERROR] Could not serve image: {e}")
            return None, "Could not serve image"
