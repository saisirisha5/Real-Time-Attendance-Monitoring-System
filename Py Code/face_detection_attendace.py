import pandas as pd
import cv2
import urllib.request
import numpy as np
import os
from datetime import datetime
import face_recognition
import firebase_admin  
from firebase_admin import credentials, firestore

cred = credentials.Certificate(r"<firebase-key-in-json>")
firebase_admin.initialize_app(cred)
db = firestore.client()

path = r'<path-to-image-folder>'
url = 'http://<ip-address to access the camera>/cam-hi.jpg'

# Attendance file setup
if 'Attendance.csv' in os.listdir(os.path.join(os.getcwd(), 'Attendance')):  
    print("Attendance file exists, removing it.")
    os.remove("Attendance.csv")
else:
    df = pd.DataFrame(list())
    df.to_csv("Attendance.csv")

images = []
classNames = []
myList = os.listdir(path)
print(myList)

for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

def markAttendance(name):
    now = datetime.now()
    dtString = now.strftime('%Y-%m-%d %H:%M:%S')

    with open("Attendance.csv", 'r+') as f:
        myDataList = f.readlines()
        nameList = [line.split(',')[0] for line in myDataList]
        if name not in nameList:
            f.writelines(f'\n{name},{dtString}')
            print(f"Local Attendance marked for {name} at {dtString}")
            
            # Firestore entry
            doc_ref = db.collection('attendance').document()
            doc_ref.set({
                'name': name,
                'timestamp': dtString
            })
            print(f"Uploaded {name} to Firestore")

encodeListKnown = findEncodings(images)
print('Encoding Complete')

# Commented out webcam line because you're using ESP32 stream
# cap = cv2.VideoCapture(0)

while True:
    img_resp = urllib.request.urlopen(url)
    imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
    img = cv2.imdecode(imgnp, -1)

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            markAttendance(name)

            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow('Webcam', img)
    key = cv2.waitKey(5)
    if key == ord('q'):
        break

cv2.destroyAllWindows()
