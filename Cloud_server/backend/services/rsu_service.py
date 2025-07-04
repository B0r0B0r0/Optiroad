from utils.rsu_helpers import find_nearest_tls, reverse_geocode
from database.connection import get_db_connection
from datetime import datetime, timedelta
from database.mongo import events_collection, rou_files_collection
from utils.rou_generator_helpers import generate_rou_file, aggregate_rsu_events
import docker

class RsuService:
    @staticmethod
    def register_camera(lat, lon, ip):
        id = find_nearest_tls(lat, lon)
        if id is None:
            return "No traffic light found nearby", 404

        address = reverse_geocode(lat, lon) 
        if address is None:
            return "Failed to reverse geocode the location", 500
        
        connection = get_db_connection()

        if not connection:
            return "Database connection failed", 500
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT add_device(%s::VARCHAR, %s::VARCHAR, %s::VARCHAR, %s::VARCHAR, %s::DECIMAL, %s::DECIMAL, %s::VARCHAR, %s::VARCHAR);
            """, (
                str(id),
                address['city'],
                address['county'],
                address['country'],
                float(lat),
                float(lon),
                ip,
                ip
            ))

            db_msg = cursor.fetchone()[0]
            connection.commit()
            if db_msg == "Device added successfully" or db_msg == "Device connected successfully":
                return {
                    "rsu_id": id,
                    "country": address['country'],
                    "county": address['county'],
                    "city": address['city'],
                    }, 200
            else:
                return db_msg+ f"+ {address['city']} + {address['county']} + {address['country']}", 400
        except Exception as e:
            return f"Database error: {e}", 500
        finally:
            if connection:
                connection.close()

    @staticmethod
    def generate_rou(events_list, location, window):
        try:
            aggregated_data = aggregate_rsu_events(events_list)
            rou_file = generate_rou_file(aggregated_data)

            doc = {
                "location": location,
                "window": window,
                "created_at": datetime.utcnow(),
                "rou_content": rou_file
            }

            rou_files_collection.insert_one(doc)
            return {"status": "ok"}, 200

        except Exception as e:
            return {"status": "error", "error": str(e)}, 500



    @staticmethod
    def launch_model(country, county, city, start, end, day):
        mongo_uri = "mongodb://admin:secret123@host.docker.internal:27017"

        print("[INFO] Launching PPO training container (detach=True)...", flush=True)

        client = docker.from_env()

        try:
            container = client.containers.run(
                image="ppo_image",
                remove=True,
                environment={
                    "COUNTRY": country,
                    "COUNTY": county,
                    "CITY": city,
                    "START": start,
                    "END": end,
                    "DAY": day,
                    "MONGO_URI": mongo_uri
                },
                detach=True
            )
            print(f"[INFO] PPO container launched with ID: {container.id}", flush=True)

        except docker.errors.ContainerError as e:
            print("[ERROR] Container failed to launch:", e, flush=True)
        except Exception as e:
            print("[ERROR] Docker launch error:", e, flush=True)


    @staticmethod
    def aggregate_data(country, county, city, source_ip):
        now = datetime.utcnow()
        start_time = (now - timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)
        day_of_week = start_time.strftime("%A")

        window = {
            "day": day_of_week,
            "start": start_time.isoformat(),
            "end": end_time.isoformat()
        }

        print("Verific in postgres\n",flush=True)
        # 1️⃣ Postgres: get number of online RSU for this city
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM get_city_online_count(%s, %s, %s, %s);",
                (country, county, city, source_ip)
            )
            row = cursor.fetchone()
            online_count = row[0] if row else 0
            print(f"Am gasit {online_count} camere online\n",flush=True)
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"[ERROR] Postgres error: {e}")
            return

        if online_count <= 0:
            print(f"[WARN] No RSU registered as online for {city}")
            return

        # 2️⃣ Mongo: count distinct RSU reports for this window
        try:
            reported_count = events_collection.count_documents({
                "location.country": country,
                "location.county": county,
                "location.city": city
            })
            print(f"Am gasit {reported_count} camere raportate\n",flush=True)
        except Exception as e:
            print(f"[ERROR] MongoDB error: {e}")
            return

        if reported_count == online_count:
            try:
                events_cursor = events_collection.find({
                    "location.country": country,
                    "location.county": county,
                    "location.city": city
                })

                events_list = list(events_cursor)

                _ = events_collection.delete_many({
                    "location.country": country,
                    "location.county": county,
                    "location.city": city
                })
            except Exception as e:
                print(f"[ERROR] MongoDB read error: {e}")
                return
            
            result, status = RsuService.generate_rou(
                events_list,
                {"country": country, "county": county, "city": city},
                window
            )
            if status == 200:
                RsuService.launch_model(country=country, county=county, city=city,
                                        start=window['start'], end=window['end'], day=window['day'])
            else:
                return

                    

    @staticmethod
    def update_rsu(rsu_id, country, county, city, entered, exited, ip):
        now = datetime.utcnow()
        start_time = now.replace(minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)
        day_of_week = now.strftime("%A")

        doc = {
            "rsu_id": rsu_id,
            "location": {
                "country": country,
                "county": county,
                "city": city
            },
            "window": {
                "day": day_of_week,
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "entered": entered,
            "exited": exited,
            "received_at": now
        }

        events_collection.insert_one(doc)
        print("Updated RSU\n",flush=True)
        RsuService.aggregate_data(country, county, city, ip)
        return ({"status": "success"}), 200
