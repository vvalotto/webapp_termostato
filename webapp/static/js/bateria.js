/**
 * Modulo de gestion de la card de bateria
 * WT-18: Alerta visual de bateria baja
 * WT-23: Refactorizacion modular
 */
/* global TOOLTIPS_BATERIA, $ */
/* exported actualizarCardBateria */

/**
 * Actualiza la card de bateria segun el nivel del indicador
 * @param {string} indicador - Nivel de bateria ('normal', 'bajo', 'critico')
 */
function actualizarCardBateria(indicador) {
    const card = document.getElementById('card-bateria');
    const iconoAlerta = document.getElementById('icono-alerta-bateria');
    if (!card) return;

    const nivel = indicador.toLowerCase();

    // Actualizar clase de nivel de la card
    card.classList.remove('bateria-nivel-normal', 'bateria-nivel-bajo', 'bateria-nivel-critico');
    card.classList.add('bateria-nivel-' + nivel);

    // Mostrar/ocultar icono de alerta
    if (iconoAlerta) {
        iconoAlerta.classList.toggle('oculto', nivel === 'normal');
    }

    // Actualizar tooltip
    if (typeof $ !== 'undefined' && $.fn.tooltip) {
        $(card).attr('data-original-title', TOOLTIPS_BATERIA[nivel] || '').tooltip('fixTitle');
    }
}
