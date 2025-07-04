from pymongo import MongoClient
from config.settings import Config


client = MongoClient(Config.MONGO_URI)
db = client[Config.DB_NAME]

# Colecțiile
events_collection = db["rsu_events"]
aggregated_collection = db["aggregated_edges"]
rou_files_collection = db["rou_files"]
ppo_models_collection = db["ppo_models"]
