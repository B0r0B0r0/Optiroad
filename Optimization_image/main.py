from FindOsmCode import get_city_osm2
from MapImport import get_city_map
from SumoScripts import run_scripts
from TrafficLightLogic import extract_phases_to_json, update_phases_from_json
from RunSimulation import run_simulation_and_measure_mean
from IDontEvenThinkItsWorth import trainPPO
from mongo import fetch_rou_from_mongo_and_save, save_ppo_metrics
from regenerate_rou_file import replace_tls_ids_with_edges
from config import MONGO_URI
import os

def init(path_to_file, city, county, country, start_time, end_time, day):

    osm_code = get_city_osm2(city, county, country)
    get_city_map(osm_code, path_to_file)
    fetch_rou_from_mongo_and_save(
        mongo_uri=MONGO_URI,
        country=country,
        county=county,
        city=city,
        start_time=start_time,
        end_time=end_time,
        day=day,
        sumo_path=path_to_file
    )
    run_scripts(path_to_file)
    replace_tls_ids_with_edges(path_to_file + ".rou.xml")

    # Extract initial phase durations and measure baseline
    extract_phases_to_json(path_to_file, path_to_file)


def main(country, county, city,start_time, end_time, day):
    path_to_file = f"Cities/{country}/{county}/{city}/{city}"
    
    init(path_to_file, city, county, country, start_time, end_time, day)

    vehicle_waiting_init , init_mean_vector= run_simulation_and_measure_mean(path_to_file)

    trainPPO(
            sumopath=path_to_file,
            max_episodes=1,
            country=country,
            county=county,
            city=city,
            start_time=start_time,
            end_time=end_time,
            day=day
            )
    

    update_phases_from_json(path_to_file, path_to_file)

    vehicle_waiting_post , post_mean_vector = run_simulation_and_measure_mean(path_to_file)

    save_ppo_metrics(
        mongo_uri=MONGO_URI,
        country=country,
        county=county,
        city=city,
        start_time=start_time,
        end_time=end_time,
        day=day,
        vehicle_waiting_init=vehicle_waiting_init,
        vehicle_waiting_post=vehicle_waiting_post,
        init_mean_vector=init_mean_vector,
        post_mean_vector=post_mean_vector
    )


 

if __name__ == "__main__":

    country = os.getenv("COUNTRY")
    county = os.getenv("COUNTY")
    city = os.getenv("CITY")
    start_time = os.getenv("START")
    end_time = os.getenv("END")
    day = os.getenv("DAY")

    main(country, county, city, start_time, end_time, day)