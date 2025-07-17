from random import randint

string = "["

for i in range(720):
    string+= str(randint(i*5, (i+1)*5)) +", "

string[:-2] + "]"

random_number = randint(200, 720)

from ultralytics import YOLO
model = YOLO("yolov8n.pt")
model.export(format="onnx")