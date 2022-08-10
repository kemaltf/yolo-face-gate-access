### IMPORT PACKAGE ###
import cv2
from yolobykemal import yolo

#PARAMETER YOLO
weight = "/home/kemal/Downloads/AutomaticParkByKemal/model/deteksiPlat/deteksiPlat.weights"
cfg = "/home/kemal/Downloads/AutomaticParkByKemal/model/deteksiPlat/deteksiPlat.cfg"
names = "/home/kemal/Downloads/AutomaticParkByKemal/model/deteksiPlat/deteksiplat.names"
levelConf = 0.5

def deteksiplat(image,scaler=1):
    """
    image: gambar input yang akan dideteksi
    """
        
    # LAKUKAN DETEKSI
    hasilDeteksi = yolo(weight, cfg, names, image, levelConf,scaler)
    # AMBIL DATA YANG DI CROP
    img = hasilDeteksi[0]
    
    return img
