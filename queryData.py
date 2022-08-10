import mysql.connector
from datetime import datetime
import pickle
from encodingWajah import findEncoding
import cv2

# INSERT PLAT NOMOR
def insertPlat(plat):
    con = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "kemal123",
        db = 'dbparkir'
        )
    tabel = con.cursor()
    
    sql = "INSERT IGNORE INTO LicensePlate (platNomor) VALUES (%s)"
    data = (plat,)
    tabel.execute(sql,data)
    
    con.commit()
    
    
def insertDatabase(plat,encodeWajah):
    con = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "kemal123",
        db = 'dbparkir',
        )
    face_pickled_data = pickle.dumps(encodeWajah)
    
    tabel = con.cursor()
    sql = "INSERT INTO ParkingInformation(encodeWajah , platID , waktuMasuk , status) VALUES(%s,(SELECT id FROM LicensePlate WHERE platNomor = %s),%s, %s);"
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = (face_pickled_data,plat,now,1)
    tabel.execute(sql,data)
    con.commit()
    
def readData(plat):
    con = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "kemal123",
        db = 'dbparkir'
        )
    tabel = con.cursor()
    
    sql = "SELECT platID FROM ParkingInformation WHERE platID=(SELECT id FROM LicensePlate WHERE platNomor = (%s)) AND status = 1"
    data = (plat,)
    tabel.execute(sql,data)
    myresult = tabel.fetchall()
    y = len(myresult)
    return y

def readDataIdParkir(plat):
    con = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "kemal123",
        db = 'dbparkir'
        )

    tabel = con.cursor()
    sql = "SELECT idParkir FROM ParkingInformation WHERE platID=(SELECT id FROM LicensePlate WHERE platNomor = (%s)) AND status = 1"
    data = (plat,)
    tabel.execute(sql,data)
    myresult = tabel.fetchall()
    return myresult

def exitPlate(plat):
    con = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "kemal123",
        db = 'dbparkir'
        )
    tabel = con.cursor()
    
    sql = "SELECT idParkir, encodeWajah, facePath FROM ParkingInformation WHERE platID=(SELECT id FROM LicensePlate WHERE platNomor = (%s)) AND status = 1"
    data = (plat,)
    tabel.execute(sql,data)
    
    myresult = tabel.fetchall()
    
    con.commit()
    return myresult

def insertTimeOut(idParkir):
    con = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "kemal123",
        db = 'dbparkir'
        )           
    tabel = con.cursor()
    
    sql = "UPDATE ParkingInformation SET waktuKeluar = %s, status = 0 WHERE idParkir = %s AND status = 1"
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = (now,idParkir)
    tabel.execute(sql,data)
        
    con.commit()

def updatePath(img_name_rawImg,img_name_faceImg,idParkir):
    con = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "kemal123",
        db = 'dbparkir'
        )           
    tabel = con.cursor()
    
    sql = "UPDATE ParkingInformation SET rawPath = %s, facePath = %s WHERE idParkir = %s"
    data = (img_name_rawImg,img_name_faceImg,idParkir)
    tabel.execute(sql,data)
    con.commit()

def mendaftarParkir(karakterPlat,imageRaw,gambarPlatNomor,scaler=1):
    status = readData(karakterPlat)
    if status == 0: #jika status 0 maka data belom ada
        #encoding wajah
        hasilEncodeCrop = findEncoding(imageRaw,scaler) #hasil ecode itu 
        if not hasilEncodeCrop:
            print("Wajah tidak terdeteksi")
            return []
        else:
            print("Wajah terdeteksi")
        
        encodeWajah,croppedFace = hasilEncodeCrop
        #simpan ke database
        insertDatabase(karakterPlat, encodeWajah)
        print("Berhasil insert database")
        
        #read data
        [(idParkir)] =readDataIdParkir(karakterPlat)
        idParkir = idParkir[0]
       
        #susun nama
        img_name_rawImg = "images/record/raw/rawImg_{}.png".format(idParkir)
        #simpan raw img
        cv2.imwrite(img_name_rawImg, imageRaw)
        
        #susun nama
        img_name_faceImg = "images/record/face/faceImg_{}.png".format(idParkir)
        
        # simpan face
        cv2.imwrite(img_name_faceImg, croppedFace)
        
        #susun nama
        img_name_platImg = "images/record/plat/platImg_{}.png".format(idParkir)
        
        # simpan plat nomor
        cv2.imwrite(img_name_platImg, gambarPlatNomor)
        
        updatePath(img_name_rawImg,img_name_faceImg,idParkir)
        
        return [status,croppedFace,img_name_rawImg,img_name_faceImg,img_name_platImg]
    else:
        #Jika data sudah pernah terekam
        return [status,0,0,0,0]
