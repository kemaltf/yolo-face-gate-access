### IMPORT PACKAGE ###
import tkinter as tk
import cv2, sys, timeit, gc, time, pickle
from gstStreamerbykemal import gstreamer_pipeline
from PIL import Image, ImageTk
from tkinter import ttk
from pymata4 import pymata4
from datetime import datetime
from deteksiplat import deteksiplat
from pengenalanplat import pengenalanplat
from queryData import insertDatabase, insertPlat, readData, mendaftarParkir,exitPlate, insertTimeOut
import numpy as np
from imgpreprocesingStep import correctionF,grayF,blurF,denoiseF,gammF,gammF,histF,threshF
from resizeImg import image_resize
from convertImage import piltoCv, cvtoPil
from fpsDisplay import display_frames_per_second
from encodingWajah import findEncoding, compareImages
### FUNGSI-FUNGSI ###

def servo():
	# untuk menghemat proses pemrosesan package arduino
	# tidak dapat dipisah karena kita akan menggunakan
	# dua program secara bergantian, yaitu program untuk jarak
	#dan program untuk gerbang
	
	#messageBar("Palang terbuka, silahkan masuk")
 
	board.servo_write(servoPin, 0) # Atur servo 0 derajat (terbuka)
	time.sleep(1)
    
	while True:
		jarakBenda = board.sonar_read(triggerPin) #ambil jarak kendaraan

		if jarakBenda[0] > 30: #jika jarak benda lebih dari 200cm maka kendaraan tersebut telah lewat
			time.sleep(1)
			board.servo_write(servoPin, 90)
			break
		#messageBar(1,"Silakan masuk, gerbang akan ditutup setelah jarak 200cm, jarak Anda saat ini: {} cm".format(jarakBenda))

def jarak():
	jarakBenda = board.sonar_read(triggerPin)
	return jarakBenda[0]

def messageBar(label,message=""):
	"""
	label = 1 => label 1
	label = 2 => label 2
	"""
	if label==1:
		processBar.set(message)
	if label==2:
		platResult.set(message)
	root.update_idletasks() #untuk update window
 
def imageBar(frame,img,widthsize):

	img = image_resize(img, width = widthsize)
	img = cvtoPil(img)
	if frame == 1:
		koreksiImgFrame.paste(img)
	if frame == 2:
		grayImgFrame.paste(img)
	if frame == 3:
		blurImgFrame.paste(img)
	if frame == 4:
		denoiseImgFrame.paste(img)
	if frame == 5:
		histImgFrame.paste(img)
	if frame == 6:
		gammaImgFrame.paste(img)
	if frame == 7:
		tresholdImgFrame.paste(img)
	if frame == 8:
		faceEntryImgFrame.paste(img)
	if frame == 9:
		faceExitImgFrame.paste(img)
	if frame == 0:
		photo.paste(img)
  
  
	root.update_idletasks() #untuk update window

def timecounting(waktuAwal):
	waktuAkhir = timeit.default_timer()
	timetotal = waktuAkhir - waktuAwal
	return timetotal

def update_frame():
	START_TIME = time.time()
 
	global image
	
	now = datetime.now().strftime('%Y-%m-%d %H:%M:%S') #format waktu
	TIMETXT.set(now) # mengatur waktu pada GUI
 
	# _, frame = cap.read() # Membaca input kamera
	ret, frame = videowebCam.read()
	if frame is not None: # jika kamera terbaca
		jarakBenda = jarak() #ditangkap keluaran berupa jarak dalam satuan cm.
		if jarakBenda < 5:
			tic = timeit.default_timer() # Waktu awal memulai suatu program
			messageBar(1,"Gambar sedang di proses")
			MODE=0 #MODE 0 adalah mode uji saat presentasi akan mereplace gambar kamera dengan gambar yang ada
			if MODE==0:
				pathImage = "/home/kemal/Downloads/AutomaticParkByKemal/images/gambar tes/uji gambar/driver 1/keluar_1.jfif"
				frame = cv2.imread(pathImage)
				imageBar(0,frame,1280)
    
			#DETEKSIPLAT#
			tic1 = timeit.default_timer() # Waktu untuk deteksi plat
			imgDeteksiPlat = deteksiplat(frame,4)
   
			#jika array isinya nol maka:
			if imgDeteksiPlat == []:
				messageBar(2,"Plat tidak terdeteksi. Mohon ulangi kembali")
				update_frame()	
    
			message = "Deteksi plat: {} s".format(timecounting(tic1))
			messageBar(1,message)
			print(message)
   
			#IMG PRE-RPOCESSIMG#
			tic2 = timeit.default_timer() # waktu untuk pemrosesan
			hasilPreprocessing=correctionF(imgDeteksiPlat)
			imageBar(1,hasilPreprocessing,270)
			hasilPreprocessing=grayF(hasilPreprocessing)
			imageBar(2,hasilPreprocessing,270)
			hasilPreprocessing=blurF(hasilPreprocessing)
			imageBar(3,hasilPreprocessing,270)
			hasilPreprocessing=denoiseF(hasilPreprocessing)
			imageBar(4,hasilPreprocessing,270)
			hasilPreprocessing=histF(hasilPreprocessing)
			imageBar(5,hasilPreprocessing,270)
			hasilPreprocessing=gammF(hasilPreprocessing)
			imageBar(6,hasilPreprocessing,270)
			hasilPreprocessing=threshF(hasilPreprocessing)
			imageBar(7,hasilPreprocessing,480)

			message="Pre-processing: {} s".format(timecounting(tic2))
			messageBar(1,message)
			print(message)
			
			#RECOGNITION#
			tic3 = timeit.default_timer() # waktu untuk pengenalan
			karakterplat = pengenalanplat(hasilPreprocessing,scaler=1)

			if len(karakterplat)==0:
				messageBar(1,"Plat tidak terbaca. Mohon ulangi kembali")
				update_frame()
			
			message="Karakter plat: {} s".format(timecounting(tic3))
			messageBar(1,message)
			print(message)
   
			messageBar(2,karakterplat)
			print(karakterplat)
   
			#CARI PLAT NOMOR DI DALAM DATABASE
			querydata = exitPlate(karakterplat)
			
			if not querydata:
				messageBar(2,"Data tidak ditemukan")
				print("Data tidak ditemukan")
				update_frame()
			

			[(idParkir, wajahPickled,facePath)] = querydata
   
			faceonEntryImg = cv2.imread(facePath)
			imageBar(8,faceonEntryImg,240)
			message="Nomor ID parkir Anda {}".format(idParkir)
			messageBar(2,message)
			print(message)
			encodeDisimpan = pickle.loads(wajahPickled)
			hasilEncodeCrop = findEncoding(frame,2)
   
			if not hasilEncodeCrop:
				print("Wajah tidak terdeteksi")
				update_frame()
			else:
				print("Wajah terdeteksi")
    
			encodeBaru,croppedFace = hasilEncodeCrop
			imageBar(9,croppedFace,240)
			results,faceDis=compareImages(encodeDisimpan, encodeBaru,0.8)
			print(results,faceDis)

			if results[0] == False:
				message="Wajah cocok gerbang terbuka!"
				messageBar(2,message)
				
				insertTimeOut(idParkir)
				servo()
			else:
				message="Wajah tidak cocok, ulangi kembali"
				messageBar(2,message)

		else:
			messageBar(1,"Posisi Anda saat ini: {} cm".format(jarakBenda))
			
		frame = cv2.flip(frame, 1)
		frame = display_frames_per_second(frame, START_TIME)
		image = cvtoPil(frame)
	else:
		print("mohon restart kamera menggunakan perintah: 'sudo service nvargus-daemon restart'")
	photo.paste(image)
	root.after(round(10), update_frame) #update displayed image after: round(1000/FPS) [in milliseconds]
 
### ARDUINO SETUP ###
triggerPin = 11
echoPin = 12
servoPin = 10
board= pymata4.Pymata4()
board.set_pin_mode_sonar(triggerPin, echoPin)
board.set_pin_mode_servo(servoPin)


### GUI SETUP ###
APP_WIDTH = 1920 #minimal width of the GUI
APP_HEIGHT = 1080 #minimal height of the gui
# cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
videowebCam = cv2.VideoCapture(0)
WIDTH  = 1280#int(cap.get(3)) #webcam's picture width
HEIGHT = 720#int(cap.get(4))#wabcam's picture height

root = tk.Tk() # start of GUI
root.title("Automatic Gate Parking By Kemal")
root.minsize(APP_WIDTH,APP_HEIGHT)
root["bg"]="#c6c6c6"

### GUI elements ###
#Jarak setiap widget 0.015
# image default
defaultImg = cv2.imread("/home/kemal/Downloads/AutomaticParkByKemal/images/app/licenseDefault.png")
defaultImg = image_resize(defaultImg, width = 270)
defaultImg = cvtoPil(defaultImg)


defaultImgwide = cv2.imread("/home/kemal/Downloads/AutomaticParkByKemal/images/app/licenseDefaultwide.png")
defaultImgwide = image_resize(defaultImgwide, width = 480)
defaultImgwide = cvtoPil(defaultImgwide)

defaultProfile = cv2.imread("/home/kemal/Downloads/AutomaticParkByKemal/images/app/profile.png")
defaultProfile = image_resize(defaultProfile, width = 240)
defaultProfile = cvtoPil(defaultProfile)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,bg="white")
canvas.place(relx=0.01,rely=0.305)

#KOREKSI FRAME
MESSAGE1 = tk.StringVar()
message = "Koreksi warna gambar"
MESSAGE1.set(message)
message_label1=tk.Label(root,textvariable=MESSAGE1, wraplength = "10c", bg="black", fg="white")
message_label1.place(relx=0.150,rely=0.02,relwidth=0.140,relheight=0.03,anchor="ne")
message_label1.config(font=(None, 11))
koreksiImgFrame = ImageTk.PhotoImage(defaultImg)

# Create a Label Widget to display the text or Image
correctionImg = tk.Label(root, image = koreksiImgFrame)
correctionImg.image = koreksiImgFrame
correctionImg.place(relx=0.150,rely=0.052,relwidth=0.140,relheight=0.25,anchor="ne")

#GRAY FRAME
MESSAGE2 = tk.StringVar()
messageGray = "Grays"
MESSAGE2.set(messageGray)
message_label2=tk.Label(root,textvariable=MESSAGE2, wraplength = "10c", bg="black", fg="white")
message_label2.place(relx=0.298,rely=0.02,relwidth=0.140,relheight=0.03,anchor="ne")
message_label2.config(font=(None, 11))
grayImgFrame = ImageTk.PhotoImage(defaultImg)

# Create a Label Widget to display the text or Image
grayImg = tk.Label(root, image = grayImgFrame)
grayImg.image = grayImgFrame
grayImg.place(relx=0.298,rely=0.052,relwidth=0.140,relheight=0.25,anchor="ne")

#BLUR FRAME
MESSAGE3 = tk.StringVar()
messageBlur = "Blur"
MESSAGE3.set(messageBlur)
message_label3=tk.Label(root,textvariable=MESSAGE3, wraplength = "10c", bg="black", fg="white")
message_label3.place(relx=0.445,rely=0.02,relwidth=0.140,relheight=0.03,anchor="ne")
message_label3.config(font=(None, 11))
blurImgFrame = ImageTk.PhotoImage(defaultImg)

# Create a Label Widget to display the text or Image
blurImg = tk.Label(root, image = blurImgFrame)
blurImg.image = blurImgFrame
blurImg.place(relx=0.445,rely=0.052,relwidth=0.140,relheight=0.25,anchor="ne")

#DENOISE FRAME
MESSAGE4 = tk.StringVar()
messageDenoise = "Denoise"
MESSAGE4.set(messageDenoise)
message_label4=tk.Label(root,textvariable=MESSAGE4, wraplength = "10c", bg="black", fg="white")
message_label4.place(relx=0.593,rely=0.02,relwidth=0.140,relheight=0.03,anchor="ne")
message_label4.config(font=(None, 11))
denoiseImgFrame = ImageTk.PhotoImage(defaultImg)

# Create a Label Widget to display the text or Image
denoiseImg = tk.Label(root, image = denoiseImgFrame)
denoiseImg.image = denoiseImgFrame
denoiseImg.place(relx=0.593,rely=0.052,relwidth=0.140,relheight=0.25,anchor="ne")

#HIST FRAME
MESSAGE5 = tk.StringVar()
messageHist = "Histogram"
MESSAGE5.set(messageHist)
message_label5=tk.Label(root,textvariable=MESSAGE5, wraplength = "10c", bg="black", fg="white")
message_label5.place(relx=0.741,rely=0.02,relwidth=0.140,relheight=0.03,anchor="ne")
message_label5.config(font=(None, 11))
histImgFrame = ImageTk.PhotoImage(defaultImg)

# Create a Label Widget to display the text or Image
histImg = tk.Label(root, image = histImgFrame)
histImg.image = histImgFrame
histImg.place(relx=0.741,rely=0.052,relwidth=0.140,relheight=0.25,anchor="ne")

#GAMMA FRAME
MESSAGE6 = tk.StringVar()
messageGamma = "Gamma"
MESSAGE6.set(messageGamma)
message_label6=tk.Label(root,textvariable=MESSAGE6, wraplength = "10c", bg="black", fg="white")
message_label6.place(relx=0.889,rely=0.02,relwidth=0.140,relheight=0.03,anchor="ne")
message_label6.config(font=(None, 11))
gammaImgFrame = ImageTk.PhotoImage(defaultImg)

# Create a Label Widget to display the text or Image
gammaImg = tk.Label(root, image = gammaImgFrame)
gammaImg.image = gammaImgFrame
gammaImg.place(relx=0.889,rely=0.052,relwidth=0.140,relheight=0.25,anchor="ne")

#treshold
MESSAGE7 = tk.StringVar()
messageThresh = "THRESHOLD"
MESSAGE7.set(messageThresh)
message_label7=tk.Label(root,textvariable=MESSAGE7, wraplength = "10c", bg="black", fg="white")
message_label7.place(relx=0.93,rely=0.305,relwidth=0.25,relheight=0.03,anchor="ne")
message_label7.config(font=(None, 11))
tresholdImgFrame = ImageTk.PhotoImage(defaultImgwide)

# Create a Label Widget to display the text or Image
tresholdImg = tk.Label(root, image = tresholdImgFrame,bg="black")
tresholdImg.image = tresholdImgFrame
tresholdImg.place(relx=0.93,rely=0.335,relwidth=0.25,relheight=0.25,anchor="ne")

#face  entry
MESSAGE8 = tk.StringVar()
messageFaceEntry = "FACE ENTRY"
MESSAGE8.set(messageFaceEntry)
message_label8=tk.Label(root,textvariable=MESSAGE8, wraplength = "10c", bg="black", fg="white")
message_label8.place(relx=0.805,rely=0.6,relwidth=0.125,relheight=0.03,anchor="ne")
message_label8.config(font=(None, 11))
faceEntryImgFrame = ImageTk.PhotoImage(defaultProfile)

# Create a Label Widget to display the text or Image
imageFaceEntry = tk.Label(root, image = faceEntryImgFrame)
imageFaceEntry.image = faceEntryImgFrame
imageFaceEntry.place(relx=0.805,rely=0.63,relwidth=0.125,relheight=0.222,anchor="ne")

#face  exit
MESSAGE9 = tk.StringVar()
messageFaceExit = "FACE EXIT"
MESSAGE9.set(messageFaceExit)
message_label9=tk.Label(root,textvariable=MESSAGE9, wraplength = "10c", bg="black", fg="white")
message_label9.place(relx=0.93,rely=0.6,relwidth=0.125,relheight=0.03,anchor="ne")
message_label9.config(font=(None, 11))

# Create an object of tkinter ImageTk
faceExitImgFrame = ImageTk.PhotoImage(defaultProfile)

# Create a Label Widget to display the text or Image
imageFaceExit = tk.Label(root, image = faceExitImgFrame)
imageFaceExit.image = faceExitImgFrame
imageFaceExit.place(relx=0.93,rely=0.63,relwidth=0.125,relheight=0.222,anchor="ne")


TIMETXT = tk.StringVar()
timetext = "22/04/2022 19.00"
TIMETXT.set(timetext)
time_label=tk.Label(root,textvariable=TIMETXT, wraplength = "10c", bg="black", fg="white")
time_label.place(relx=0.93,rely=0.867,relwidth=0.25,relheight=0.03,anchor="ne")
time_label.config(font=(None, 14))

processBar = tk.StringVar()
messageProccess = "SELAMAT DATANG DI KEMAL PARK"
processBar.set(messageProccess)
process_label=tk.Label(root,textvariable=processBar, wraplength = "10c", bg="black", fg="white")
process_label.place(relx=0.93,rely=0.912,relwidth=0.25,relheight=0.03,anchor="ne")
process_label.config(font=(None, 14))

platResult = tk.StringVar()
messagePlat = "SELAMAT DATANG DI KEMAL PARK"
platResult.set(messagePlat)
platResult_label=tk.Label(root,textvariable=platResult, wraplength = "10c", bg="black", fg="white")
platResult_label.place(relx=0.93,rely=0.957,relwidth=0.25,relheight=0.03,anchor="ne")
platResult_label.config(font=(None, 14))

#####################
### Initial frame ###
#####################

# _, frame = cap.read()
ret, frame = videowebCam.read()
if frame is not None:
	image = cvtoPil(frame)
	photo = ImageTk.PhotoImage(image=image)
	canvas.create_image(WIDTH, HEIGHT, image=photo, anchor="se")
else:
    print("kamera sedang error, mohon restart atau clean GSTREAMER")

######################
### Start the show ###
######################

if __name__ == '__main__':
	update_frame()

#create the GUI.
root.mainloop()

#free memory
# cap.release()

videowebCam.release()
gc.collect()


