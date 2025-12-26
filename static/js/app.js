/**
 * Modulo principal de la aplicacion
 * Coordina todos los modulos y gestiona el ciclo de actualizacion
 * WT-12: Actualizacion sin recarga de pagina
 * WT-23: Refactorizacion modular
 */
/* global INTERVALO_MS, validarDatos, obtenerEstado, actualizarValor, actualizarBadge,
   actualizarCardBateria, actualizarEstadoConexion, actualizarTimestamp,
   mostrarActualizando, inicializarBannerCerrar, actualizarIndicadorTendencia,
   actualizarGraficaTemperatura, actualizarGraficaClimatizador,
   setUltimaActualizacion, getUltimaActualizacion, actualizarDiferencia,
   inicializarSelectorRango, cambiarRangoGrafica, $ */
/* exported detenerActualizacion */

let intervalId = null;
let timestampIntervalId = null;

/**
 * Procesa y muestra los datos recibidos de la API
 * @param {Object} datosOriginales - Datos originales de la API
 */
function procesarDatosRecibidos(datosOriginales) {
    const validacion = validarDatos(datosOriginales);
    const datos = validacion.datos;

    // Actualizar valores numericos
    actualizarValor('valor-temp-ambiente', datos.temperatura_ambiente, '');
    actualizarValor('valor-temp-deseada', datos.temperatura_deseada, '');
    actualizarValor('valor-bateria', datos.carga_bateria, '');

    // Actualizar badges de estado
    actualizarBadge('badge-climatizador', datos.estado_climatizador, 'estado-badge');
    actualizarBadge('badge-indicador', datos.indicador, 'nivel-badge');

    // Actualizar card de bateria
    if (typeof datos.indicador === 'string' && datos.indicador !== 'Error') {
        actualizarCardBateria(datosOriginales.indicador);
    }

    // Actualizar graficas y tendencia solo si los datos son validos
    if (!validacion.hayErrores) {
        actualizarGraficaTemperatura();
        actualizarGraficaClimatizador();
        actualizarIndicadorTendencia(
            datosOriginales.temperatura_ambiente,
            datosOriginales.temperatura_deseada,
            datosOriginales.estado_climatizador
        );
        // WT-11: Actualizar indicador de diferencia
        actualizarDiferencia(
            datosOriginales.temperatura_ambiente,
            datosOriginales.temperatura_deseada
        );
    }
}

/**
 * Maneja el caso de fallo de conexion
 */
function manejarFalloConexion() {
    if (!getUltimaActualizacion()) {
        setUltimaActualizacion(Date.now());
    }
    actualizarEstadoConexion('offline');
    actualizarTimestamp();
}

/**
 * Funcion principal que obtiene datos y actualiza el DOM
 */
async function actualizarDatos() {
    try {
        mostrarActualizando(true);
        const resultado = await obtenerEstado();

        if (resultado.success) {
            procesarDatosRecibidos(resultado.data);
            setUltimaActualizacion(Date.now());
            actualizarEstadoConexion(resultado.from_cache ? 'offline' : 'online');
            actualizarTimestamp();
        } else {
            manejarFalloConexion();
        }
    } catch (error) {
        console.error('Error actualizando datos:', error);
        manejarFalloConexion();
    } finally {
        mostrarActualizando(false);
    }
}

/**
 * Inicializa el indicador de tendencia con valores del DOM
 */
function inicializarTendencia() {
    const tempAmbEl = document.getElementById('valor-temp-ambiente');
    const tempDesEl = document.getElementById('valor-temp-deseada');
    const badgeClimEl = document.getElementById('badge-climatizador');

    if (tempAmbEl && tempDesEl && badgeClimEl) {
        const tempAmb = parseFloat(tempAmbEl.textContent) || 0;
        const tempDes = parseFloat(tempDesEl.textContent) || 0;
        const estadoClim = badgeClimEl.textContent.toLowerCase().trim();
        actualizarIndicadorTendencia(tempAmb, tempDes, estadoClim);
    }
}

/**
 * Inicializa el indicador de diferencia con valores del DOM (WT-11)
 */
function inicializarDiferencia() {
    const tempAmbEl = document.getElementById('valor-temp-ambiente');
    const tempDesEl = document.getElementById('valor-temp-deseada');

    if (tempAmbEl && tempDesEl) {
        const tempAmb = parseFloat(tempAmbEl.textContent) || 0;
        const tempDes = parseFloat(tempDesEl.textContent) || 0;
        actualizarDiferencia(tempAmb, tempDes);
    }
}

/**
 * Inicia el ciclo de actualizacion automatica
 */
function iniciarActualizacion() {
    // Inicializar boton de cerrar del banner
    inicializarBannerCerrar();

    // Verificar conexion inmediatamente al iniciar
    actualizarDatos();

    // Configurar intervalo de datos
    intervalId = setInterval(actualizarDatos, INTERVALO_MS);

    // Configurar intervalo para actualizar timestamp cada segundo
    timestampIntervalId = setInterval(actualizarTimestamp, 1000);

    // Inicializar tooltips de Bootstrap
    if (typeof $ !== 'undefined' && $.fn.tooltip) {
        $('[data-toggle="tooltip"]').tooltip();
    }

    // Inicializar indicador de tendencia
    inicializarTendencia();

    // Inicializar indicador de diferencia (WT-11)
    inicializarDiferencia();

    // Inicializar selector de rango de tiempo (WT-15)
    inicializarSelectorRango(cambiarRangoGrafica);

    console.log('Actualizacion automatica iniciada (intervalo: ' + INTERVALO_MS + 'ms)');
}

/**
 * Detiene el ciclo de actualizacion
 */
function detenerActualizacion() {
    if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
    }
    if (timestampIntervalId) {
        clearInterval(timestampIntervalId);
        timestampIntervalId = null;
    }
    console.log('Actualizacion automatica detenida');
}

// Iniciar cuando el DOM este listo
document.addEventListener('DOMContentLoaded', iniciarActualizacion);
