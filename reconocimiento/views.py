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
