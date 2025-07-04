from flask import Flask, request, jsonify, make_response, session
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_mail import Mail, Message
import os
import psycopg2
import bcrypt
import base64
import json
from MailService import get_contact_email, get_key_email
import secrets
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError
import pycountry

#### Globals
TEMP = False # Schimba cand treci in https
DATABASE_URL = os.environ.get('DATABASE_URL')
NGINX_URL = os.environ.get('NGINX_URL')
ACCESS_EXP_TIME = 900
REFRESH_EXP_TIME = 2592000
SENDER_EMAIL = "stinaalin@gmail.com"
PASSWORD_EMAIL = "skgr kvav qjtc vdbp"

#### Inits
app = Flask(__name__) 


app.config['SECRET_KEY'] = 'super_secret_key'    # TODO Modify

#### JWT configs
app.config['JWT_TOKEN_LOCATION'] = ['cookies']  
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'  
app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 900  # 15 minute
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 2592000  # 30 zile
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

#### Session csrf configs
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_USE_SIGNER"] = True

#### Mail configs
app.config['MAIL_SERVER']= 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = SENDER_EMAIL
app.config['MAIL_PASSWORD'] = PASSWORD_EMAIL
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

#### Cors
CORS(app, origins=NGINX_URL, methods=["POST","GET","OPTIONS"], 
     allow_headers=["Authorization", "X-CSRF-Token"], supports_credentials=True)
#cors switch to nginx_url os environ

geolocator = Nominatim(user_agent="OptiRoad/1.0 (contact@optiroad.com)", timeout=10)

jwt = JWTManager(app)

#### Middlewares
@app.before_request
def check_csrf_token():
    if request.method in ["POST", "PUT", "DELETE"] and request.endpoint not in ['get_csrf_token', 'login', 'register', 'logout', 'refresh']:
        csrf_token_from_session = session.get("csrf_token")
        csrf_token_from_request = request.headers.get("X-CSRF-Token")

        if not csrf_token_from_request or csrf_token_from_request != csrf_token_from_session:
            return jsonify({"error": "Invalid CSRF Token!"}), 400


#### Utils
def get_client_ip():
    if 'X-Forwarded-For' in request.headers:
        ip = request.headers['X-Forwarded-For'].split(',')[0]
    elif 'X-Real-IP' in request.headers:
        ip = request.headers['X-Real-IP']
    else:
        ip = request.remote_addr
    return ip

def get_db_connection():
    try:
        connection = psycopg2.connect(DATABASE_URL)
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def geocode_city(city, county, country):
    try:
        location = geolocator.geocode(f"{city}, {county}, {country}")
        if location:
            return location.latitude, location.longitude
        else:
            print(f"[WARN] Geocoding failed for: {city}, {county}, {country}")
            return 0.0, 0.0
    except GeocoderServiceError as e:
        print(f"[ERROR] Geocoding exception: {e}")
        return 0.0, 0.0

def get_country_code(country_name):
    try:
        country = pycountry.countries.get(name=country_name)
        if not country:
            country = next((c for c in pycountry.countries if country_name.lower() in c.name.lower()), None)
        return country.alpha_2 if country else None
    except Exception as e:
        print(f"Error getting country code: {e}")
        return None

#### Auth
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    source_ip = get_client_ip()

    if not username or not password or not source_ip:
        return jsonify({'message': 'Invalid request'}), 400
    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(f"SELECT get_password(%s, %s);",(username, source_ip))
    result = cursor.fetchone()
    if result and result[0] == "Invalid credentials":
        cursor.close()
        connection.close()
        return jsonify({'message': result}), 401
    
    db_password = base64.b64decode(result[0]).decode('utf-8')
    connection.commit()
    cursor.close()
    connection.close()

    if not bcrypt.checkpw(password.encode('utf-8'), db_password.encode('utf-8')):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)

    response = make_response(jsonify({'message': 'Login successful'}), 200)

    response.set_cookie('access_token', access_token, httponly=True, secure=TEMP, samesite='Strict', max_age=ACCESS_EXP_TIME)
    response.set_cookie('refresh_token', refresh_token, httponly=True, secure=TEMP, samesite='Strict', max_age=REFRESH_EXP_TIME)

    return response

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    username = get_jwt_identity()  

    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT get_user_role(%s, %s)", (username, get_client_ip()))
    result = cursor.fetchone()
    
    cursor.close()
    connection.close()

    if not result:
        return jsonify({'message': 'Unexpected error'}), 500


    if 'error' in result[0]:
        return jsonify({'message': result[0]['error']}), 404

    return jsonify({
        'username': result[0]['username'],
        'role': result[0]['role']
    }), 200

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    key = data.get('key')
    source_ip = get_client_ip()

    if not username or not password or not email or not key or not source_ip:
        return jsonify({'message': 'Invalid request'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    hashed_password_base64 = base64.b64encode(hashed_password.encode('utf-8')).decode('utf-8')

    connection = get_db_connection()

    if connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT add_user(%s, %s, %s, %s, %s);",(username, hashed_password_base64, email, key, source_ip))
        result = cursor.fetchone()
        if result and result[0] == "User registered successfully":
            connection.commit()
        cursor.close()
        connection.close()

        if result and result[0] == "User registered successfully":
            return jsonify({'message': 'Register successful'}), 200
        else:
            return jsonify({'message': result}), 401
    else:
        return jsonify({'message': 'Database connection failed'}), 500

@app.route("/api/logout", methods=["POST"])
@jwt_required(refresh=True)  
def logout():
    response = make_response(jsonify({"message": "Logged out"}), 200)
    response.set_cookie("access_token", "", expires=0, httponly=True, samesite="Strict")
    response.set_cookie("refresh_token", "", expires=0, httponly=True, samesite="Strict")
    response.set_cookie("session", "", expires=0, httponly=True, samesite="Strict")
    response.set_cookie("csrf_token", "", expires=0, httponly=True, samesite="Strict")
    return response

@app.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True, locations=["cookies"])
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    response = make_response(jsonify({'message': 'Refresh succesful'}), 200)
    response.set_cookie('access_token', access_token, httponly=True, secure=TEMP, samesite='Strict', max_age=ACCESS_EXP_TIME)
    return response

@app.route("/api/csrf-token", methods=["GET"])
def get_csrf_token():
    session["csrf_token"] = secrets.token_hex(32)
    response = jsonify({"msg" : "CSRF token generated"})
    response.set_cookie("csrf_token", session["csrf_token"], httponly=False, secure=TEMP, samesite="Strict", max_age=ACCESS_EXP_TIME)
    return response

@app.route('/api/change-password', methods=['POST'])
@jwt_required()
def change_password():
    
    data = request.get_json()
    username = get_jwt_identity()
    source_ip = get_client_ip()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'message': 'Missing required fields'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()

        # 1. Get current password
        cursor.execute("SELECT get_password(%s, %s);", (username, source_ip))
        result = cursor.fetchone()

        if not result or result[0] == "Invalid credentials":
            return jsonify({'message': 'Current password could not be retrieved'}), 400

        db_password = base64.b64decode(result[0]).decode('utf-8')
        if not bcrypt.checkpw(old_password.encode('utf-8'), db_password.encode('utf-8')):
            return jsonify({'message': 'Incorrect current password'}), 403

        # 2. Hash new password and encode
        hashed_new = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        hashed_new_b64 = base64.b64encode(hashed_new.encode('utf-8')).decode('utf-8')

        # 3. Update password in DB
        cursor.execute("SELECT update_user_password(%s, %s, %s);", (username, hashed_new_b64, source_ip))
        result = cursor.fetchone()[0]
        conn.commit()

        if result == "Password updated successfully":
            return jsonify({'message': result}), 200
        else:
            return jsonify({'message': result}), 400

    except Exception as e:
        return jsonify({'message': "Internal server error"}), 500
    finally:
        cursor.close()
        conn.close()

def send_key_email(key, name, email):
    msg = Message(subject='Your Registration Key', sender=SENDER_EMAIL, recipients=[email])
    msg.html = get_key_email(name, key)
    mail.send(msg)

def generate_key(name, email):
    key = '-'.join([secrets.token_hex(2) for _ in range(4)])
    send_key_email(key, name, email)
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO registration_keys (name, email, key) VALUES (%s, %s, %s);", (name, email, key))
            connection.commit()
            cursor.close()
        except Exception as e:
            print(f"Error inserting key into database: {e}")
        finally:
            connection.close()
    else:
        print("Failed to connect to the database.")
    return key

@app.route('/api/generate-key', methods=['POST'])
def debug():
    password = "admin" 
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    hashed_password_base64 = base64.b64encode(hashed_password.encode('utf-8')).decode('utf-8')
    return jsonify({
        'username': 'admin',
        'password': hashed_password_base64,
    }), 200

@app.route('/api/add-user', methods=['POST'])
def add_user():
    # firstName: "",
    # lastName: "",
    # birthDate: "",
    # address: "",
    # profession: "",
    # occupation: "",
    # workplace: "",
    # email: "",
    # idFront: null,
    # idBack: null
    data = request.get_json()
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    birth_date = data.get('birthDate')
    address = data.get('address')
    profession = data.get('profession')
    workplace = data.get('workplace')
    email = data.get('email')
    phone = data.get('phoneNumber')
    id_front = data.get('idFront')
    id_back = data.get('idBack')
    


#### Mail
@app.route("/api/contact-mail", methods=["POST"])
def index():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    msg = Message(subject='OptiRoad Contact!', sender=SENDER_EMAIL, recipients=[email])
    msg.html = get_contact_email(name, message)
    mail.send(msg)

    return jsonify({'message': 'Email sent!'}), 200



#### Cities
@app.route('/api/cities/add', methods=['POST'])
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

    country = country.lower()
    county = county.lower()
    city = city.lower()
    country = country[0].upper() + country[1:]  
    county = county[0].upper() + county[1:]
    city = city[0].upper() + city[1:]


    country_code = get_country_code(country)

    if not country_code:
        return jsonify({'message': 'Invalid country name provided'}), 400

    lat, lon = geocode_city(city, county, country)

    if lat == 0.0 and lon == 0.0:
        return jsonify({'message': 'We could not get the cities location, please verify the provided information.'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'message': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT add_city_with_hierarchy(%s, %s, %s, %s, %s, %s, %s, %s);
        """, (username, country, country_code, county, city, lat, lon, source_ip))
        result = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        if result == "City added successfully":
            return jsonify({'message': result}), 200
        else:
            return jsonify({'message': result}), 400
    except Exception as e:
        print("Error in /api/cities/add:", e)
        return jsonify({'message': f'Internal error: {e}'}), 500

@app.route('/api/cities/get-cities', methods=['GET'])
@jwt_required()
def get_my_cities():
    username = get_jwt_identity()
    source_ip = get_client_ip()
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'DB connection error'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT get_managed_cities(%s, %s);", (username, source_ip))
        result = cursor.fetchone()[0]
        return jsonify(result), 200
    except Exception as e:
        print("Error in /api/cities/my:", e)
        return jsonify({'message': 'Internal error'}), 500


@app.route('/api/cities/coordinates', methods=['POST'])
@jwt_required()
def get_city_coordinates_from_body():
    data = request.get_json()
    username = get_jwt_identity()
    source_ip = get_client_ip()

    city = data.get("city")
    county = data.get("county")
    country = data.get("country")

    if not city or not county or not country:
        return jsonify({"error": "Missing city, county or country"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"message": "DB connection error"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT get_city_coordinates(%s, %s, %s, %s);",
            (city, county, country, source_ip)
        )
        result = cursor.fetchone()[0]
        return jsonify(result), 200
    except Exception as e:
        print("Error in /api/cities/coordinates:", e)
        return jsonify({"message": "Internal error"}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)