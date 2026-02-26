/**
 * Modulo de gestion del estado de conexion
 * WT-10: Estado de conexion visible
 * WT-19: Alerta visual de perdida de conexion
 * WT-22: Indicador de reintentando
 * WT-23: Refactorizacion modular
 */
import { ESTADOS_CONEXION, CONFIG_REINTENTOS, UMBRAL_OBSOLETO_MS } from './config.js';
import { tiempoTranscurrido } from './dom-utils.js';

// Estado del modulo
let ultimaActualizacion = null;
let estadoAnterior = 'online';
let bannerCerradoManualmente = false;

/**
 * Obtiene el timestamp de la ultima actualizacion
 * @returns {number|null} Timestamp o null
 */
export function getUltimaActualizacion() {
    return ultimaActualizacion;
}

/**
 * Establece el timestamp de la ultima actualizacion
 * @param {number} timestamp - Nuevo timestamp
 */
export function setUltimaActualizacion(timestamp) {
    ultimaActualizacion = timestamp;
}

/**
 * Muestra u oculta el banner de perdida de conexion
 * @param {boolean} mostrar - Si mostrar u ocultar el banner
 */
function actualizarBannerConexion(mostrar) {
    const banner = document.getElementById('banner-conexion');
    const bannerTiempo = document.getElementById('banner-tiempo');
    if (!banner) return;

    if (mostrar && !bannerCerradoManualmente) {
        banner.classList.remove('oculto');
        document.body.classList.add('banner-visible');
        if (bannerTiempo && ultimaActualizacion) {
            bannerTiempo.textContent = 'Ultimo dato: ' + tiempoTranscurrido(ultimaActualizacion);
        }
    } else {
        banner.classList.add('oculto');
        document.body.classList.remove('banner-visible');
    }
}

/**
 * Muestra notificacion de reconexion
 */
function mostrarNotificacionReconexion() {
    const notificacion = document.getElementById('notificacion-reconexion');
    if (!notificacion) return;

    notificacion.classList.remove('oculto');
    setTimeout(function() {
        notificacion.classList.add('oculto');
    }, 3000);
}

/**
 * Inicializa el boton de cerrar del banner
 */
export function inicializarBannerCerrar() {
    const botonCerrar = document.querySelector('.banner-cerrar');
    if (botonCerrar) {
        botonCerrar.addEventListener('click', function() {
            bannerCerradoManualmente = true;
            actualizarBannerConexion(false);
        });
    }
}

/**
 * Detecta y maneja la reconexion
 * @param {string} estadoNuevo - Nuevo estado de conexion
 */
function manejarReconexion(estadoNuevo) {
    const eraDesconectado = (estadoAnterior === 'offline' || estadoAnterior === 'obsoleto');
    const ahoraConectado = (estadoNuevo === 'online');
    if (eraDesconectado && ahoraConectado) {
        mostrarNotificacionReconexion();
        bannerCerradoManualmente = false;
    }
}

/**
 * Muestra/oculta el indicador de reintentando
 * @param {boolean} visible - Si mostrar el indicador
 * @param {number} intento - Numero de intento actual
 */
export function mostrarReintentando(visible, intento) {
    const contenedor = document.getElementById('estado-conexion');
    const icono = document.getElementById('icono-estado');
    const texto = document.getElementById('texto-estado');

    if (!contenedor || !icono || !texto) return;

    if (visible) {
        contenedor.classList.remove('online', 'offline', 'obsoleto');
        contenedor.classList.add('reintentando');
        icono.classList.remove('glyphicon-ok', 'glyphicon-remove', 'glyphicon-warning-sign');
        icono.classList.add('glyphicon-refresh', 'actualizando');
        texto.textContent = 'Reintentando... (' + intento + '/' + CONFIG_REINTENTOS.maxReintentos + ')';
    }
}

/**
 * Actualiza el indicador de estado de conexion
 * @param {string} estado - Estado de conexion ('online', 'offline', 'obsoleto')
 */
export function actualizarEstadoConexion(estado) {
    const contenedor = document.getElementById('estado-conexion');
    const icono = document.getElementById('icono-estado');
    const texto = document.getElementById('texto-estado');
    const dashboardContainer = document.querySelector('.dashboard-container');
    const config = ESTADOS_CONEXION[estado];

    if (!contenedor || !icono || !texto || !config) return;

    manejarReconexion(estado);

    // Remover clases previas
    contenedor.classList.remove('online', 'offline', 'obsoleto', 'reintentando');
    icono.classList.remove('glyphicon-ok', 'glyphicon-remove', 'glyphicon-warning-sign', 'glyphicon-refresh', 'actualizando');

    // Aplicar nueva configuracion
    contenedor.classList.add(config.clase);
    icono.classList.add(config.icono);
    texto.textContent = config.texto;

    if (dashboardContainer) {
        dashboardContainer.classList.toggle('datos-obsoletos', config.datosObsoletos);
    }
    actualizarBannerConexion(config.mostrarBanner);

    estadoAnterior = estado;
}

/**
 * Actualiza el timestamp mostrado
 */
export function actualizarTimestamp() {
    const timestampEl = document.getElementById('timestamp-estado');
    const bannerTiempo = document.getElementById('banner-tiempo');

    if (timestampEl && ultimaActualizacion) {
        const textoTiempo = tiempoTranscurrido(ultimaActualizacion);
        timestampEl.textContent = 'Actualizado ' + textoTiempo;

        if (bannerTiempo) {
            bannerTiempo.textContent = 'Ultimo dato: ' + textoTiempo;
        }

        // Verificar si los datos estan obsoletos
        const tiempoSinActualizar = Date.now() - ultimaActualizacion;
        if (tiempoSinActualizar > UMBRAL_OBSOLETO_MS) {
            actualizarEstadoConexion('obsoleto');
        }
    }
}

/**
 * Muestra/oculta el icono de actualizacion
 * @param {boolean} visible - Si mostrar el icono
 */
export function mostrarActualizando(visible) {
    const icono = document.getElementById('icono-estado');
    if (!icono) return;

    if (visible) {
        icono.classList.remove('glyphicon-ok', 'glyphicon-remove', 'glyphicon-warning-sign');
        icono.classList.add('glyphicon-refresh', 'actualizando');
    } else {
        icono.classList.remove('glyphicon-refresh', 'actualizando');
    }
}
