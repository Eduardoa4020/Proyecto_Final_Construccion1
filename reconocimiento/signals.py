from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils.timezone import now
from .models import Usuario

@receiver(user_logged_in)
def marcar_usuario_activo(sender, request, user, **kwargs):
    try:
        usuario = Usuario.objects.get(correo=user.email)
        usuario.estado = 'Activo'
        usuario.ultimo_acceso = now().strftime('%d/%m/%Y %H:%M')
        usuario.save()
    except Usuario.DoesNotExist:
        pass

@receiver(user_logged_out)
def marcar_usuario_inactivo(sender, request, user, **kwargs):
    try:
        usuario = Usuario.objects.get(correo=user.email)
        usuario.estado = 'Inactivo'
        usuario.save()
    except Usuario.DoesNotExist:
        pass
