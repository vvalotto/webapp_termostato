/**
 * Módulo de gráficas para el Dashboard del Termostato
 * Gestiona la visualización de la evolución de temperatura y estados del climatizador
 * Utiliza Chart.js y localStorage para persistencia de datos
 */

// ==================== CONFIGURACIÓN GLOBAL ====================

const VENTANA_TIEMPO_MS = 5 * 60 * 1000; // 5 minutos en milisegundos
const TEMPERATURA_KEY = 'temperatura_historico';
const CLIMATIZADOR_KEY = 'climatizador_historico';

// Variables para las instancias de gráficas
let chartTemperatura = null;
let chartClimatizador = null;

/**
 * Filtra un histórico para mantener solo los datos de los últimos 5 minutos
 * @param {Array} historico - Array con datos históricos
 * @returns {Array} Array filtrado con datos recientes
 */
function filtrarPorTiempo(historico) {
  const ahora = new Date().getTime();
  return historico.filter(item => {
    const fechaItem = new Date(item.fecha_completa).getTime();
    const diferencia = ahora - fechaItem;
    return diferencia <= VENTANA_TIEMPO_MS;
  });
}


// ==================== MÓDULO DE TEMPERATURA ====================

/**
 * Obtiene la temperatura actual desde el DOM
 * @returns {number|null} Temperatura actual o null si no se encuentra
 */
function obtenerTemperaturaActual() {
  const tempElement = document.querySelector('.card-ambiente .metric-value');
  if (tempElement) {
    const texto = tempElement.textContent.trim();
    const match = texto.match(/[\d.]+/);
    if (match) {
      return parseFloat(match[0]);
    }
  }
  return null;
}

/**
 * Carga el histórico de temperaturas desde localStorage
 * Filtra automáticamente datos más antiguos de 5 minutos
 * @returns {Array} Array con el histórico de temperaturas filtrado
 */
function cargarHistoricoTemperatura() {
  const datos = localStorage.getItem(TEMPERATURA_KEY);
  if (datos) {
    try {
      const historico = JSON.parse(datos);
      return filtrarPorTiempo(historico);
    } catch (e) {
      console.error('Error al parsear histórico de temperatura:', e);
      return [];
    }
  }
  return [];
}

/**
 * Guarda el histórico de temperaturas en localStorage
 * Filtra automáticamente para guardar solo datos de los últimos 5 minutos
 * @param {Array} historico - Array con datos de temperatura
 */
function guardarHistoricoTemperatura(historico) {
  // Filtrar antes de guardar para evitar almacenar datos antiguos innecesarios
  const historicoFiltrado = filtrarPorTiempo(historico);
  localStorage.setItem(TEMPERATURA_KEY, JSON.stringify(historicoFiltrado));
}

/**
 * Agrega una nueva temperatura al histórico
 * Filtra automáticamente datos más antiguos de 5 minutos
 * @param {number} temperatura - Valor de temperatura a agregar
 * @returns {Array} Histórico actualizado
 */
function agregarTemperatura(temperatura) {
  let historico = cargarHistoricoTemperatura();

  const ahora = new Date();
  const timestamp = ahora.toLocaleTimeString('es-ES');

  historico.push({
    temperatura: temperatura,
    timestamp: timestamp,
    fecha_completa: ahora.toISOString()
  });

  // Filtrar datos más antiguos de 5 minutos
  historico = filtrarPorTiempo(historico);

  guardarHistoricoTemperatura(historico);
  return historico;
}

/**
 * Crea o actualiza la gráfica de temperatura
 */
function actualizarGraficaTemperatura() {
  const temperatura = obtenerTemperaturaActual();

  if (temperatura === null || isNaN(temperatura)) {
    console.log('No se pudo obtener temperatura válida');
    return;
  }

  const historico = agregarTemperatura(temperatura);

  const labels = historico.map(d => d.timestamp);
  const datos = historico.map(d => d.temperatura);

  const ctx = document.getElementById('temperaturaChart');

  if (!ctx) {
    console.error('No se encontró el canvas de temperatura');
    return;
  }

  if (chartTemperatura) {
    // Actualizar gráfica existente
    chartTemperatura.data.labels = labels;
    chartTemperatura.data.datasets[0].data = datos;
    chartTemperatura.update();
  } else {
    // Crear nueva gráfica
    chartTemperatura = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Temperatura (°C)',
          data: datos,
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.4,
          fill: true,
          pointRadius: 4,
          pointHoverRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        aspectRatio: 3,
        plugins: {
          legend: {
            display: true,
            position: 'top'
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        },
        scales: {
          y: {
            beginAtZero: false,
            title: {
              display: true,
              text: 'Temperatura (°C)'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Hora'
            },
            ticks: {
              maxRotation: 45,
              minRotation: 45
            }
          }
        }
      }
    });
  }
}


// ==================== MÓDULO DE CLIMATIZADOR ====================

/**
 * Obtiene el estado actual del climatizador desde el DOM
 * @returns {string|null} 'encendido', 'apagado' o null si no se encuentra
 */
function obtenerEstadoClimatizador() {
  const estadoElement = document.querySelector('.card-climatizador .estado-badge');
  if (estadoElement) {
    const texto = estadoElement.textContent.trim().toLowerCase();
    if (texto.includes('encendido')) {
      return 'encendido';
    } else if (texto.includes('apagado')) {
      return 'apagado';
    }
  }
  return null;
}

/**
 * Carga el histórico de estados del climatizador desde localStorage
 * Filtra automáticamente datos más antiguos de 5 minutos
 * @returns {Array} Array con el histórico de estados filtrado
 */
function cargarHistoricoClimatizador() {
  const datos = localStorage.getItem(CLIMATIZADOR_KEY);
  if (datos) {
    try {
      const historico = JSON.parse(datos);
      return filtrarPorTiempo(historico);
    } catch (e) {
      console.error('Error al parsear histórico del climatizador:', e);
      return [];
    }
  }
  return [];
}

/**
 * Guarda el histórico de estados del climatizador en localStorage
 * Filtra automáticamente para guardar solo datos de los últimos 5 minutos
 * @param {Array} historico - Array con datos de estados
 */
function guardarHistoricoClimatizador(historico) {
  // Filtrar antes de guardar para evitar almacenar datos antiguos innecesarios
  const historicoFiltrado = filtrarPorTiempo(historico);
  localStorage.setItem(CLIMATIZADOR_KEY, JSON.stringify(historicoFiltrado));
}

/**
 * Agrega un nuevo estado al histórico del climatizador
 * Filtra automáticamente datos más antiguos de 5 minutos
 * @param {string} estado - 'encendido' o 'apagado'
 * @returns {Array} Histórico actualizado
 */
function agregarEstadoClimatizador(estado) {
  let historico = cargarHistoricoClimatizador();

  const ahora = new Date();
  const timestamp = ahora.toLocaleTimeString('es-ES');

  // Convertir estado a valor numérico para la gráfica
  const valor = estado === 'encendido' ? 1 : 0;

  historico.push({
    estado: estado,
    valor: valor,
    timestamp: timestamp,
    fecha_completa: ahora.toISOString()
  });

  // Filtrar datos más antiguos de 5 minutos
  historico = filtrarPorTiempo(historico);

  guardarHistoricoClimatizador(historico);
  return historico;
}

/**
 * Crea o actualiza la gráfica del climatizador
 */
function actualizarGraficaClimatizador() {
  const estado = obtenerEstadoClimatizador();

  if (estado === null) {
    console.log('No se pudo obtener estado del climatizador');
    return;
  }

  const historico = agregarEstadoClimatizador(estado);

  const labels = historico.map(d => d.timestamp);
  const datos = historico.map(d => d.valor);

  const ctx = document.getElementById('climatizadorChart');

  if (!ctx) {
    console.error('No se encontró el canvas del climatizador');
    return;
  }

  if (chartClimatizador) {
    // Actualizar gráfica existente
    chartClimatizador.data.labels = labels;
    chartClimatizador.data.datasets[0].data = datos;
    chartClimatizador.update();
  } else {
    // Crear nueva gráfica
    chartClimatizador = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Estado',
          data: datos,
          borderColor: 'rgb(46, 204, 113)',
          backgroundColor: 'rgba(46, 204, 113, 0.2)',
          stepped: 'before',
          fill: true,
          pointRadius: 5,
          pointHoverRadius: 7,
          pointBackgroundColor: function(context) {
            const valor = context.parsed.y;
            return valor === 1 ? 'rgb(46, 204, 113)' : 'rgb(149, 165, 166)';
          }
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        aspectRatio: 3,
        plugins: {
          legend: {
            display: true,
            position: 'top'
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            callbacks: {
              label: function(context) {
                const valor = context.parsed.y;
                const estado = valor === 1 ? 'ENCENDIDO' : 'APAGADO';
                return 'Estado: ' + estado;
              }
            }
          }
        },
        scales: {
          y: {
            min: -0.2,
            max: 1.2,
            ticks: {
              stepSize: 1,
              callback: function(value) {
                if (value === 1) return 'ENCENDIDO';
                if (value === 0) return 'APAGADO';
                return '';
              }
            },
            title: {
              display: true,
              text: 'Estado del Sistema'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Hora'
            },
            ticks: {
              maxRotation: 45,
              minRotation: 45
            }
          }
        }
      }
    });
  }
}


// ==================== INICIALIZACIÓN ====================

/**
 * Inicializa todas las gráficas cuando el DOM está listo
 */
function inicializarGraficas() {
  actualizarGraficaTemperatura();
  actualizarGraficaClimatizador();
}

// Ejecutar cuando el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', inicializarGraficas);
