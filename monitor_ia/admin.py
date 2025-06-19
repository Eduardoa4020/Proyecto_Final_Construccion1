from django.contrib import admin
from .models import Subir_mp4

@admin.register(Subir_mp4)
class SubirMp4Admin(admin.ModelAdmin):
    list_display = ('titulo', 'video', 'fecha_subida')
    search_fields = ('titulo',)
    list_filter = ('fecha_subida',)
