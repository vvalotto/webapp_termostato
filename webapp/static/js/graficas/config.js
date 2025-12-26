/**
 * Configuracion compartida para graficas Chart.js
 * WT-23: Refactorizacion modular
 */
/* global VENTANA_TIEMPO_MS */
/* exported filtrarPorTiempo, crearOpcionesBase */

/**
 * Filtra un historico para mantener solo los datos de los ultimos 5 minutos
 * @param {Array} historico - Array con datos historicos
 * @returns {Array} Array filtrado con datos recientes
 */
function filtrarPorTiempo(historico) {
    const ahora = new Date().getTime();
    return historico.filter(function(item) {
        const fechaItem = new Date(item.fecha_completa).getTime();
        const diferencia = ahora - fechaItem;
        return diferencia <= VENTANA_TIEMPO_MS;
    });
}

/**
 * Crea las opciones base para las graficas
 * @param {string} tituloY - Titulo del eje Y
 * @returns {Object} Opciones de configuracion de Chart.js
 */
function crearOpcionesBase(tituloY) {
    return {
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
                title: {
                    display: true,
                    text: tituloY
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
    };
}
