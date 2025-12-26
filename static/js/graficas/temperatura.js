/**
 * Modulo de grafica de temperatura
 * WT-23: Refactorizacion modular
 * WT-15: Soporte para historial de API
 */
/* global TEMPERATURA_KEY, RANGOS_TIEMPO, Chart, filtrarPorTiempo, crearOpcionesBase,
   obtenerHistorialAPI */
/* exported actualizarGraficaTemperatura, cambiarRangoGrafica, getChartTemperatura,
   recargarHistorialAPI */

let chartTemperatura = null;
let usandoHistorialAPI = false;
let rangoActualConfig = null;

/**
 * Obtiene la instancia del chart (para uso externo)
 * @returns {Chart|null} Instancia del chart o null
 */
function getChartTemperatura() {
    return chartTemperatura;
}

/**
 * Obtiene la temperatura actual desde el DOM
 * @returns {number|null} Temperatura actual o null si no se encuentra
 */
function obtenerTemperaturaActual() {
    const tempElement = document.querySelector('.card-ambiente .metric-value');
    if (!tempElement) return null;

    const texto = tempElement.textContent.trim();
    const match = texto.match(/[\d.]+/);
    return match ? parseFloat(match[0]) : null;
}

/**
 * Carga el historico de temperaturas desde localStorage
 * @returns {Array} Array con el historico de temperaturas filtrado
 */
function cargarHistoricoTemperatura() {
    const datos = localStorage.getItem(TEMPERATURA_KEY);
    if (!datos) return [];

    try {
        const historico = JSON.parse(datos);
        return filtrarPorTiempo(historico);
    } catch (e) {
        console.error('Error al parsear historico de temperatura:', e);
        return [];
    }
}

/**
 * Guarda el historico de temperaturas en localStorage
 * @param {Array} historico - Array con datos de temperatura
 */
function guardarHistoricoTemperatura(historico) {
    const historicoFiltrado = filtrarPorTiempo(historico);
    localStorage.setItem(TEMPERATURA_KEY, JSON.stringify(historicoFiltrado));
}

/**
 * Agrega una nueva temperatura al historico
 * @param {number} temperatura - Valor de temperatura a agregar
 * @returns {Array} Historico actualizado
 */
function agregarTemperatura(temperatura) {
    let historico = cargarHistoricoTemperatura();
    const ahora = new Date();

    historico.push({
        temperatura: temperatura,
        timestamp: ahora.toLocaleTimeString('es-ES'),
        fecha_completa: ahora.toISOString()
    });

    historico = filtrarPorTiempo(historico);
    guardarHistoricoTemperatura(historico);
    return historico;
}

/**
 * Crea la configuracion del dataset de temperatura
 * @param {Array} datos - Datos de temperatura
 * @returns {Object} Configuracion del dataset
 */
function crearDatasetTemperatura(datos) {
    return {
        label: 'Temperatura (C)',
        data: datos,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.4,
        fill: true,
        pointRadius: usandoHistorialAPI ? 2 : 4,
        pointHoverRadius: 6
    };
}

/**
 * Crea una nueva instancia de la grafica de temperatura
 * @param {HTMLElement} ctx - Canvas de la grafica
 * @param {Array} labels - Etiquetas del eje X
 * @param {Array} datos - Datos de temperatura
 * @returns {Chart} Nueva instancia de Chart
 */
function crearGraficaTemperatura(ctx, labels, datos) {
    const opciones = crearOpcionesBase('Temperatura (C)');
    opciones.scales.y.beginAtZero = false;

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [crearDatasetTemperatura(datos)]
        },
        options: opciones
    });
}

/**
 * Actualiza la grafica con los datos proporcionados
 * @param {Array} historico - Datos a mostrar
 */
function renderizarGrafica(historico) {
    const labels = historico.map(function(d) { return d.timestamp; });
    const datos = historico.map(function(d) { return d.temperatura; });
    const ctx = document.getElementById('temperaturaChart');

    if (!ctx) {
        console.error('No se encontro el canvas de temperatura');
        return;
    }

    if (chartTemperatura) {
        chartTemperatura.data.labels = labels;
        chartTemperatura.data.datasets[0].data = datos;
        chartTemperatura.data.datasets[0].pointRadius = usandoHistorialAPI ? 2 : 4;
        chartTemperatura.update();
    } else {
        chartTemperatura = crearGraficaTemperatura(ctx, labels, datos);
    }
}

/**
 * Cambia el rango de tiempo de la grafica (WT-15)
 * @param {string} rango - Clave del rango seleccionado
 * @param {Array|null} historialAPI - Datos de la API o null para usar localStorage
 */
function cambiarRangoGrafica(rango, historialAPI) {
    const config = RANGOS_TIEMPO[rango];
    if (!config) return;

    usandoHistorialAPI = config.usaAPI;
    rangoActualConfig = config;

    if (config.usaAPI && historialAPI) {
        // Usar datos de la API
        renderizarGrafica(historialAPI);
    } else {
        // Usar datos locales (5min)
        const historico = cargarHistoricoTemperatura();
        renderizarGrafica(historico);
    }
}

/**
 * Recarga el historial de la API para el rango actual
 */
async function recargarHistorialAPI() {
    if (!usandoHistorialAPI || !rangoActualConfig) return;

    try {
        const historial = await obtenerHistorialAPI(rangoActualConfig.limite);
        if (historial && historial.length > 0) {
            renderizarGrafica(historial);
        }
    } catch (error) {
        console.error('Error recargando historial:', error);
    }
}

/**
 * Crea o actualiza la grafica de temperatura
 */
function actualizarGraficaTemperatura() {
    const temperatura = obtenerTemperaturaActual();
    if (temperatura === null || isNaN(temperatura)) {
        console.log('No se pudo obtener temperatura valida');
        return;
    }

    // Siempre guardamos en localStorage para el modo 5min
    const historico = agregarTemperatura(temperatura);

    // Actualizar segun el modo
    if (usandoHistorialAPI) {
        // En modo API, recargar historial del servidor
        recargarHistorialAPI();
    } else {
        // En modo local, usar datos de localStorage
        renderizarGrafica(historico);
    }
}
