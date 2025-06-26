from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    rol = models.CharField(max_length=50, choices=[('Administrador', 'Administrador'), ('Docente', 'Docente'), ('Observador', 'Observador')])

    def __str__(self):
        return self.nombre

