/**
 * Modulo de grafica de temperatura
 * WT-23: Refactorizacion modular
 * WT-15: Soporte para historial de API
 * WT-16: Zona de confort en grafica
 */
import { TEMPERATURA_KEY, RANGOS_TIEMPO } from '../config.js';
import { filtrarPorTiempo, crearOpcionesBase } from './config.js';
import { obtenerHistorialAPI } from '../historial.js';

let chartTemperatura = null;
let usandoHistorialAPI = false;
let rangoActualConfig = null;

/**
 * Obtiene la instancia del chart (para uso externo)
 * @returns {Chart|null} Instancia del chart o null
 */
export function getChartTemperatura() {
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
 * Obtiene la temperatura deseada desde el DOM
 * @returns {number|null} Temperatura deseada o null si no se encuentra
 */
function obtenerTemperaturaDeseada() {
    const tempElement = document.getElementById('valor-temp-deseada');
    if (!tempElement) return null;

    const valor = parseFloat(tempElement.textContent);
    return isNaN(valor) ? null : valor;
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
 * Crea la configuracion del dataset de temperatura ambiente
 * @param {Array} datos - Datos de temperatura
 * @returns {Object} Configuracion del dataset
 */
function crearDatasetTemperatura(datos) {
    return {
        label: 'Temperatura Ambiente',
        data: datos,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.4,
        fill: false,
        pointRadius: usandoHistorialAPI ? 2 : 4,
        pointHoverRadius: 6,
        order: 1
    };
}

/**
 * Crea el dataset para la linea de temperatura deseada (WT-16)
 * @param {number} tempDeseada - Temperatura objetivo
 * @param {number} numPuntos - Numero de puntos en la grafica
 * @returns {Object} Configuracion del dataset
 */
function crearDatasetTempDeseada(tempDeseada, numPuntos) {
    const datos = new Array(numPuntos).fill(tempDeseada);
    return {
        label: 'Temperatura Deseada',
        data: datos,
        borderColor: 'rgba(46, 204, 113, 1)',
        borderWidth: 2,
        borderDash: [5, 5],
        pointRadius: 0,
        fill: false,
        order: 2
    };
}

/**
 * Crea el dataset para la zona de confort superior (WT-16)
 * @param {number} tempDeseada - Temperatura objetivo
 * @param {number} numPuntos - Numero de puntos en la grafica
 * @returns {Object} Configuracion del dataset
 */
function crearDatasetConfortSuperior(tempDeseada, numPuntos) {
    const datos = new Array(numPuntos).fill(tempDeseada + 1);
    return {
        label: 'Zona Confort (+1°C)',
        data: datos,
        borderColor: 'rgba(46, 204, 113, 0.3)',
        backgroundColor: 'rgba(46, 204, 113, 0.1)',
        borderWidth: 1,
        pointRadius: 0,
        fill: '+1',
        order: 3
    };
}

/**
 * Crea el dataset para la zona de confort inferior (WT-16)
 * @param {number} tempDeseada - Temperatura objetivo
 * @param {number} numPuntos - Numero de puntos en la grafica
 * @returns {Object} Configuracion del dataset
 */
function crearDatasetConfortInferior(tempDeseada, numPuntos) {
    const datos = new Array(numPuntos).fill(tempDeseada - 1);
    return {
        label: 'Zona Confort (-1°C)',
        data: datos,
        borderColor: 'rgba(46, 204, 113, 0.3)',
        borderWidth: 1,
        pointRadius: 0,
        fill: false,
        order: 4
    };
}

/**
 * Crea una nueva instancia de la grafica de temperatura
 * @param {HTMLElement} ctx - Canvas de la grafica
 * @param {Array} labels - Etiquetas del eje X
 * @param {Array} datos - Datos de temperatura
 * @param {number|null} tempDeseada - Temperatura deseada para zona de confort
 * @returns {Chart} Nueva instancia de Chart
 */
function crearGraficaTemperatura(ctx, labels, datos, tempDeseada) {
    const opciones = crearOpcionesBase('Temperatura (°C)');
    opciones.scales.y.beginAtZero = false;

    const datasets = [crearDatasetTemperatura(datos)];

    // WT-16: Agregar zona de confort si hay temperatura deseada
    if (tempDeseada !== null) {
        const numPuntos = datos.length;
        datasets.push(crearDatasetConfortSuperior(tempDeseada, numPuntos));
        datasets.push(crearDatasetConfortInferior(tempDeseada, numPuntos));
        datasets.push(crearDatasetTempDeseada(tempDeseada, numPuntos));
    }

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
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
    const tempDeseada = obtenerTemperaturaDeseada();

    if (!ctx) {
        console.error('No se encontro el canvas de temperatura');
        return;
    }

    if (chartTemperatura) {
        const numPuntos = datos.length;

        // Actualizar dataset de temperatura ambiente
        chartTemperatura.data.labels = labels;
        chartTemperatura.data.datasets[0].data = datos;
        chartTemperatura.data.datasets[0].pointRadius = usandoHistorialAPI ? 2 : 4;

        // WT-16: Actualizar zona de confort si hay temperatura deseada
        if (tempDeseada !== null && chartTemperatura.data.datasets.length >= 4) {
            // Actualizar datasets de confort
            chartTemperatura.data.datasets[1].data = new Array(numPuntos).fill(tempDeseada + 1);
            chartTemperatura.data.datasets[2].data = new Array(numPuntos).fill(tempDeseada - 1);
            chartTemperatura.data.datasets[3].data = new Array(numPuntos).fill(tempDeseada);
        } else if (tempDeseada !== null && chartTemperatura.data.datasets.length === 1) {
            // Agregar datasets de confort si no existen
            chartTemperatura.data.datasets.push(crearDatasetConfortSuperior(tempDeseada, numPuntos));
            chartTemperatura.data.datasets.push(crearDatasetConfortInferior(tempDeseada, numPuntos));
            chartTemperatura.data.datasets.push(crearDatasetTempDeseada(tempDeseada, numPuntos));
        }

        chartTemperatura.update();
    } else {
        chartTemperatura = crearGraficaTemperatura(ctx, labels, datos, tempDeseada);
    }
}

/**
 * Cambia el rango de tiempo de la grafica (WT-15)
 * @param {string} rango - Clave del rango seleccionado
 * @param {Array|null} historialAPI - Datos de la API o null para usar localStorage
 */
export function cambiarRangoGrafica(rango, historialAPI) {
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
export async function recargarHistorialAPI() {
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
export function actualizarGraficaTemperatura() {
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
