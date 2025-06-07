from django import forms

class FaceForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100)
    image = forms.ImageField(label='Upload Face Image')
