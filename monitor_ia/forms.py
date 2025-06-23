# monitor_ia/forms.py

from django import forms
from .models import SubirArchivo

class ArchivoUploadForm(forms.ModelForm):
    class Meta:
        model = SubirArchivo
        fields = ['titulo', 'archivo']

    def clean_archivo(self):
        archivo = self.cleaned_data['archivo']
        ext = archivo.name.lower().split('.')[-1]
        if ext not in ['mp4', 'jpg', 'jpeg', 'png']:
            raise forms.ValidationError("Formato no permitido. Solo .mp4, .jpg, .jpeg, .png")
        return archivo
