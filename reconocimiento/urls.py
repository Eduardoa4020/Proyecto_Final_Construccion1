from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('monitor/', views.monitor, name='monitor'),
    path('monitor_oflime/', views.monitor_oflime, name='monitor_oflime'),
    path('reportes/', views.reportes, name='reportes'),
    path('usuarios/', views.usuarios, name='usuarios'),
    path('configuracion/', views.configuracion, name='configuracion'),
    
]