from django.contrib.auth.models import User
from django.db import models


class Partida(models.Model):
    """
    > Partidas del juego
    Cada vez que una partida termina, se envia el resultado al backend de Django con una
    peticion HTTP, y este registro se guarda en la db
    """

    NIVEL_BASICO = 'basico'
    NIVEL_MEDIO = 'medio'
    NIVEL_AVANZADO = 'avanzado'

    NIVEL_CHOICES = [
        (NIVEL_BASICO, 'Básico'),
        (NIVEL_MEDIO, 'Medio'),
        (NIVEL_AVANZADO, 'Avanzado'),
    ]

    RESULTADO_VICTORIA = 'victoria'
    RESULTADO_DERROTA = 'derrota'

    RESULTADO_CHOICES = [
        (RESULTADO_VICTORIA, 'Victoria'),
        (RESULTADO_DERROTA, 'Derrota'),
    ]

    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='partidas'
    )
    nivel = models.CharField(max_length=10, choices=NIVEL_CHOICES)
    resultado = models.CharField(max_length=10, choices=RESULTADO_CHOICES)
    intentos_permitidos = models.PositiveSmallIntegerField()
    intentos_usados = models.PositiveSmallIntegerField()
    tiempo_limite = models.PositiveSmallIntegerField(help_text='Segundos disponibles para la partida')
    tiempo_usado = models.FloatField(help_text='Segundos que tardó el jugador')
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Partida'
        verbose_name_plural = 'Partidas'

    def __str__(self):
        return f'{self.usuario.username} - {self.get_nivel_display()} - {self.get_resultado_display()}'
