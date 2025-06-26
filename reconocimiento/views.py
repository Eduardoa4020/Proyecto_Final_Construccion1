# reconocimiento/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from monitor_ia.models import Monitoreo
from django.views.decorators.csrf import csrf_exempt


def dashboard(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Debes iniciar sesión para acceder a los módulos.")
        return redirect('home')
    return render(request, 'core/reconocimiento/dashboard.html')

def monitor(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Debes iniciar sesión para acceder a los módulos.")
        return redirect('home')
    return render(request, 'core/reconocimiento/monitor.html')

def reportes(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Debes iniciar sesión para acceder a los módulos.")
        return redirect('home')
    return render(request, 'core/reconocimiento/reportes.html')

def usuarios(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Debes iniciar sesión para acceder a los módulos.")
        return redirect('home')
    return render(request, 'core/reconocimiento/usuarios.html')

def configuracion(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Debes iniciar sesión para acceder a los módulos.")
        return redirect('home')
    return render(request, 'core/reconocimiento/configuracion.html')

def configuracion_view(request):
    return render(request, 'configuracion.html')


