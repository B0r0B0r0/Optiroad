import requests
import os

def get_city_map(osm_code, output_file="unnamed/export"):
    query = f"""
 [out:xml];
area({osm_code})->.a;
(
  way(area.a)
  ['name']
  ['highway']
  ['highway' !~ 'path']
  ['highway' !~ 'steps']
  ['highway' !~ 'motorway']
  ['highway' !~ 'motorway_link']
  ['highway' !~ 'raceway']
  ['highway' !~ 'bridleway']
  ['highway' !~ 'proposed']
  ['highway' !~ 'construction']
  ['highway' !~ 'elevator']
  ['highway' !~ 'bus_guideway']
  ['highway' !~ 'footway']
  ['highway' !~ 'cycleway']
  ['foot' !~ 'no']
  ['access' !~ 'private']
  ['access' !~ 'no'];
  node(area);
);
(._;>;);
out;
    """

    url = "http://overpass-api.de/api/interpreter"
    
    response = requests.get(url, params={"data": query})
    export_file = f"{output_file}.osm"
    if response.status_code == 200:
        os.makedirs(os.path.dirname(export_file), exist_ok=True)
        with open(export_file, "w", encoding="utf-8") as file:
            file.write(response.text)
        #for debugging
        print(f"{osm_code} map has been saved in {export_file}")
        return "Success"
    else:
        raise Exception(f"[ERROR] Error at downloading map ({response.status_code})")