from django.contrib import admin
from .models import Monitoreo

@admin.register(Monitoreo)
class MonitoreoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'atencion', 'somnolencia', 'distraccion', 'fecha')
    list_filter = ('usuario', 'fecha')
    search_fields = ('usuario__username',)
    ordering = ('-fecha',)
