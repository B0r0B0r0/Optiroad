from database.connection import get_db_connection
import requests
from utils.helpers import get_country_code, geocode_city, format_name

class CityService:
    @staticmethod
    def add_city(username, country, county, city, source_ip):
        """Add a new city with geocoding"""
        # Format names
        country = format_name(country)
        county = format_name(county)
        city = format_name(city)
        
        # Get country code
        country_code = get_country_code(country)
        if not country_code:
            return False, 'Invalid country name provided'
        
        # Geocode city
        lat, lon = geocode_city(city, county, country)
        if lat == 0.0 and lon == 0.0:
            return False, 'We could not get the cities location, please verify the provided information.'
        
        # Add to database
        conn = get_db_connection()
        if conn is None:
            return False, 'Database connection failed'
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT add_city_with_hierarchy(%s, %s, %s, %s, %s, %s, %s, %s);
            """, (username, country, country_code, county, city, lat, lon, source_ip))
            result = cursor.fetchone()[0]
            conn.commit()
            
            if result == "City added successfully":
                return True, result
            else:
                return False, result
                
        except Exception as e:
            print("Error in add_city:", e)
            return False, f'Internal error: {e}'
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_managed_cities(username, source_ip):
        """Get cities managed by user"""
        conn = get_db_connection()
        if not conn:
            return None, 'DB connection error'
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT get_managed_cities(%s, %s);", (username, source_ip))
            result = cursor.fetchone()[0]
            return result, "Success"
        except Exception as e:
            print("Error in get_managed_cities:", e)
            return None, 'Internal error'
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_city_coordinates(city, county, country, source_ip):
        """Get coordinates for a specific city"""
        conn = get_db_connection()
        if not conn:
            return None, "DB connection error"
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT get_city_coordinates(%s, %s, %s, %s);",
                (city, county, country, source_ip)
            )
            result = cursor.fetchone()[0]
            return result, "Success"
        except Exception as e:
            print("Error in get_city_coordinates:", e)
            return None, "Internal error"
        finally:
            cursor.close()
            conn.close()


    @staticmethod
    def get_city_devices(city, county, country, username, source_ip):
        conn = get_db_connection()
        if not conn:
            return None, "DB connection failed"
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM get_city_devices(%s, %s, %s, %s, %s);",
                (city, county, country, username, source_ip)
            )
            
            row = cursor.fetchone()
            if not row:
                return [], "No devices returned"

            device_list = row[0]  # JSON array de la funcția SQL

            devices = []
            for item in device_list:
                device_id = item.get("device_id")
                lat = item.get("lat")
                lon = item.get("lon")
                ip_address = item.get("ip_address")
                location = item.get("node_name") or "Unknown location"
                stream_url = f"http://{ip_address}:5050/stream"

                # Test ping/health
                status = "offline"
                try:
                    r = requests.get(f"http://{ip_address}:5050/health", timeout=1.5)
                    if r.text.strip().lower() == "ok":
                        cursor.execute(
                            "SELECT * FROM update_device_status(%s, %s, %s);",
                            (int(device_id), "online", source_ip)
                        )
                        status = "online"     
                except:
                    cursor.execute(
                            "SELECT * FROM update_device_status(%s, %s, %s);",
                            (int(device_id), "offline", source_ip)
                        )
                    


                devices.append({
                    "id": device_id,
                    "lat": float(lat),
                    "lng": float(lon),
                    "location": location,
                    "status": status,
                    "videoUrl": stream_url
                })

            return devices, "Success"
        
        except Exception as e:
            print("Error in get_city_devices:", e)
            return None, f"Internal error: {e}"

        finally:
            conn.commit()
            cursor.close()
            conn.close()