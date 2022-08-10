import face_recognition as fr
import cv2

MODEL ="hog" #could be either "hog" less accurate than its "cnn" counterpart but faster

def findEncoding(img,scaler=1):
    imgResize = cv2.resize(img, None, fx = 1/scaler, fy = 1/scaler) #uncoment kalao mau di resize
    facesCurFrame = fr.face_locations(imgResize,model=MODEL,number_of_times_to_upsample=2)
    print(facesCurFrame)
    if len(facesCurFrame)==0:
        return[]
    encode = fr.face_encodings(imgResize)[0]
    (y1,x2,y2,x1) = facesCurFrame[0]
    cropped_image = img[(y1*scaler):(y2*scaler),(x1*scaler):(x2*scaler)]
    return [encode,cropped_image]

def compareImages(encodeDisimpan,encodeBaru,tolerance=0.4):
    results = fr.compare_faces([encodeDisimpan],encodeBaru,tolerance)
    faceDis = fr.face_distance([encodeDisimpan],encodeBaru)
    return [results,faceDis]

