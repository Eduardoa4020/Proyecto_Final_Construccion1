from django.urls import path
from . import views

urlpatterns = [
    path('analizar-imagen/', views.analizar_frame, name='analizar_frame'),  # Ruta para analizar imágenes
    path('subir-archivos/', views.subir_archivos, name='subir_archivos'),  # Ruta para subir archivos
    path('dashboard/', views.dashboard, name='dashboard'),  # Ruta para mostrar el dashboard
]
