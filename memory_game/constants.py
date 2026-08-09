
# Config de los niveles de dificultad

TAMANO_TABLERO = 4  # 4x4
TOTAL_PARES = (TAMANO_TABLERO * TAMANO_TABLERO) // 2  # 8 pares

NIVELES = {
    'basico': {
        'nombre': 'Básico',
        'intentos': 6,
        'tiempo': 60,
    },
    'medio': {
        'nombre': 'Medio',
        'intentos': 4,
        'tiempo': 45,
    },
    'avanzado': {
        'nombre': 'Avanzado',
        'intentos': 2,
        'tiempo': 30,
    },
}

# iconos en las cartas
SIMBOLOS_CARTAS = [
    'iconoPacMan.png',
    'iconoBlinky.png',
    'iconoPinky.png',
    'iconoInky.png',
    'iconoClyde.png',
    'iconoFantasmaDebil.png',
    'iconoCereza.png',
    'iconoNaranja.png',
]
