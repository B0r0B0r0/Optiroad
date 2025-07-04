import math
import time
import cv2
import imagehash
from ultralytics import YOLO
from PIL import Image
from detector.car import Car
from network.client import send_update
import config


class Detector:
    def __init__(self, self_id, country, county, city, ip):
        self.self_id = self_id
        self.country = country
        self.county = county
        self.city = city
        self.ip= ip
        self.model = YOLO(config.MODEL_PATH)
        self.cap = cv2.VideoCapture(config.VIDEO_SOURCE)

        self.offset_car = 0
        self.hash = None
        self.car_list = []
        self.entered_timestamps = []
        self.counter_down = 0
        self.last_update = time.time()
        self.latest_frame = None

    def init_first_frame(self):
        """
        Rulează până la prima detectare validă pentru a calcula offset-ul mașinii
        și a popula lista inițială de mașini.
        """
        while self.offset_car == 0:
            ret, frame = self.cap.read()
            if not ret:
                continue

            self.latest_frame = frame.copy()    

            results = self.model.predict(frame, classes=config.VEHICLE_CLASSES)
            self.hash = imagehash.phash(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            found = False

            for result in results:
                for box in result.boxes:
                    class_index = int(box.cls.item())
                    x1, y1, x2, y2 = [int(coord) for coord in box.xyxy[0].tolist()]
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    if class_index == 2 and not found:
                        self.offset_car = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) // 2
                        found = True
                    self.car_list.append(Car([center_x, center_y]))

            if config.DEBUG_VIEW:
                cv2.imshow("YOLO Detection", frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    self.stop()

    def step(self):
        """
        Rulează o iterație de procesare:
        - verifică dacă frame-ul e diferit de anteriorul
        - face YOLO dacă e necesar
        - actualizează car_list și latest_frame
        """
        ret, frame = self.cap.read()
        if not ret:
            self.cap.release()
            self.cap = cv2.VideoCapture(config.VIDEO_SOURCE)
            return  # ieși din pasul curent fără să procesezi

        current_hash = imagehash.phash(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        if self.hash - current_hash <= 5:
            self.latest_frame = frame.copy()
            return  # frame prea similar, ignorăm

        self.hash = current_hash
        results = self.model.predict(frame, classes=config.VEHICLE_CLASSES, conf=0.5)

        for result in results:
            for box in result.boxes:
                class_index = int(box.cls.item())
                x1, y1, x2, y2 = [int(coord) for coord in box.xyxy[0].tolist()]
                confidence = box.conf.item()
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                label = config.CLASS_LIST[class_index]

                found = any(car.update_center([center_x, center_y], self.offset_car) for car in self.car_list)

                if not found:
                    self.car_list.append(Car([center_x, center_y]))


                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f'{label} {confidence:.2f}', (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Update car state
        for car in self.car_list[:]:
            result = car.update_iter()
            if result == 1:
                self.counter_down += 1
                self.car_list.remove(car)
            elif result == -1:
                t = time.localtime()
                timestamp = t.tm_min * 60 + t.tm_sec
                self.entered_timestamps.append(timestamp)
                self.car_list.remove(car)

        # Salvează latest_frame doar dacă a fost procesat
        self.latest_frame = frame.copy()

        if config.DEBUG_VIEW:
            cv2.imshow("YOLO Detection", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                self.stop()

    def should_update(self):
        return time.time() - self.last_update >= config.UPDATE_INTERVAL

    def send_periodic_update(self):
        send_update(self.entered_timestamps, self.counter_down, self.self_id, self.country, self.county, self.city, self.ip)
        self.entered_timestamps = []
        self.counter_down = 0
        self.last_update = time.time()

    def get_latest_frame(self):
        return self.latest_frame

    def stop(self):
        self.cap.release()
        cv2.destroyAllWindows()
