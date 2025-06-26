from storages.backends.s3boto3 import S3Boto3Storage
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class ProfilePictureStorage(S3Boto3Storage):
    location = 'profile_pictures'
    default_acl = 'public-read'
    file_overwrite = False

class SubirArchivo(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    archivo = models.FileField(
        upload_to='uploads/',
        storage=ProfilePictureStorage(),  # Instancia, no clase
        blank=True,
        null=True
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.titulo}"

class Monitoreo(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    atencion = models.IntegerField()
    somnolencia = models.IntegerField()
    distraccion = models.IntegerField()
    fecha = models.DateTimeField()

    def __str__(self):
        return f"{self.usuario} - {self.fecha}"




class ReporteHistorico(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    atentos = models.IntegerField(default=0)
    somnolientos = models.IntegerField(default=0)
    distraidos = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reporte {self.timestamp} - {self.usuario.username}"