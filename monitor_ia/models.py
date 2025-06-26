from storages.backends.s3boto3 import S3Boto3Storage
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Storage class for profile pictures using S3
class ProfilePictureStorage(S3Boto3Storage):
    location = 'profile_pictures'
    default_acl = 'public-read'
    file_overwrite = False

# Model for uploading files (e.g., documents or profile pictures)
class SubirArchivo(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    archivo = models.FileField(
        upload_to='uploads/',
        storage=ProfilePictureStorage(),  # Instancia de la clase, no la clase
        blank=True,
        null=True
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.titulo}"

# Model to store monitoring results (e.g., attention, distraction, etc.)
class Monitoreo(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    atencion = models.IntegerField()  # Attention level detected by AI (percentage, for example)
    somnolencia = models.IntegerField()  # Sleepiness level detected by AI
    distraccion = models.IntegerField()  # Distraction level detected by AI
    fecha = models.DateTimeField()  # The date and time of the monitoring session

    def __str__(self):
        return f"{self.usuario} - {self.fecha}"
