import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Avg, Count, Q
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static
from django.views.decorators.http import require_POST

from .constants import NIVELES, TAMANO_TABLERO, SIMBOLOS_CARTAS
from .forms import RegistroForm
from .models import Partida


# ---------------------------------------------------------------------------
# Autenticación
# ---------------------------------------------------------------------------

def registro_view(request):
    """Pantalla de registro: usuario, correo y contraseña."""
    if request.user.is_authenticated:
        return redirect('seleccionar_nivel')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, f'¡Bienvenido, {usuario.username}! Tu cuenta fue creada correctamente.')
            return redirect('seleccionar_nivel')
    else:
        form = RegistroForm()

    return render(request, 'memory_game/registro.html', {'form': form})


def login_view(request):
    """Pantalla de login: verifica credenciales e inicia sesión."""
    if request.user.is_authenticated:
        return redirect('seleccionar_nivel')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            return redirect('seleccionar_nivel')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()

    return render(request, 'memory_game/login.html', {'form': form})


@login_required
def logout_view(request):
    """Cierra la sesión y regresa a la pantalla de login."""
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('login')


# ---------------------------------------------------------------------------
# Flujo del juego
# ---------------------------------------------------------------------------

@login_required
def seleccionar_nivel(request):
    """Pantalla de selección de nivel de dificultad."""
    niveles = [
        {'clave': clave, **datos} for clave, datos in NIVELES.items()
    ]
    return render(request, 'memory_game/dificultad.html', {'niveles': niveles})


@login_required
def jugar_view(request, nivel):
    """Pantalla del tablero de juego para el nivel seleccionado."""
    config = NIVELES.get(nivel)
    if config is None:
        raise Http404('Nivel de dificultad no válido')

    contexto = {
        'nivel_clave': nivel,
        'nivel_nombre': config['nombre'],
        'intentos': config['intentos'],
        'tiempo': config['tiempo'],
        'tamano_tablero': TAMANO_TABLERO,
        'simbolos': json.dumps(SIMBOLOS_CARTAS),
        'url_imagenes': static('memory_game/img/'),
    }
    return render(request, 'memory_game/juego.html', contexto)


@login_required
@require_POST
def guardar_partida(request):
    """
    Endpoint llamado por JavaScript (fetch) al terminar una partida.

    El navegador ejecuta toda la lógica de emparejar cartas, contar
    intentos y controlar el tiempo (procesamiento en el cliente). Cuando
    la partida termina, el resultado final se envía aquí mediante una
    petición HTTP POST para quedar persistido en la base de datos.
    """
    try:
        datos = json.loads(request.body)
        nivel = datos['nivel']
        resultado = datos['resultado']
        intentos_usados = int(datos['intentos_usados'])
        tiempo_usado = float(datos['tiempo_usado'])
    except (KeyError, ValueError, json.JSONDecodeError):
        return JsonResponse({'ok': False, 'error': 'Datos inválidos'}, status=400)

    config = NIVELES.get(nivel)
    if config is None or resultado not in (Partida.RESULTADO_VICTORIA, Partida.RESULTADO_DERROTA):
        return JsonResponse({'ok': False, 'error': 'Nivel o resultado inválido'}, status=400)

    Partida.objects.create(
        usuario=request.user,
        nivel=nivel,
        resultado=resultado,
        intentos_permitidos=config['intentos'],
        intentos_usados=min(intentos_usados, config['intentos']),
        tiempo_limite=config['tiempo'],
        tiempo_usado=round(tiempo_usado, 2),
    )

    estadisticas = calcular_estadisticas(request.user)
    return JsonResponse({'ok': True, 'estadisticas': estadisticas})


def calcular_estadisticas(usuario):
    """
    Calcula las estadísticas del jugador a partir de su historial de
    partidas guardado en la base de datos: total de victorias, derrotas,
    partidas jugadas, promedio de tiempo y nivel más jugado.
    """
    partidas = Partida.objects.filter(usuario=usuario)
    total_partidas = partidas.count()
    total_victorias = partidas.filter(resultado=Partida.RESULTADO_VICTORIA).count()
    total_derrotas = partidas.filter(resultado=Partida.RESULTADO_DERROTA).count()
    promedio_tiempo = partidas.aggregate(promedio=Avg('tiempo_usado'))['promedio'] or 0

    nivel_mas_jugado = '—'
    if total_partidas:
        conteo_por_nivel = (
            partidas.values('nivel')
            .annotate(total=Count('id'))
            .order_by('-total')
            .first()
        )
        if conteo_por_nivel:
            nivel_mas_jugado = NIVELES[conteo_por_nivel['nivel']]['nombre']

    return {
        'total_partidas': total_partidas,
        'total_victorias': total_victorias,
        'total_derrotas': total_derrotas,
        'promedio_tiempo': round(promedio_tiempo, 1),
        'nivel_mas_jugado': nivel_mas_jugado,
    }


# ---------------------------------------------------------------------------
# Perfil y estadísticas
# ---------------------------------------------------------------------------

@login_required
def perfil_view(request):
    """
    Pantalla de perfil: estadísticas agregadas + historial completo +
    evolución de las estadísticas a lo largo del tiempo (para el gráfico).
    """
    partidas = Partida.objects.filter(usuario=request.user)
    estadisticas = calcular_estadisticas(request.user)
    partidas_cronologicas = partidas.order_by('fecha')
    evolucion = {
        'fechas': [p.fecha.strftime('%d/%m %H:%M') for p in partidas_cronologicas],
        'resultados': [1 if p.resultado == Partida.RESULTADO_VICTORIA else 0 for p in partidas_cronologicas],
        'tiempos': [p.tiempo_usado for p in partidas_cronologicas],
    }

    contexto = {
        **estadisticas,
        'historial': partidas[:30],  # ultimas 30 partidas
        'evolucion_json': json.dumps(evolucion),
    }
    return render(request, 'memory_game/perfil.html', contexto)
