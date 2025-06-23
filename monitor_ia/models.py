from storages.backends.s3boto3 import S3Boto3Storage
from django.db import models
from django.conf import settings

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
    nombre_clase = models.CharField(max_length=100)
    fecha = models.DateField()
    nivel_atencion = models.IntegerField()

    def __str__(self):
        return f"{self.nombre_clase} - {self.fecha}"
