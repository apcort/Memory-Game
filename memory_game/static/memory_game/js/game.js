/*
    LÓGICA DEL JUEGO: se ejecuta enteramente en el navegador
    (procesamiento del cliente: manejo de eventos, validaciones,
    animaciones y el temporizador). Al finalizar la partida, el
    resultado se envía al backend Django mediante fetch (petición HTTP)
    para guardarlo en la base de datos.
*/

(function () {
    'use strict';

    // --- Estado del juego 
    let cartasVolteadas = [];
    let paresEncontrados = 0;
    let intentosUsados = 0;
    let tiempoRestante = CONFIG_JUEGO.tiempoLimite;
    let tiempoInicio = null;
    let temporizador = null;
    let bloqueado = false;
    let juegoTerminado = false;

    const tablero = document.getElementById('tablero');
    const elIntentos = document.getElementById('intentos-restantes');
    const elTiempo = document.getElementById('tiempo-restante');
    const elPares = document.getElementById('pares-encontrados');
    const modal = document.getElementById('modal-resultado');
    const modalTitulo = document.getElementById('modal-titulo');
    const modalDetalle = document.getElementById('modal-detalle');

    const sonidoFlip = document.getElementById('sonido-flip');
    const sonidoMatch = document.getElementById('sonido-match');
    const sonidoVictoria = document.getElementById('sonido-victoria');
    const sonidoDerrota = document.getElementById('sonido-derrota');
    const musicaFondo = document.getElementById('musica-fondo');

    function reproducir(elementoAudio) {
        if (!elementoAudio) return;
        elementoAudio.currentTime = 0;
        elementoAudio.play().catch(() => {
        });
    }

    // --- tablero 
    function barajar(array) {
        const copia = [...array];
        for (let i = copia.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [copia[i], copia[j]] = [copia[j], copia[i]];
        }
        return copia;
    }

    function construirTablero() {
        const totalPares = (CONFIG_JUEGO.tamanoTablero * CONFIG_JUEGO.tamanoTablero) / 2;
        const simbolosElegidos = CONFIG_JUEGO.simbolos.slice(0, totalPares);
        const valores = barajar([...simbolosElegidos, ...simbolosElegidos]);

        tablero.innerHTML = '';
        valores.forEach((simbolo, indice) => {
            const carta = document.createElement('div');
            carta.className = 'carta';
            carta.dataset.valor = simbolo;
            carta.dataset.indice = indice;
            carta.innerHTML = `
                <div class="carta-interior">
                    <div class="carta-cara carta-dorso"><span class="punto-dorso"></span></div>
                    <div class="carta-cara carta-frontal"><img src="${CONFIG_JUEGO.urlImagenes}${simbolo}" alt="carta" class="carta-imagen"></div>
                </div>`;
            carta.addEventListener('click', () => manejarClicCarta(carta));
            tablero.appendChild(carta);
        });
    }

    // --- Interacción del jugador 
    function manejarClicCarta(carta) {
        if (bloqueado || juegoTerminado) return;
        if (carta.classList.contains('volteada') || carta.classList.contains('emparejada')) return;
        if (cartasVolteadas.length === 2) return;

        if (tiempoInicio === null) {
            iniciarTemporizador();
        }

        carta.classList.add('volteada');
        reproducir(sonidoFlip);
        cartasVolteadas.push(carta);

        if (cartasVolteadas.length === 2) {
            bloqueado = true;
            setTimeout(evaluarPar, 700);
        }
    }

    function evaluarPar() {
        const [carta1, carta2] = cartasVolteadas;

        if (carta1.dataset.valor === carta2.dataset.valor) {
            carta1.classList.add('emparejada');
            carta2.classList.add('emparejada');
            paresEncontrados += 1;
            elPares.textContent = String(paresEncontrados);
            reproducir(sonidoMatch);

            const totalPares = (CONFIG_JUEGO.tamanoTablero * CONFIG_JUEGO.tamanoTablero) / 2;
            if (paresEncontrados === totalPares) {
                finalizarJuego('victoria');
            }
        } else {
            intentosUsados += 1;
            const restantes = Math.max(CONFIG_JUEGO.intentosPermitidos - intentosUsados, 0);
            elIntentos.textContent = String(restantes);
            carta1.classList.remove('volteada');
            carta2.classList.remove('volteada');

            if (intentosUsados >= CONFIG_JUEGO.intentosPermitidos) {
                finalizarJuego('derrota');
            }
        }

        cartasVolteadas = [];
        bloqueado = false;
    }

    // --- Temporizador
    function iniciarTemporizador() {
        tiempoInicio = Date.now();
        reproducir(musicaFondo);

        temporizador = setInterval(() => {
            tiempoRestante -= 1;
            elTiempo.textContent = String(Math.max(tiempoRestante, 0));

            if (tiempoRestante <= 0) {
                finalizarJuego('derrota');
            }
        }, 1000);
    }

    // --- Fin de partida
    function finalizarJuego(resultado) {
        if (juegoTerminado) return;
        juegoTerminado = true;
        bloqueado = true;

        clearInterval(temporizador);
        if (musicaFondo) {
            musicaFondo.pause();
            musicaFondo.currentTime = 0;
        }

        const tiempoUsadoSegundos = tiempoInicio
            ? (Date.now() - tiempoInicio) / 1000
            : 0;

        const modalIcono = document.getElementById('modal-icono');

        if (resultado === 'victoria') {
            reproducir(sonidoVictoria);
            modalIcono.src = CONFIG_JUEGO.urlIconoVictoria;
            modalIcono.alt = 'Victoria';
            modalTitulo.textContent = '¡Victoria!';
            modalDetalle.textContent = `Completaste el nivel ${CONFIG_JUEGO.nivel} en ${tiempoUsadoSegundos.toFixed(1)}s usando ${intentosUsados} de ${CONFIG_JUEGO.intentosPermitidos} intentos.`;
        } else {
            reproducir(sonidoDerrota);
            modalIcono.src = CONFIG_JUEGO.urlIconoDerrota;
            modalIcono.alt = 'Derrota';
            modalTitulo.textContent = 'Derrota';
            modalDetalle.textContent = 'Se acabaron los intentos o el tiempo. ¡Inténtalo de nuevo!';
        }

        modal.classList.remove('d-none');
        enviarResultado(resultado, tiempoUsadoSegundos);
    }

    function obtenerCookie(nombre) {
        const valor = `; ${document.cookie}`;
        const partes = valor.split(`; ${nombre}=`);
        if (partes.length === 2) return partes.pop().split(';').shift();
        return null;
    }

    function enviarResultado(resultado, tiempoUsadoSegundos) {
        fetch(CONFIG_JUEGO.urlGuardarPartida, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': obtenerCookie('csrftoken'),
            },
            body: JSON.stringify({
                nivel: CONFIG_JUEGO.nivel,
                resultado: resultado,
                intentos_usados: intentosUsados,
                tiempo_usado: tiempoUsadoSegundos,
            }),
        })
            .then((respuesta) => respuesta.json())
            .then((datos) => {
                if (datos.ok && datos.estadisticas) {
                    mostrarEstadisticas(datos.estadisticas);
                }
            })
            .catch((error) => {
                console.error('No se pudo guardar la partida:', error);
            });
    }

    function mostrarEstadisticas(stats) {
        document.getElementById('stat-victorias').textContent = stats.total_victorias;
        document.getElementById('stat-derrotas').textContent = stats.total_derrotas;
        document.getElementById('stat-jugadas').textContent = stats.total_partidas;
        document.getElementById('stat-promedio').textContent = stats.promedio_tiempo + 's';
        document.getElementById('stat-nivel-top').textContent = stats.nivel_mas_jugado;
    }

    // --- muestra todas las cartas rapidamente para que el jugador pueda memorizar su posición antes de empezar a jugar
    const TIEMPO_VISTA_PREVIA_MS = 1500;

    function mostrarVistaPreviaInicial() {
        bloqueado = true; 
        const avisoEl = document.getElementById('aviso-memoriza');
        if (avisoEl) avisoEl.classList.remove('d-none');

        const cartas = tablero.querySelectorAll('.carta');
        cartas.forEach((carta) => carta.classList.add('volteada'));

        setTimeout(() => {
            cartas.forEach((carta) => carta.classList.remove('volteada'));
            if (avisoEl) avisoEl.classList.add('d-none');
            bloqueado = false; 
        }, TIEMPO_VISTA_PREVIA_MS);
    }

    // --- Inicialización
    construirTablero();
    elTiempo.textContent = String(tiempoRestante);
    elIntentos.textContent = String(CONFIG_JUEGO.intentosPermitidos);
    mostrarVistaPreviaInicial();
})();
