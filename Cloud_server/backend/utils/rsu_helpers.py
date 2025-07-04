import overpy
import math
import requests
import unicodedata

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # rază Pământ (m)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def find_nearest_tls(lat, lon, radius=1000):
    api = overpy.Overpass()
    query = f"""
    (
      node["highway"="traffic_signals"](around:{radius},{lat},{lon});
    );
    out body;
    """
    result = api.query(query)

    if not result.nodes:
        return None, float("inf")  

    nearest = None
    min_dist = float("inf")

    for node in result.nodes:
        d = haversine(float(lat), float(lon), float(node.lat), float(node.lon))
        if d < min_dist:
            min_dist = d
            nearest = node

    return nearest.id if nearest else None

def remove_diacritics(text):
    if not text:
        return text

    normalized = unicodedata.normalize('NFD', text)

    return ''.join(
        c for c in normalized
        if unicodedata.category(c) != 'Mn'
    )

def reverse_geocode(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json"
    }
    headers = {
        "User-Agent": "OptiRoad/1.0"
    }

    r = requests.get(url, params=params, headers=headers)
    if r.status_code != 200:
        return None

    data = r.json()
    return {
        "city": remove_diacritics(data["address"].get("city") or data["address"].get("town")),
        "county": remove_diacritics(data["address"].get("county")),
        "country": remove_diacritics(data["address"].get("country"))
    }
