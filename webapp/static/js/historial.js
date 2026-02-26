/**
 * Modulo de historial de temperatura (WT-15)
 * Maneja la obtencion de datos historicos desde la API
 */
import { RANGOS_TIEMPO, RANGO_PREFERENCIA_KEY } from './config.js';

let rangoActual = '5min';

/**
 * Obtiene el rango guardado en localStorage o el default
 * @returns {string} Clave del rango actual
 */
export function getRangoActual() {
    const guardado = localStorage.getItem(RANGO_PREFERENCIA_KEY);
    if (guardado && RANGOS_TIEMPO[guardado]) {
        return guardado;
    }
    return '5min';
}

/**
 * Guarda el rango seleccionado en localStorage
 * @param {string} rango - Clave del rango a guardar
 */
export function setRangoActual(rango) {
    if (RANGOS_TIEMPO[rango]) {
        rangoActual = rango;
        localStorage.setItem(RANGO_PREFERENCIA_KEY, rango);
    }
}

/**
 * Obtiene el historial de temperaturas desde la API
 * @param {number} limite - Numero maximo de registros
 * @returns {Promise<Array>} Array con datos del historial
 */
export async function obtenerHistorialAPI(limite) {
    try {
        const response = await fetch('/api/historial?limite=' + limite);
        const data = await response.json();

        if (data.success && data.historial) {
            // Transformar formato de API a formato de grafica
            const historial = data.historial.map(function(item) {
                const fecha = new Date(item.timestamp);
                return {
                    temperatura: item.temperatura,
                    timestamp: fecha.toLocaleTimeString('es-ES', {
                        hour: '2-digit',
                        minute: '2-digit'
                    }),
                    fecha_completa: item.timestamp
                };
            });
            // Ordenar de mas antiguo a mas reciente (la API viene al reves)
            historial.sort(function(a, b) {
                return new Date(a.fecha_completa) - new Date(b.fecha_completa);
            });
            return historial;
        }
        return [];
    } catch (error) {
        console.error('Error obteniendo historial:', error);
        return [];
    }
}

/**
 * Muestra u oculta el indicador de carga
 * @param {boolean} mostrar - True para mostrar, false para ocultar
 */
function mostrarCargando(mostrar) {
    const el = document.getElementById('grafica-cargando');
    if (el) {
        if (mostrar) {
            el.classList.remove('oculto');
        } else {
            el.classList.add('oculto');
        }
    }
}

/**
 * Actualiza el estado visual de los botones del selector
 * @param {string} rangoSeleccionado - Clave del rango seleccionado
 */
function actualizarBotonesRango(rangoSeleccionado) {
    const botones = document.querySelectorAll('.btn-rango');
    botones.forEach(function(btn) {
        if (btn.dataset.rango === rangoSeleccionado) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

/**
 * Inicializa el selector de rango de tiempo
 * @param {Function} callbackCambioRango - Funcion a llamar cuando cambia el rango
 */
export function inicializarSelectorRango(callbackCambioRango) {
    // Cargar preferencia guardada
    rangoActual = getRangoActual();
    actualizarBotonesRango(rangoActual);

    // Configurar event listeners
    const selector = document.getElementById('rango-selector');
    if (selector) {
        selector.addEventListener('click', async function(e) {
            const btn = e.target.closest('.btn-rango');
            if (!btn || btn.classList.contains('active')) return;

            const nuevoRango = btn.dataset.rango;
            const config = RANGOS_TIEMPO[nuevoRango];

            if (!config) return;

            // Actualizar estado
            setRangoActual(nuevoRango);
            actualizarBotonesRango(nuevoRango);

            // Llamar callback con datos
            if (callbackCambioRango) {
                if (config.usaAPI) {
                    mostrarCargando(true);
                    const historial = await obtenerHistorialAPI(config.limite);
                    mostrarCargando(false);
                    callbackCambioRango(nuevoRango, historial);
                } else {
                    callbackCambioRango(nuevoRango, null);
                }
            }
        });
    }

    // Retornar rango inicial
    return rangoActual;
}
