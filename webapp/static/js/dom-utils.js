/**
 * Utilidades para manipulacion del DOM
 * WT-21: Marca valores invalidos con clase especial
 * WT-23: Refactorizacion modular
 */
/* exported actualizarValor, actualizarBadge, tiempoTranscurrido */

/**
 * Actualiza un valor en el DOM si ha cambiado
 * @param {string} elementId - ID del elemento a actualizar
 * @param {any} valor - Nuevo valor
 * @param {string} sufijo - Sufijo opcional (ej: unidad)
 */
function actualizarValor(elementId, valor, sufijo) {
    if (sufijo === undefined) sufijo = '';
    const elemento = document.getElementById(elementId);
    if (!elemento) return;

    const valorFormateado = valor + sufijo;
    const esInvalido = (valor === 'N/A' || valor === 'Error');

    if (elemento.textContent !== valorFormateado) {
        elemento.textContent = valorFormateado;
        // WT-21: Marcar si es valor invalido
        elemento.classList.toggle('valor-invalido', esInvalido);
        // Efecto visual de cambio
        elemento.classList.add('valor-actualizado');
        setTimeout(function() {
            elemento.classList.remove('valor-actualizado');
        }, 300);
    }
}

/**
 * Actualiza un badge de estado (climatizador o indicador bateria)
 * @param {string} elementId - ID del elemento badge
 * @param {string} valor - Nuevo valor del badge
 * @param {string} claseBase - Clase CSS base del badge
 */
function actualizarBadge(elementId, valor, claseBase) {
    const elemento = document.getElementById(elementId);
    if (!elemento) return;

    const esInvalido = (valor === 'N/A' || valor === 'Error');
    const valorMostrar = esInvalido ? valor : valor.toUpperCase();

    if (elemento.textContent !== valorMostrar) {
        elemento.textContent = valorMostrar;
        // Actualizar clase del badge
        if (esInvalido) {
            elemento.className = claseBase + ' badge-invalido';
        } else {
            elemento.className = claseBase + ' badge-' + valor.toLowerCase();
        }
        // Efecto visual de cambio
        elemento.classList.add('valor-actualizado');
        setTimeout(function() {
            elemento.classList.remove('valor-actualizado');
        }, 300);
    }
}

/**
 * Calcula el tiempo transcurrido en formato legible
 * @param {number} timestamp - Timestamp en milisegundos
 * @returns {string} Tiempo formateado (ej: "hace 30s", "hace 2min")
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
