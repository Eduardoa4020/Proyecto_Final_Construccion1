from storages.backends.s3boto3 import S3Boto3Storage
from django.db import models

class ProfilePictureStorage(S3Boto3Storage):
    location = 'profile_pictures'
    default_acl = 'public-read'
    file_overwrite = False


class Subir_mp4(models.Model):
    titulo = models.CharField(max_length=255)
    video = models.FileField(upload_to='videos/',storage=ProfilePictureStorage,blank=True,null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
# monitor_ia/models.py
from django.db import models

class Monitoreo(models.Model):
    nombre_clase = models.CharField(max_length=100)
    fecha = models.DateField()
    nivel_atencion = models.IntegerField()

    def __str__(self):
        return f"{self.nombre_clase} - {self.fecha}"
