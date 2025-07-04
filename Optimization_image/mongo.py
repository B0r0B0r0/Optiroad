from pymongo import MongoClient
import os
from datetime import datetime

def fetch_rou_from_mongo_and_save(
    mongo_uri,
    country, county, city,
    start_time, end_time, day,
    sumo_path
):
    client = MongoClient(mongo_uri)
    db = client["ppo_results"]
    collection = db["rou_files"]

    query = {
        "location.country": country,
        "location.county": county,
        "location.city": city,
        "window.day": day,
        "window.start": start_time,
        "window.end": end_time
    }

    doc = collection.find_one(query)
    if not doc:
        raise ValueError("No rou file found in MongoDB for given location and window.")

    rou_content = doc.get("rou_content")
    if not rou_content:
        raise ValueError("rou_content field is missing in MongoDB document.")

    with open(sumo_path+".rou.xml", "w") as f:
        f.write(rou_content)


def save_ppo_metrics(
    mongo_uri,
    country, county, city,
    start_time, end_time, day,
    vehicle_waiting_init, vehicle_waiting_post,
    init_mean_vector, post_mean_vector
):
    client = MongoClient(mongo_uri)
    db = client["ppo_results"]
    collection = db["ppo_metrics"]

    doc = {
        "location": {
            "country": country,
            "county": county,
            "city": city
        },
        "window": {
            "day": day,
            "start": start_time,
            "end": end_time
        },
        "vehicle_waiting_init": vehicle_waiting_init,
        "vehicle_waiting_post": vehicle_waiting_post,
        "init_mean_vector": init_mean_vector,
        "post_mean_vector": post_mean_vector,
        "created_at": datetime.utcnow()
    }

    result = collection.insert_one(doc)
    print(f"[INFO] PPO metrics saved with id: {result.inserted_id}")

