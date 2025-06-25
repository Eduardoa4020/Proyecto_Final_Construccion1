
# Create your models here.
from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    rol = models.CharField(max_length=50, choices=[('Administrador', 'Administrador'), ('Docente', 'Docente'), ('Observador', 'Observador')])
    estado = models.CharField(max_length=10, choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')])
    ultimo_acceso = models.CharField(max_length=50)  # o DateTimeField si lo manejas con formato

    def __str__(self):
        return self.nombre
    