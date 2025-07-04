from geopy.geocoders import Nominatim


def get_city_osm(city_name,county_name,country_name):
    geolocator = Nominatim(user_agent="optiroad")
    address = f"{city_name}, {county_name}, {country_name}"
    
    location = geolocator.geocode(address)
    if location is None:
        raise Exception(f"[ERROR] Could not geocode the address: {address}")
    osm_id = location.raw["osm_id"]
    if osm_id is None:
        raise Exception(f"[ERROR] Error at getting osm_id for the address: {address}")
    
    return osm_id + 3600000000 


def get_city_osm2(city_name,county_name,country_name):
    geolocator = Nominatim(user_agent="optiroad")
    address = f"{city_name}, {county_name}, {country_name}"
    locations = geolocator.geocode(address, exactly_one=False, addressdetails=True, extratags=True)
    if not locations:
        raise Exception(f"[ERROR] Could not geocode the address: {address}")

    for location in locations:
        osm_type = location.raw.get("type", "")
        class_type = location.raw.get("class", "")
        
        if class_type == "boundary" and osm_type in ["administrative", "city", "town"]:
            return location.raw["osm_id"] + 3600000000
        
    if county_name != "":
        return get_city_osm2(city_name, "", country_name)
        
    raise Exception(f"[ERROR] No suitable OSM ID found for the address: {address}")