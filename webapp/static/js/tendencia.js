/**
 * Modulo de indicadores visuales de tendencia
 * WT-9: Indicadores visuales de tendencia
 * WT-23: Refactorizacion modular
 */
import { TEMPERATURA_KEY } from './config.js';

/**
 * Obtiene el historico de temperaturas desde localStorage
 * @returns {Array} Array con historico de temperaturas
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
 * Calcula la tendencia basada en las ultimas lecturas
 * @param {number} tempActual - Temperatura actual
 * @param {number} tempDeseada - Temperatura objetivo
 * @returns {Object} {direccion: 'subiendo'|'bajando'|'estable', acercando: boolean|null}
 */
function calcularTendencia(tempActual, tempDeseada) {
    const historico = obtenerHistoricoTemperatura();

    // Necesitamos al menos 3 lecturas para calcular tendencia
    if (historico.length < 3) {
        return { direccion: 'estable', acercando: null };
    }

    // Obtener ultimas 3 lecturas
    const ultimas = historico.slice(-3);
    const temperaturas = ultimas.map(function(h) { return h.temperatura; });

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

    return { direccion: direccion, acercando: acercando };
}

/**
 * Actualiza la flecha de tendencia
 * @param {HTMLElement} flechaEl - Elemento de la flecha
 * @param {Object} tendencia - Objeto con direccion y acercando
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
    clases.forEach(function(c) { flechaEl.classList.add(c); });

    if (tendencia.acercando === true) flechaEl.classList.add('acercando');
    if (tendencia.acercando === false) flechaEl.classList.add('alejando');

    flechaEl.classList.add('cambio');
    setTimeout(function() { flechaEl.classList.remove('cambio'); }, 300);
}

/**
 * Actualiza el icono del climatizador
 * @param {HTMLElement} iconoEl - Elemento del icono
 * @param {string} estadoClimatizador - Estado del climatizador
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
    clases.forEach(function(c) { iconoEl.classList.add(c); });
}

/**
 * Genera el texto descriptivo de tendencia
 * @param {number} tempActual - Temperatura actual
 * @param {number} tempDeseada - Temperatura objetivo
 * @param {string} estadoClimatizador - Estado del climatizador
 * @param {string} direccion - Direccion de la tendencia
 * @returns {string} Texto descriptivo
 */
function generarTextoTendencia(tempActual, tempDeseada, estadoClimatizador, direccion) {
    const textos = {
        'enfriando': 'Enfriando hacia ' + tempDeseada + ' C',
        'calentando': 'Calentando hacia ' + tempDeseada + ' C'
    };
    if (textos[estadoClimatizador]) return textos[estadoClimatizador];
    if (direccion === 'subiendo') return 'Subiendo hacia ' + tempDeseada + ' C';
    if (direccion === 'bajando') return 'Bajando hacia ' + tempDeseada + ' C';
    if (Math.abs(tempActual - tempDeseada) < 1) return 'Temperatura estable en objetivo';
    return '';
}

/**
 * Actualiza los indicadores visuales de tendencia
 * @param {number} tempActual - Temperatura actual
 * @param {number} tempDeseada - Temperatura objetivo
 * @param {string} estadoClimatizador - Estado del climatizador
 */
export function actualizarIndicadorTendencia(tempActual, tempDeseada, estadoClimatizador) {
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
