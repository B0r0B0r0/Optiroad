import requests
import config


def get_coordinates():
    # În viitor, poate citi din GPS sau ENV
    return config.LATITUDE, config.LONGITUDE

def send_init(ip):
    lat, lon = get_coordinates()
    to_send = {"lat": lat, "lon": lon, "ip": ip}

    try:
        response = requests.post(f"{config.BACKEND_URL}/rsu/register-camera", json=to_send)
        if response.status_code == 200:
            return response.json().get("rsu_id"), response.json().get("country"), response.json().get("county"), response.json().get("city")
    except Exception as e:
        print(f"[ERROR] Failed to send init: {e}")
    return False

def send_update(entered_timestamps, counter_down, rsu_id, country, county, city, ip):
    to_send = {
        "rsu_id": rsu_id,
        "country": country,
        "county": county,
        "city": city,
        "ip": ip,
        "entered": entered_timestamps,
        "exited": counter_down
    }

    try:
        response = requests.post(f"{config.BACKEND_URL}/rsu/update_rsu", json=to_send)
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] Failed to send update: {e}")
        return False
