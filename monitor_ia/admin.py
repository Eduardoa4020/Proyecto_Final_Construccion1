from django.contrib import admin
from .models import SubirArchivo

@admin.register(SubirArchivo)
class SubirArchivoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'titulo', 'archivo', 'fecha_subida')
    search_fields = ('titulo', 'usuario__username')
    list_filter = ('fecha_subida',)
