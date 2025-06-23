from django.urls import path
from . import views 

urlpatterns = [
    path('analizar-imagen/', views.analizar_frame, name='analizar_frame'),
    path('monitor/', views.subir_archivos, name='subir_archivos')
]