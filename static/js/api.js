/**
 * Modulo de comunicacion con la API
 * WT-22: Reintentos automaticos en API
 * WT-23: Refactorizacion modular
 */
/* global CONFIG_REINTENTOS, mostrarReintentando */
/* exported obtenerEstado */

let intentoActual = 0;

/**
 * Fetch con timeout
 * @param {string} url - URL a consultar
 * @param {number} timeout - Timeout en milisegundos
 * @returns {Promise} Promesa con la respuesta
 */
function fetchConTimeout(url, timeout) {
    return Promise.race([
        fetch(url),
        new Promise(function(_, reject) {
            setTimeout(function() {
                reject(new Error('Timeout'));
            }, timeout);
        })
    ]);
}

/**
 * Obtiene el estado con reintentos automaticos
 * @returns {Promise<Object>} Datos del estado
 * @throws {Error} Si todos los reintentos fallan
 */
async function obtenerEstado() {
    intentoActual = 0;

    while (intentoActual < CONFIG_REINTENTOS.maxReintentos) {
        const timeout = CONFIG_REINTENTOS.timeouts[intentoActual];
        try {
            const response = await fetchConTimeout('/api/estado', timeout);
            const data = await response.json();

            // Verificar si la respuesta indica exito
            if (data.success) {
                intentoActual = 0;
                return data;
            }

            // API respondio pero con error, reintentar
            throw new Error('API retorno success=false');
        } catch (error) {
            intentoActual++;
            console.warn('WT-22: Intento ' + intentoActual + ' fallido:', error.message);

            if (intentoActual < CONFIG_REINTENTOS.maxReintentos) {
                if (typeof mostrarReintentando === 'function') {
                    mostrarReintentando(true, intentoActual);
                }
                // Esperar antes del siguiente reintento (backoff)
                await new Promise(function(resolve) {
                    setTimeout(resolve, 500 * intentoActual);
                });
            }
        }
    }

    // Todos los reintentos fallaron
    throw new Error('Todos los reintentos fallaron');
}
