from flask import jsonify
from database.connection import get_db_connection
from storage.minio_client import upload_file, delete_file
from services.mail_service import MailService
from utils.helpers import generate_key

class UserService:
    @staticmethod
    def add_user_with_id_cards(data, files, source_ip):
        # Extragem datele
        f = data.get
        first_name = f("firstName")
        last_name = f("lastName")
        birth_date = f("birthDate")
        address = f("address")
        profession = f("profession")
        workplace = f("workplace")
        email = f("email")
        phone = f("phoneNumber")

        id_front = files.get("idFront")
        id_back = files.get("idBack")

        if not id_front or not id_back:
            return False, "Missing ID images"

        # Upload to MinIO
        front_url = upload_file(id_front)
        back_url = upload_file(id_back)

        # Inserare în DB
        conn = get_db_connection()
        if not conn:
            return False, "Database connection failed"

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT add_user(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                first_name, last_name, birth_date, address, email,
                profession, workplace, phone, front_url, back_url, source_ip
            ))
            result = cursor.fetchone()[0]
            conn.commit()
            return True, result
        except Exception as e:
            print(f"DB error: {e}")
            return False, "Database error"
        finally:
            cursor.close()
            conn.close()
            
    @staticmethod
    def get_pending_users(username, source_ip):
        connection = get_db_connection()
        if not connection:
            return None, "Database connection failed"
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT get_pending_users(%s, %s);", (username, source_ip))
            result = cursor.fetchone()[0]
            
            if 'error' in result:
                return None, result['error']

            formatted_result = {}
            for user in result:
                user_id = user.pop('id')
                formatted_result[user_id] = user

            result = {
                "users": formatted_result
            }

            return result, "Success"

        except Exception as e:
            print(f"Error fetching pending users: {e}")
            return None, "Internal error"
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def deny_pending_user(username, user_id, source_ip, id_front, id_back, name, email):
        connection = get_db_connection()
        delete_file(id_front)
        delete_file(id_back)
        if not connection:
            return "Database connection failed", 500
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT deny_pending_user(%s, %s, %s);", (username, int(user_id), source_ip))
            result = cursor.fetchone()[0]
            connection.commit()
            if result == "Pending user denied and deleted successfully":
                MailService.send_deny_email(name, email)
                return result, 200
            else:
                return "An error occurred", 400
            
        except Exception as e:
            return "Internal error", 500
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def approve_pending_user(username, user_id, source_ip, fname, lname, email):
        key = generate_key()
        connection = get_db_connection()
        
        if not connection:
            return "Database connection failed", 500
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT add_key(%s, %s, %s, %s);", (int(user_id), username, key, source_ip))
            result = cursor.fetchone()[0]

            if result != "Key created and assigned successfully":
                return "An error occurred while creating the key", 400
            
            cursor.execute("SELECT approve_pending_user(%s, %s, %s, %s, %s);", (int(user_id), username, fname, lname, source_ip))
            result = cursor.fetchone()[0]

            if result == "User approved successfully":
                MailService.send_approve_email(key, fname + " " + lname, email)
                connection.commit()
                return result, 200
            else:
                return "An error occurred", 400
            
        except Exception as e:
            return "Internal error", 500
        finally:
            cursor.close()
            connection.close()
