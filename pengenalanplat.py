#LIBRARY
from yolobykemal import yolo
import cv2

#PARAMETER
## memasukkan parameter
weight = "/home/kemal/Downloads/AutomaticParkByKemal/model/pengenalanPlat/yolov4-obj_5000.weights"
cfg = "/home/kemal/Downloads/AutomaticParkByKemal/model/pengenalanPlat/pengenalan.cfg"
names = "/home/kemal/Downloads/AutomaticParkByKemal/model/pengenalanPlat/pengenalan.names"
levelConf = 0.75

def pengenalanplat(image,scaler=1):
    # LAKUKAN pengenalan
    hasilPengenalan = yolo(weight, cfg, names, image, levelConf, scaler)
    licensePlate= str(hasilPengenalan[2]) # SIMPAN DATA PLAT NOMOR
    return licensePlate
