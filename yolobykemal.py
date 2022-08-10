#import packages
import cv2
import numpy as np
import sys
def yolo(weight, cfg, names, img, levelConf=0.5,scaler=1):
    """
    Program yolo opencv disusun oleh:
    Kemal Taufik Fikri
    github: github.com/kemaltf
    instagram: @kemaltfcode
    =============================================
    :weight: Alamat dari weight yang akan digunakan
    :cfg: Alamat dari cfg yang akan digunakan
    :names: Alamat dari file names yang akan digunakan
    :img: gambar yang akan digunakan, pada cv2 gunakan imread
    :levelConf: levelConfidence yang digunakan
    :scaler: angka skala untuk gambar dari 1-4 semakin tinggi skalanya semakin cepat, namun bisa saja tidak terbaca 
    """
    level_confidence = levelConf
    #inisialisasi array
    class_ids = []
    confidences = []
    boxes = []
    texts = []
    cropped = []
    x_array = []
    font = cv2.FONT_HERSHEY_PLAIN
    rawImg = img #menyimpan gambar asli
    net = cv2.dnn.readNet(weight,cfg)
        
    #load YOLO network
    classes = []
    with open(names,"r") as f:
        classes = [line.strip() for line in f.readlines()]
        
    #dapatkkan output layer
    layer_names = net.getLayerNames() 
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
 
    #resize gambar
    img = cv2.resize(img, None, fx = 1/scaler, fy = 1/scaler) #uncoment kalao mau di resize
    
    height, width, channels = img.shape
        
    #detecting object
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416,416),(0,0,0),True,crop = False)
        
    # proses gambar
    net.setInput(blob)
    outs = net.forward(output_layers)
    
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > level_confidence:
                # objek terdeteksi
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                
                #koordinat kotak
                x = int(center_x - w /2)
                y = int(center_y - h /2)
            
                boxes.append([x,y,w,h])
                
                confidences.append(float(confidence))
                class_ids.append(class_id)
                
    #kasih warna untuk setiap kelas
    colors = np.random.uniform(0,255,size=(len(boxes),3))
    #paksa untuk menampilkan hanya 1 box
    indexes = cv2.dnn.NMSBoxes(boxes,confidences,0.5,0.4)
    for i in range(len(boxes)):
        if i in indexes:
            x,y,w,h = boxes[i]
            label = str(classes[class_ids[i]])
            texts.append([x,label])
            #kasih warna
            color = colors[i]
            #cv2.rectangle(img,(x,y),(x+w,y+h),color,2) #membuat kotak pada gambar yang terdeteksi
            #cv2.putText(img,label,(x,y + 30),font,2,color,3) #membuat text pada gambar yang terdeteksi
            cropped_image = rawImg[y:y+h,x:x+w]
            cropped_image = rawImg[y*scaler:(y+h)*scaler,x*scaler:(x+w)*scaler] # Slicing to crop the image
    texts.sort()

    textsJoin =""
    
    for i in range (len(texts)):
        textsJoin = textsJoin + texts[i][1]
    
    if not textsJoin:
        print("Gambar tidak terdeteksi!")
        return [[],[],[]]
    else:
        return [cropped_image, rawImg, textsJoin]  
