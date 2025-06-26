# reconocimiento/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from monitor_ia.models import Monitoreo
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import models

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
        'request': request
    })

def configuracion_view(request):
    return render(request, 'configuracion.html')