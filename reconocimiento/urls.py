from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('monitor/', views.monitor, name='monitor'),
    path('monitor_oflime/', views.monitor_oflime, name='monitor_oflime'),
    path('reportes/', views.reportes, name='reportes'),
    path('usuarios/', views.usuarios, name='usuarios'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/<int:id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/<int:id>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/<int:id>/cambiar-clave/', views.cambiar_clave_usuario, name='cambiar_clave_usuario'),


]