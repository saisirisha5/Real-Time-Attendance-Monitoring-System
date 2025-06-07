import firebase_admin
from firebase_admin import credentials, firestore
from django.shortcuts import render
cred = credentials.Certificate("<firebasekey>-json file")
firebase_admin.initialize_app(cred)
db = firestore.client()
def student_list(request):
    docs = db.collection('attendance').stream()

    data = {}
    for doc in docs:
        record = doc.to_dict()
        name = record.get("name")
        timestamp = record.get("timestamp")
        if name in data:
            if timestamp > data[name]:
                data[name] = timestamp
        else:
            data[name] = timestamp

    students = [{'name': name, 'last_timestamp': ts} for name, ts in data.items()]
    return render(request, 'view_attendance.html', {'students': students})