/**
 * Modulo de actualizacion automatica sin recarga de pagina.
 * Reemplaza el meta refresh por AJAX polling.
 * WT-12: Actualizacion sin recarga de pagina
 * WT-10: Estado de conexion visible
 * WT-9: Indicadores visuales de tendencia
 */
/* global actualizarGraficaTemperatura, actualizarGraficaClimatizador, TEMPERATURA_KEY */
/* exported detenerActualizacion */

const INTERVALO_MS = 10000; // 10 segundos
const UMBRAL_OBSOLETO_MS = 30000; // 30 segundos para considerar datos obsoletos
// TEMPERATURA_KEY ya definida en graficas.js (se carga primero)
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
 * WT-9: Obtiene el historico de temperaturas desde localStorage
 */
function obtenerHistoricoTemperatura() {
    try {
        const datos = localStorage.getItem(TEMPERATURA_KEY);
        return datos ? JSON.parse(datos) : [];
    } catch (e) {
        return [];
    }
}

/**
 * WT-9: Calcula la tendencia basada en las ultimas lecturas
 * @returns {Object} {direccion: 'subiendo'|'bajando'|'estable', acercando: boolean}
 */
function calcularTendencia(tempActual, tempDeseada) {
    const historico = obtenerHistoricoTemperatura();

    // Necesitamos al menos 3 lecturas para calcular tendencia
    if (historico.length < 3) {
        return { direccion: 'estable', acercando: null };
    }

    // Obtener ultimas 3 lecturas
    const ultimas = historico.slice(-3);
    const temperaturas = ultimas.map(h => h.temperatura);

    // Calcular promedio de diferencias
    let sumaDiferencias = 0;
    for (let i = 1; i < temperaturas.length; i++) {
        sumaDiferencias += temperaturas[i] - temperaturas[i - 1];
    }
    const promedioDiff = sumaDiferencias / (temperaturas.length - 1);

    // Determinar direccion
    let direccion = 'estable';
    if (promedioDiff > 0.2) {
        direccion = 'subiendo';
    } else if (promedioDiff < -0.2) {
        direccion = 'bajando';
    }

    // Determinar si se acerca o aleja de la deseada
    let acercando = null;
    if (tempActual !== null && tempDeseada !== null) {
        const diffActual = Math.abs(tempActual - tempDeseada);
        const diffAnterior = Math.abs(temperaturas[0] - tempDeseada);
        if (diffActual < diffAnterior - 0.1) {
            acercando = true;
        } else if (diffActual > diffAnterior + 0.1) {
            acercando = false;
        }
    }

    return { direccion, acercando };
}

/**
 * WT-9: Actualiza la flecha de tendencia
 */
function actualizarFlechaTendencia(flechaEl, tendencia) {
    flechaEl.classList.remove('subiendo', 'bajando', 'estable', 'acercando', 'alejando');
    flechaEl.classList.remove('glyphicon', 'glyphicon-arrow-up', 'glyphicon-arrow-down', 'glyphicon-minus');
    flechaEl.classList.add('glyphicon');

    const clasesFlecha = {
        'subiendo': ['glyphicon-arrow-up', 'subiendo'],
        'bajando': ['glyphicon-arrow-down', 'bajando'],
        'estable': ['glyphicon-minus', 'estable']
    };
    const clases = clasesFlecha[tendencia.direccion] || clasesFlecha['estable'];
    flechaEl.classList.add(...clases);

    if (tendencia.acercando === true) flechaEl.classList.add('acercando');
    if (tendencia.acercando === false) flechaEl.classList.add('alejando');

    flechaEl.classList.add('cambio');
    setTimeout(() => flechaEl.classList.remove('cambio'), 300);
}

/**
 * WT-9: Actualiza el icono del climatizador
 */
function actualizarIconoClimatizador(iconoEl, estadoClimatizador) {
    iconoEl.classList.remove('enfriando', 'calentando', 'apagado', 'encendido');
    iconoEl.classList.remove('glyphicon', 'glyphicon-asterisk', 'glyphicon-fire', 'glyphicon-off', 'glyphicon-ok');
    iconoEl.classList.add('glyphicon');

    const clasesIcono = {
        'enfriando': ['glyphicon-asterisk', 'enfriando'],
        'calentando': ['glyphicon-fire', 'calentando'],
        'encendido': ['glyphicon-ok', 'encendido'],
        'apagado': ['glyphicon-off', 'apagado']
    };
    const clases = clasesIcono[estadoClimatizador] || clasesIcono['apagado'];
    iconoEl.classList.add(...clases);
}

/**
 * WT-9: Genera el texto descriptivo de tendencia
 */
function generarTextoTendencia(tempActual, tempDeseada, estadoClimatizador, direccion) {
    const textos = {
        'enfriando': 'Enfriando hacia ' + tempDeseada + '°C',
        'calentando': 'Calentando hacia ' + tempDeseada + '°C'
    };
    if (textos[estadoClimatizador]) return textos[estadoClimatizador];
    if (direccion === 'subiendo') return 'Subiendo hacia ' + tempDeseada + '°C';
    if (direccion === 'bajando') return 'Bajando hacia ' + tempDeseada + '°C';
    if (Math.abs(tempActual - tempDeseada) < 1) return 'Temperatura estable en objetivo';
    return '';
}

/**
 * WT-9: Actualiza los indicadores visuales de tendencia
 */
function actualizarIndicadorTendencia(tempActual, tempDeseada, estadoClimatizador) {
    const flechaEl = document.getElementById('tendencia-flecha');
    const iconoEl = document.getElementById('tendencia-icono');
    const textoEl = document.getElementById('tendencia-texto');

    if (!flechaEl || !iconoEl || !textoEl) return;

    const tendencia = calcularTendencia(tempActual, tempDeseada);

    actualizarFlechaTendencia(flechaEl, tendencia);
    actualizarIconoClimatizador(iconoEl, estadoClimatizador);

    const textoDescriptivo = generarTextoTendencia(
        tempActual, tempDeseada, estadoClimatizador, tendencia.direccion
    );
    textoEl.textContent = textoDescriptivo;
    textoEl.classList.toggle('activo', textoDescriptivo !== '');
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

            // WT-9: Actualizar indicador de tendencia
            actualizarIndicadorTendencia(
                datos.temperatura_ambiente,
                datos.temperatura_deseada,
                datos.estado_climatizador
            );

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

    // WT-8: Inicializar tooltips de Bootstrap
    if (typeof $ !== 'undefined' && $.fn.tooltip) {
        $('[data-toggle="tooltip"]').tooltip();
    }

    // WT-9: Inicializar indicador de tendencia con valores del DOM
    const tempAmbEl = document.getElementById('valor-temp-ambiente');
    const tempDesEl = document.getElementById('valor-temp-deseada');
    const badgeClimEl = document.getElementById('badge-climatizador');
    if (tempAmbEl && tempDesEl && badgeClimEl) {
        const tempAmb = parseFloat(tempAmbEl.textContent) || 0;
        const tempDes = parseFloat(tempDesEl.textContent) || 0;
        const estadoClim = badgeClimEl.textContent.toLowerCase().trim();
        actualizarIndicadorTendencia(tempAmb, tempDes, estadoClim);
    }

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
