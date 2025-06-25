# reconocimiento/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, 'core/reconocimiento/dashboard.html')

@login_required
def monitor(request):
    return render(request, 'core/reconocimiento/monitor.html')

@login_required
def monitor_oflime(request):
    return render(request, 'core/reconocimiento/monitor_oflime.html')

@login_required
def reportes(request):
    return render(request, 'core/reconocimiento/reportes.html')

@login_required
def usuarios(request):
    return render(request, 'core/reconocimiento/usuarios.html')

@login_required
def configuracion(request):
    return render(request, 'core/reconocimiento/configuracion.html')

# reconocimiento/views.py
from monitor_ia.models import Monitoreo  # importa el modelo correcto

def reportes_historicos(request):
    queryset = Monitoreo.objects.all()

    desde = request.GET.get("desde")
    hasta = request.GET.get("hasta")
    nombre = request.GET.get("nombre")

    if desde:
        queryset = queryset.filter(fecha__gte=desde)
    if hasta:
        queryset = queryset.filter(fecha__lte=hasta)
    if nombre:
        queryset = queryset.filter(nombre_clase__icontains=nombre)

    return render(request, 'core/reconocimiento/reportes.html', {
        'reportes': queryset,
        'request': request  # para que funcione {{ request.GET... }}
    })

from django.shortcuts import render, redirect, get_object_or_404
from .models import Usuario
from django.utils import timezone


def gestion_usuarios_view(request):
    usuarios = Usuario.objects.all()
    return render(request, 'gestion_usuarios.html', {'usuarios': usuarios})

def crear_usuario(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        correo = request.POST['correo']
        rol = request.POST['rol']
        ultimo_acceso = timezone.now().strftime("%d/%m/%Y %H:%M")

        Usuario.objects.create(
            nombre=nombre,
            correo=correo,
            rol=rol,
            estado='Activo',  # Se asigna automáticamente
            ultimo_acceso=ultimo_acceso
        )
        return redirect('gestion_usuarios')
    return render(request, 'crear_usuario.html')

def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    # Lógica para editar usuario (puedes mejorarla después)
    return render(request, 'editar_usuario.html', {'usuario': usuario})

def eliminar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    usuario.delete()
    return redirect('gestion_usuarios')

def cambiar_clave_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    # Lógica para cambiar clave (puedes implementarla luego)
    return render(request, 'cambiar_clave.html', {'usuario': usuario})
