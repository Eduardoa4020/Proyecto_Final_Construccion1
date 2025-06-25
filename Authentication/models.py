from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

class CustomUser(AbstractUser):
    GENERO_OPCIONES = [
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
        ('Otro', 'Otro'),
    ]

    email = models.EmailField(unique=True)
    genero = models.CharField(max_length=20, choices=GENERO_OPCIONES)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)  
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
User = get_user_model()

class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)

    def is_valid(self):
        return timezone.now() - self.created_at < timezone.timedelta(minutes=10)

    def __str__(self):
        return f"Código {self.code} para {self.user.email}"