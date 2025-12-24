/**
 * Modulo de actualizacion automatica sin recarga de pagina.
 * Reemplaza el meta refresh por AJAX polling.
 * WT-12: Actualizacion sin recarga de pagina
 */
/* global actualizarGraficaTemperatura, actualizarGraficaClimatizador */
/* exported detenerActualizacion */

const INTERVALO_MS = 10000; // 10 segundos
let intervalId = null;

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
 * Funcion principal que obtiene datos y actualiza el DOM
 */
async function actualizarDatos() {
    const indicador = document.getElementById('indicador-actualizacion');
    try {
        if (indicador) indicador.classList.add('visible');

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
        }
    } catch (error) {
        console.error('Error actualizando datos:', error);
    } finally {
        if (indicador) indicador.classList.remove('visible');
    }
}

/**
 * Inicia el ciclo de actualizacion automatica
 */
function iniciarActualizacion() {
    // Configurar intervalo (la primera carga ya tiene datos del servidor)
    intervalId = setInterval(actualizarDatos, INTERVALO_MS);
    console.log('Actualizacion automatica iniciada (intervalo: ' + INTERVALO_MS + 'ms)');
}

/**
 * Detiene el ciclo de actualizacion
 */
function detenerActualizacion() {
    if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
        console.log('Actualizacion automatica detenida');
    }
}

// Iniciar cuando el DOM este listo
document.addEventListener('DOMContentLoaded', iniciarActualizacion);
