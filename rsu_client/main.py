import time
import threading
from detector import Detector
from server.stream_server import app, set_frame_callback
from network.client import send_init
from utils.helpers import wait_until_next_hour
from server.helpers import get_local_ip

def start_flask():
    app.run(host="0.0.0.0", port=5050, threaded=True)

if __name__ == "__main__":
    # 1. Trimitem init și așteptăm răspuns
    ip =get_local_ip()
    self_id, country, county, city = send_init(ip)
    while not self_id:
        print("[INFO] Retry init in 5s...")
        time.sleep(5)
        self_id = send_init()

    # print(f"[INFO] RSU registered with ID: {self_id}")

    #wait_until_next_hour()

    # 2. Inițializăm detectorul și prima detecție
    detector = Detector(self_id, country, county, city, ip)
    
    threading.Thread(target=start_flask, daemon=True).start()
    set_frame_callback(detector.get_latest_frame)
    
    detector.init_first_frame()

    # 3. Legăm callback-ul pentru Flask

    # 4. Pornim serverul Flask pe thread separat

    # 5. Loop principal: YOLO + periodic update
    try:
        while True:
            detector.step()
            if detector.should_update():
                detector.send_periodic_update()
    except KeyboardInterrupt:
        print("[INFO] Oprit cu CTRL+C")
    finally:
        detector.stop()
