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
from Authentication.models import CustomUser as User
from django.contrib import messages
from .models import Usuario
from .forms import UsuarioForm  # Asegúrate de importar el formulario

def gestion_usuarios_view(request):
    usuarios = Usuario.objects.all()
    return render(request, 'core/reconocimiento/usuarios.html', {'usuarios': usuarios})

def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.usuario_padre = request.user
            usuario.save()

            messages.success(request, "El usuario se ha creado exitosamente.")
            return redirect('gestion_usuarios')
        else:
            messages.error(request, "Error al crear el usuario. Por favor, corrige los errores.")
            return redirect('gestion_usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'core/reconocimiento/crear_usuario.html', {'form': form})

def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    if request.method == 'POST':
        usuario.nombre = request.POST.get('nombre')
        usuario.correo = request.POST.get('correo')
        usuario.rol = request.POST.get('rol')
        usuario.save()
        return redirect('gestion_usuarios')
    return render(request, 'core/reconocimiento/editar_usuario.html', {'usuario': usuario})

def eliminar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    usuario.delete()
    return redirect('gestion_usuarios')

def cambiar_clave_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    # Aquí puedes agregar lógica para cambiar clave (si lo implementas)
    return render(request, 'core/reconocimiento/cambiar_clave.html', {'usuario': usuario})


def configuracion_view(request):
    return render(request, 'configuracion.html')