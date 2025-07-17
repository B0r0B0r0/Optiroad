from pymongo import MongoClient
from config.settings import Config


client = MongoClient(Config.MONGO_URI)
db = client[Config.DB_NAME]

# Colecțiile
events_collection = db["rsu_events"]
ppo_metrics = db["ppo_metrics"]
rou_files_collection = db["rou_files"]
ppo_models_collection = db["ppo_models"]
