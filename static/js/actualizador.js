/**
 * Modulo de actualizacion automatica sin recarga de pagina.
 * Reemplaza el meta refresh por AJAX polling.
 * WT-12: Actualizacion sin recarga de pagina
 * WT-10: Estado de conexion visible
 */
/* global actualizarGraficaTemperatura, actualizarGraficaClimatizador */
/* exported detenerActualizacion */

const INTERVALO_MS = 10000; // 10 segundos
const UMBRAL_OBSOLETO_MS = 30000; // 30 segundos para considerar datos obsoletos
let intervalId = null;
let timestampIntervalId = null;
let ultimaActualizacion = null;

/**
 * Obtiene el estado del termostato desde el endpoint /api/estado
 */
async function obtenerEstado() {
    const response = await fetch('/api/estado');
    return response.json();
}

/**
 * Actualiza un valor en el DOM si ha cambiado
 */
function actualizarValor(elementId, valor, sufijo = '') {
    const elemento = document.getElementById(elementId);
    if (elemento) {
        const valorFormateado = valor + sufijo;
        if (elemento.textContent !== valorFormateado) {
            elemento.textContent = valorFormateado;
            // Efecto visual de cambio
            elemento.classList.add('valor-actualizado');
            setTimeout(() => elemento.classList.remove('valor-actualizado'), 300);
        }
    }
}

/**
 * Actualiza un badge de estado (climatizador o indicador bateria)
 */
function actualizarBadge(elementId, valor, claseBase) {
    const elemento = document.getElementById(elementId);
    if (elemento) {
        const valorUpper = valor.toUpperCase();
        if (elemento.textContent !== valorUpper) {
            elemento.textContent = valorUpper;
            // Actualizar clase del badge
            elemento.className = claseBase + ' badge-' + valor.toLowerCase();
            // Efecto visual de cambio
            elemento.classList.add('valor-actualizado');
            setTimeout(() => elemento.classList.remove('valor-actualizado'), 300);
        }
    }
}

/**
 * WT-10: Calcula el tiempo transcurrido en formato legible
 */
function tiempoTranscurrido(timestamp) {
    if (!timestamp) return 'nunca';
    const segundos = Math.floor((Date.now() - timestamp) / 1000);
    if (segundos < 60) return 'hace ' + segundos + 's';
    const minutos = Math.floor(segundos / 60);
    if (minutos < 60) return 'hace ' + minutos + 'min';
    const horas = Math.floor(minutos / 60);
    return 'hace ' + horas + 'h';
}

/**
 * WT-10: Actualiza el indicador de estado de conexion
 */
function actualizarEstadoConexion(estado) {
    const contenedor = document.getElementById('estado-conexion');
    const icono = document.getElementById('icono-estado');
    const texto = document.getElementById('texto-estado');
    const dashboardContainer = document.querySelector('.dashboard-container');

    if (!contenedor || !icono || !texto) return;

    // Remover clases previas
    contenedor.classList.remove('online', 'offline', 'obsoleto');
    icono.classList.remove('glyphicon-ok', 'glyphicon-remove', 'glyphicon-warning-sign');

    if (estado === 'online') {
        contenedor.classList.add('online');
        icono.classList.add('glyphicon-ok');
        texto.textContent = 'En línea';
        if (dashboardContainer) dashboardContainer.classList.remove('datos-obsoletos');
    } else if (estado === 'offline') {
        contenedor.classList.add('offline');
        icono.classList.add('glyphicon-remove');
        texto.textContent = 'Sin conexión';
    } else if (estado === 'obsoleto') {
        contenedor.classList.add('obsoleto');
        icono.classList.add('glyphicon-warning-sign');
        texto.textContent = 'Datos desactualizados';
        if (dashboardContainer) dashboardContainer.classList.add('datos-obsoletos');
    }
}

/**
 * WT-10: Actualiza el timestamp mostrado
 */
function actualizarTimestamp() {
    const timestampEl = document.getElementById('timestamp-estado');
    if (timestampEl && ultimaActualizacion) {
        timestampEl.textContent = 'Actualizado ' + tiempoTranscurrido(ultimaActualizacion);

        // Verificar si los datos estan obsoletos (> 30s)
        const tiempoSinActualizar = Date.now() - ultimaActualizacion;
        if (tiempoSinActualizar > UMBRAL_OBSOLETO_MS) {
            actualizarEstadoConexion('obsoleto');
        }
    }
}

/**
 * WT-10: Muestra/oculta el icono de actualizacion
 */
function mostrarActualizando(visible) {
    const icono = document.getElementById('icono-estado');
    if (icono) {
        if (visible) {
            icono.classList.remove('glyphicon-ok', 'glyphicon-remove', 'glyphicon-warning-sign');
            icono.classList.add('glyphicon-refresh', 'actualizando');
        } else {
            icono.classList.remove('glyphicon-refresh', 'actualizando');
        }
    }
}

/**
 * Funcion principal que obtiene datos y actualiza el DOM
 */
async function actualizarDatos() {
    try {
        // WT-10: Mostrar icono de actualizacion
        mostrarActualizando(true);

        const resultado = await obtenerEstado();

        if (resultado.success) {
            const datos = resultado.data;

            // Actualizar valores numericos
            actualizarValor('valor-temp-ambiente', datos.temperatura_ambiente, '');
            actualizarValor('valor-temp-deseada', datos.temperatura_deseada, '');
            actualizarValor('valor-bateria', datos.carga_bateria, '');

            // Actualizar badges de estado
            actualizarBadge('badge-climatizador', datos.estado_climatizador, 'estado-badge');
            actualizarBadge('badge-indicador', datos.indicador, 'nivel-badge');

            // Actualizar graficas (si existen las funciones de graficas.js)
            if (typeof actualizarGraficaTemperatura === 'function') {
                actualizarGraficaTemperatura();
            }
            if (typeof actualizarGraficaClimatizador === 'function') {
                actualizarGraficaClimatizador();
            }

            // WT-10: Marcar estado segun si son datos frescos o cacheados
            ultimaActualizacion = Date.now();
            if (resultado.from_cache) {
                actualizarEstadoConexion('offline');
            } else {
                actualizarEstadoConexion('online');
            }
            actualizarTimestamp();
        }
    } catch (error) {
        console.error('Error actualizando datos:', error);
        // WT-10: Marcar como offline
        actualizarEstadoConexion('offline');
    } finally {
        // WT-10: Ocultar icono de actualizacion
        mostrarActualizando(false);
    }
}

/**
 * Inicia el ciclo de actualizacion automatica
 */
function iniciarActualizacion() {
    // WT-10: Marcar timestamp inicial (datos vienen del servidor)
    ultimaActualizacion = Date.now();
    actualizarEstadoConexion('online');

    // Configurar intervalo de datos (la primera carga ya tiene datos del servidor)
    intervalId = setInterval(actualizarDatos, INTERVALO_MS);

    // WT-10: Configurar intervalo para actualizar timestamp cada segundo
    timestampIntervalId = setInterval(actualizarTimestamp, 1000);

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
    // WT-10: Detener actualizacion de timestamp
    if (timestampIntervalId) {
        clearInterval(timestampIntervalId);
        timestampIntervalId = null;
    }
    console.log('Actualizacion automatica detenida');
}

// Iniciar cuando el DOM este listo
document.addEventListener('DOMContentLoaded', iniciarActualizacion);
