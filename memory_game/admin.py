from django.contrib import admin

from .models import Partida


@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = (
        'usuario', 'nivel', 'resultado', 'intentos_usados',
        'intentos_permitidos', 'tiempo_usado', 'tiempo_limite', 'fecha',
    )
    list_filter = ('nivel', 'resultado')
    search_fields = ('usuario__username',)
