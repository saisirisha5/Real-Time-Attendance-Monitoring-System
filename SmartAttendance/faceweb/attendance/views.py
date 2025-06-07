from django.shortcuts import render, redirect
from .forms import FaceForm
from .firebase_config import db
from django.conf import settings
import os

def index(request):
    return render(request, 'index.html')

def view_attendance(request):
    records = db.collection('attendance').stream()
    all_data = [r.to_dict() for r in records]

    # Get each student's latest attendance timestamp
    latest_attendance = {}
    for record in all_data:
        name = record.get('name')
        timestamp = record.get('timestamp')
        if name:
            if name not in latest_attendance or timestamp > latest_attendance[name]:
                latest_attendance[name] = timestamp

    students = [{'name': name, 'last_timestamp': ts} for name, ts in latest_attendance.items()]
    return render(request, 'view_attendance.html', {'students': students})

def student_detail(request, name):
    records = db.collection('attendance').where('name', '==', name).stream()
    attendance_history = [r.to_dict() for r in records]
    attendance_history.sort(key=lambda x: x['timestamp'], reverse=True)
    return render(request, 'student_detail.html', {'name': name, 'history': attendance_history})

def add_face(request):
    if request.method == 'POST':
        form = FaceForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            image = form.cleaned_data['image']
            save_path = os.path.join(settings.MEDIA_ROOT, image.name)
            with open(save_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            db.collection('face_data').add({
                'name': name,
                'image_name': image.name
            })
            return redirect('home')
    else:
        form = FaceForm()
    return render(request, 'add_face.html', {'form': form})
