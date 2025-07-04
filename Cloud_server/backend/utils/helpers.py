from flask import request
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError
import pycountry
import random
import string

# Initialize geolocator
geolocator = Nominatim(user_agent="OptiRoad/1.0 (contact@optiroad.com)", timeout=10)

def get_client_ip():
    """Get client IP address from request headers"""
    if 'X-Forwarded-For' in request.headers:
        ip = request.headers['X-Forwarded-For'].split(',')[0]
    elif 'X-Real-IP' in request.headers:
        ip = request.headers['X-Real-IP']
    else:
        ip = request.remote_addr
    return ip

def geocode_city(city, county, country):
    """Geocode a city to get latitude and longitude"""
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
    """Get country code from country name"""
    try:
        country = pycountry.countries.get(name=country_name)
        if not country:
            country = next((c for c in pycountry.countries if country_name.lower() in c.name.lower()), None)
        return country.alpha_2 if country else None
    except Exception as e:
        print(f"Error getting country code: {e}")
        return None

def format_name(name):
    """Format name with proper capitalization"""
    return name.lower().capitalize()

def generate_key():
    chars = string.ascii_letters + string.digits
    key_parts = [''.join(random.choices(chars, k=4)) for _ in range(4)]
    return '-'.join(key_parts)
