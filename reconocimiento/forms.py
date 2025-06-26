# reconocimiento/forms.py
from django import forms
from monitor_ia.models import SubirArchivo
class ArchivoUploadForm(forms.ModelForm):
    class Meta:
        model = SubirArchivo
        fields = ['archivo']  # Ajusta según los campos de tu modelo