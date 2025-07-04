import bcrypt
import base64
from database.connection import get_db_connection
from utils.helpers import get_client_ip

class AuthService:
    @staticmethod
    def verify_password(username, password, source_ip):
        """Verify user password"""
        connection = get_db_connection()
        if not connection:
            return False, "Database connection failed"
            
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT get_password(%s, %s);", (username, source_ip))
            result = cursor.fetchone()
            
            if result and result[0] == "Invalid credentials":
                return False, "Invalid credentials"
            
            db_password = base64.b64decode(result[0]).decode('utf-8')
            
            if bcrypt.checkpw(password.encode('utf-8'), db_password.encode('utf-8')):
                return True, "Password verified"
            else:
                return False, "Invalid credentials"
                
        except Exception as e:
            print(f"Error verifying password: {e}")
            return False, "Internal error"
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def register_user(username, password, email, key, source_ip):
        """Register a new user"""
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        hashed_password_base64 = base64.b64encode(hashed_password.encode('utf-8')).decode('utf-8')

        connection = get_db_connection()
        if not connection:
            return False, "Database connection failed"

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT register_user(%s, %s, %s, %s, %s);", 
                         (username, hashed_password_base64, email, key, source_ip))
            result = cursor.fetchone()
            
            if result and result[0] == "User registered successfully":
                connection.commit()
                return True, "User registered successfully"
            else:
                return False, result[0] if result else "Registration failed"
                
        except Exception as e:
            print(f"Error registering user: {e}")
            return False, "Internal error"
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def get_user_profile(username, source_ip):
        """Get user profile information"""
        connection = get_db_connection()
        if not connection:
            return None, "Database connection failed"
            
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT get_user_role(%s, %s)", (username, source_ip))
            result = cursor.fetchone()
            
            if not result:
                return None, "User not found"
            
            if 'error' in result[0]:
                return None, result[0]['error']
            
            return result[0], "Success"
            
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None, "Internal error"
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def update_password(username, old_password, new_password, source_ip):
        """Update user password"""
        # First verify old password
        is_valid, message = AuthService.verify_password(username, old_password, source_ip)
        if not is_valid:
            return False, "Incorrect current password"
        
        # Hash new password
        hashed_new = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        hashed_new_b64 = base64.b64encode(hashed_new.encode('utf-8')).decode('utf-8')
        
        connection = get_db_connection()
        if not connection:
            return False, "Database connection failed"
        
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT update_user_password(%s, %s, %s);", 
                         (username, hashed_new_b64, source_ip))
            result = cursor.fetchone()[0]
            connection.commit()
            
            if result == "Password updated successfully":
                return True, result
            else:
                return False, result
                
        except Exception as e:
            print(f"Error updating password: {e}")
            return False, "Internal error"
        finally:
            cursor.close()
            connection.close()
