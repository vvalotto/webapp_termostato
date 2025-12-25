/**
 * Modulo de grafica de estados del climatizador
 * WT-23: Refactorizacion modular
 */
/* global CLIMATIZADOR_KEY, Chart, filtrarPorTiempo, crearOpcionesBase */
/* exported actualizarGraficaClimatizador */

let chartClimatizador = null;

/**
 * Obtiene el estado actual del climatizador desde el DOM
 * @returns {string|null} Estado del climatizador o null
 */
function obtenerEstadoClimatizador() {
    const estadoElement = document.querySelector('.card-climatizador .estado-badge');
    if (!estadoElement) return null;

    const texto = estadoElement.textContent.trim().toLowerCase();
    if (texto.includes('apagado')) return 'apagado';
    if (texto.includes('enfriando')) return 'enfriando';
    if (texto.includes('calentando')) return 'calentando';
    return null;
}

/**
 * Carga el historico de estados desde localStorage
 * @returns {Array} Array con el historico filtrado
 */
function cargarHistoricoClimatizador() {
    const datos = localStorage.getItem(CLIMATIZADOR_KEY);
    if (!datos) return [];

    try {
        const historico = JSON.parse(datos);
        return filtrarPorTiempo(historico);
    } catch (e) {
        console.error('Error al parsear historico del climatizador:', e);
        return [];
    }
}

/**
 * Guarda el historico de estados en localStorage
 * @param {Array} historico - Array con datos de estados
 */
function guardarHistoricoClimatizador(historico) {
    const historicoFiltrado = filtrarPorTiempo(historico);
    localStorage.setItem(CLIMATIZADOR_KEY, JSON.stringify(historicoFiltrado));
}

/**
 * Convierte estado a valor numerico
 * @param {string} estado - Estado del climatizador
 * @returns {number} Valor numerico (0, 1 o 2)
 */
function estadoAValor(estado) {
    const valores = { 'apagado': 0, 'enfriando': 1, 'calentando': 2 };
    return valores[estado] !== undefined ? valores[estado] : 0;
}

/**
 * Agrega un nuevo estado al historico
 * @param {string} estado - Estado del climatizador
 * @returns {Array} Historico actualizado
 */
function agregarEstadoClimatizador(estado) {
    let historico = cargarHistoricoClimatizador();
    const ahora = new Date();

    historico.push({
        estado: estado,
        valor: estadoAValor(estado),
        timestamp: ahora.toLocaleTimeString('es-ES'),
        fecha_completa: ahora.toISOString()
    });

    historico = filtrarPorTiempo(historico);
    guardarHistoricoClimatizador(historico);
    return historico;
}

/**
 * Crea la configuracion del dataset del climatizador
 * @param {Array} datos - Datos de estados
 * @returns {Object} Configuracion del dataset
 */
function crearDatasetClimatizador(datos) {
    return {
        label: 'Estado',
        data: datos,
        borderColor: 'rgb(52, 152, 219)',
        backgroundColor: 'rgba(52, 152, 219, 0.2)',
        stepped: 'before',
        fill: true,
        pointRadius: 5,
        pointHoverRadius: 7,
        pointBackgroundColor: function(context) {
            const valor = context.parsed.y;
            if (valor === 2) return 'rgb(231, 76, 60)';
            if (valor === 1) return 'rgb(52, 152, 219)';
            return 'rgb(149, 165, 166)';
        }
    };
}

/**
 * Crea las opciones especificas del climatizador
 * @returns {Object} Opciones de configuracion
 */
function crearOpcionesClimatizador() {
    const opciones = crearOpcionesBase('Estado del Sistema');
    opciones.scales.y.min = -0.3;
    opciones.scales.y.max = 2.3;
    opciones.scales.y.ticks = {
        stepSize: 1,
        callback: function(value) {
            if (value === 2) return 'CALENTANDO';
            if (value === 1) return 'ENFRIANDO';
            if (value === 0) return 'APAGADO';
            return '';
        }
    };
    opciones.plugins.tooltip.callbacks = {
        label: function(context) {
            const valor = context.parsed.y;
            let estado = 'APAGADO';
            if (valor === 2) estado = 'CALENTANDO';
            else if (valor === 1) estado = 'ENFRIANDO';
            return 'Estado: ' + estado;
        }
    };
    return opciones;
}

/**
 * Crea una nueva instancia de la grafica del climatizador
 * @param {HTMLElement} ctx - Canvas de la grafica
 * @param {Array} labels - Etiquetas del eje X
 * @param {Array} datos - Datos de estados
 * @returns {Chart} Nueva instancia de Chart
 */
function crearGraficaClimatizador(ctx, labels, datos) {
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [crearDatasetClimatizador(datos)]
        },
        options: crearOpcionesClimatizador()
    });
}

/**
 * Crea o actualiza la grafica del climatizador
 */
function actualizarGraficaClimatizador() {
    const estado = obtenerEstadoClimatizador();
    if (estado === null) {
        console.log('No se pudo obtener estado del climatizador');
        return;
    }

    const historico = agregarEstadoClimatizador(estado);
    const labels = historico.map(function(d) { return d.timestamp; });
    const datos = historico.map(function(d) { return d.valor; });
    const ctx = document.getElementById('climatizadorChart');

    if (!ctx) {
        console.error('No se encontro el canvas del climatizador');
        return;
    }

    if (chartClimatizador) {
        chartClimatizador.data.labels = labels;
        chartClimatizador.data.datasets[0].data = datos;
        chartClimatizador.update();
    } else {
        chartClimatizador = crearGraficaClimatizador(ctx, labels, datos);
    }
}
