/**
 * Modulo de actualizacion automatica sin recarga de pagina.
 * Reemplaza el meta refresh por AJAX polling.
 * WT-12: Actualizacion sin recarga de pagina
 * WT-10: Estado de conexion visible
 * WT-9: Indicadores visuales de tendencia
 */
/* global actualizarGraficaTemperatura, actualizarGraficaClimatizador, TEMPERATURA_KEY */
/* exported detenerActualizacion */

const INTERVALO_MS = 10000; // 10 segundos
const UMBRAL_OBSOLETO_MS = 30000; // 30 segundos para considerar datos obsoletos
// TEMPERATURA_KEY ya definida en graficas.js (se carga primero)
let intervalId = null;
let timestampIntervalId = null;
let ultimaActualizacion = null;
// WT-19: Estado anterior para detectar reconexion
let estadoAnterior = 'online';
let bannerCerradoManualmente = false;

/**
 * WT-21: Reglas de validacion para cada campo de la API
 */
const REGLAS_VALIDACION = {
    temperatura_ambiente: { tipo: 'number', min: 0, max: 50 },
    temperatura_deseada: { tipo: 'number', min: 15, max: 30 },
    carga_bateria: { tipo: 'number', min: 0, max: 5 },
    indicador: { tipo: 'enum', valores: ['NORMAL', 'BAJO', 'CRITICO'] },
    estado_climatizador: { tipo: 'enum', valores: ['apagado', 'encendido', 'enfriando', 'calentando'] }
};

/**
 * WT-21: Valida un campo segun sus reglas
 * @returns {Object} {valido: boolean, valor: any, error: string|null}
 */
function validarCampo(campo, valor) {
    const regla = REGLAS_VALIDACION[campo];
    if (!regla) {
        return { valido: true, valor: valor, error: null };
    }

    // Validar tipo
    if (regla.tipo === 'number') {
        if (typeof valor !== 'number' || isNaN(valor)) {
            console.warn('WT-21: Campo "' + campo + '" tipo invalido. Esperado: number, Recibido:', typeof valor, valor);
            return { valido: false, valor: 'Error', error: 'tipo_invalido' };
        }
        if (valor < regla.min || valor > regla.max) {
            console.warn('WT-21: Campo "' + campo + '" fuera de rango [' + regla.min + '-' + regla.max + ']. Valor:', valor);
            return { valido: false, valor: 'N/A', error: 'fuera_de_rango' };
        }
    } else if (regla.tipo === 'enum') {
        const valorNormalizado = String(valor).toUpperCase();
        const valoresUpper = regla.valores.map(function(v) { return v.toUpperCase(); });
        if (valoresUpper.indexOf(valorNormalizado) === -1) {
            console.warn('WT-21: Campo "' + campo + '" valor invalido. Esperado:', regla.valores, 'Recibido:', valor);
            return { valido: false, valor: 'Error', error: 'valor_invalido' };
        }
    }

    return { valido: true, valor: valor, error: null };
}

/**
 * WT-21: Valida todos los datos recibidos de la API
 * @returns {Object} Datos validados con valores corregidos si es necesario
 */
function validarDatos(datos) {
    const datosValidados = {};
    let hayErrores = false;

    for (const campo in REGLAS_VALIDACION) {
        if (REGLAS_VALIDACION.hasOwnProperty(campo)) {
            const resultado = validarCampo(campo, datos[campo]);
            datosValidados[campo] = resultado.valor;
            if (!resultado.valido) {
                hayErrores = true;
            }
        }
    }

    return { datos: datosValidados, hayErrores: hayErrores };
}

/**
 * Obtiene el estado del termostato desde el endpoint /api/estado
 */
async function obtenerEstado() {
    const response = await fetch('/api/estado');
    return response.json();
}

/**
 * Actualiza un valor en el DOM si ha cambiado
 * WT-21: Marca valores invalidos con clase especial
 */
function actualizarValor(elementId, valor, sufijo = '') {
    const elemento = document.getElementById(elementId);
    if (elemento) {
        const valorFormateado = valor + sufijo;
        const esInvalido = (valor === 'N/A' || valor === 'Error');

        if (elemento.textContent !== valorFormateado) {
            elemento.textContent = valorFormateado;
            // WT-21: Marcar si es valor invalido
            elemento.classList.toggle('valor-invalido', esInvalido);
            // Efecto visual de cambio
            elemento.classList.add('valor-actualizado');
            setTimeout(() => elemento.classList.remove('valor-actualizado'), 300);
        }
    }
}

/**
 * Actualiza un badge de estado (climatizador o indicador bateria)
 * WT-21: Maneja valores invalidos
 */
function actualizarBadge(elementId, valor, claseBase) {
    const elemento = document.getElementById(elementId);
    if (elemento) {
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
            setTimeout(() => elemento.classList.remove('valor-actualizado'), 300);
        }
    }
}

/**
 * WT-18: Configuracion de tooltips segun nivel de bateria
 */
const TOOLTIPS_BATERIA = {
    normal: 'Bateria con carga suficiente',
    bajo: 'Bateria baja - Considere recargar pronto',
    critico: 'Bateria critica - Riesgo de apagado inminente'
};

/**
 * WT-18: Actualiza la card de bateria segun el nivel del indicador
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

/**
 * WT-10: Calcula el tiempo transcurrido en formato legible
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

/**
 * WT-19: Muestra u oculta el banner de perdida de conexion
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
 * WT-19: Muestra notificacion de reconexion
 */
function mostrarNotificacionReconexion() {
    const notificacion = document.getElementById('notificacion-reconexion');
    if (!notificacion) return;

    notificacion.classList.remove('oculto');
    // Ocultar automaticamente despues de 3 segundos
    setTimeout(function() {
        notificacion.classList.add('oculto');
    }, 3000);
}

/**
 * WT-19: Inicializa el boton de cerrar del banner
 */
function inicializarBannerCerrar() {
    const botonCerrar = document.querySelector('.banner-cerrar');
    if (botonCerrar) {
        botonCerrar.addEventListener('click', function() {
            bannerCerradoManualmente = true;
            actualizarBannerConexion(false);
        });
    }
}

/**
 * WT-19: Configuracion visual para cada estado de conexion
 */
const ESTADOS_CONEXION = {
    online: {
        clase: 'online',
        icono: 'glyphicon-ok',
        texto: 'En línea',
        datosObsoletos: false,
        mostrarBanner: false
    },
    offline: {
        clase: 'offline',
        icono: 'glyphicon-remove',
        texto: 'Sin conexión',
        datosObsoletos: true,
        mostrarBanner: true
    },
    obsoleto: {
        clase: 'obsoleto',
        icono: 'glyphicon-warning-sign',
        texto: 'Datos desactualizados',
        datosObsoletos: true,
        mostrarBanner: true
    }
};

/**
 * WT-19: Detecta y maneja la reconexion
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
 * WT-10: Actualiza el indicador de estado de conexion
 * WT-19: Gestiona banner y notificaciones de reconexion
 */
function actualizarEstadoConexion(estado) {
    const contenedor = document.getElementById('estado-conexion');
    const icono = document.getElementById('icono-estado');
    const texto = document.getElementById('texto-estado');
    const dashboardContainer = document.querySelector('.dashboard-container');
    const config = ESTADOS_CONEXION[estado];

    if (!contenedor || !icono || !texto || !config) return;

    manejarReconexion(estado);

    // Remover clases previas
    contenedor.classList.remove('online', 'offline', 'obsoleto');
    icono.classList.remove('glyphicon-ok', 'glyphicon-remove', 'glyphicon-warning-sign');

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
 * WT-10: Actualiza el timestamp mostrado
 * WT-19: Actualiza tambien el tiempo en el banner
 */
function actualizarTimestamp() {
    const timestampEl = document.getElementById('timestamp-estado');
    const bannerTiempo = document.getElementById('banner-tiempo');

    if (timestampEl && ultimaActualizacion) {
        const textoTiempo = tiempoTranscurrido(ultimaActualizacion);
        timestampEl.textContent = 'Actualizado ' + textoTiempo;

        // WT-19: Actualizar tiempo en el banner si esta visible
        if (bannerTiempo) {
            bannerTiempo.textContent = 'Ultimo dato: ' + textoTiempo;
        }

        // Verificar si los datos estan obsoletos (> 30s)
        const tiempoSinActualizar = Date.now() - ultimaActualizacion;
        if (tiempoSinActualizar > UMBRAL_OBSOLETO_MS) {
            actualizarEstadoConexion('obsoleto');
        }
    }
}

/**
 * WT-10: Muestra/oculta el icono de actualizacion
 */
function mostrarActualizando(visible) {
    const icono = document.getElementById('icono-estado');
    if (icono) {
        if (visible) {
            icono.classList.remove('glyphicon-ok', 'glyphicon-remove', 'glyphicon-warning-sign');
            icono.classList.add('glyphicon-refresh', 'actualizando');
        } else {
            icono.classList.remove('glyphicon-refresh', 'actualizando');
        }
    }
}

/**
 * WT-9: Obtiene el historico de temperaturas desde localStorage
 */
function obtenerHistoricoTemperatura() {
    try {
        const datos = localStorage.getItem(TEMPERATURA_KEY);
        return datos ? JSON.parse(datos) : [];
    } catch (e) {
        return [];
    }
}

/**
 * WT-9: Calcula la tendencia basada en las ultimas lecturas
 * @returns {Object} {direccion: 'subiendo'|'bajando'|'estable', acercando: boolean}
 */
function calcularTendencia(tempActual, tempDeseada) {
    const historico = obtenerHistoricoTemperatura();

    // Necesitamos al menos 3 lecturas para calcular tendencia
    if (historico.length < 3) {
        return { direccion: 'estable', acercando: null };
    }

    // Obtener ultimas 3 lecturas
    const ultimas = historico.slice(-3);
    const temperaturas = ultimas.map(h => h.temperatura);

    // Calcular promedio de diferencias
    let sumaDiferencias = 0;
    for (let i = 1; i < temperaturas.length; i++) {
        sumaDiferencias += temperaturas[i] - temperaturas[i - 1];
    }
    const promedioDiff = sumaDiferencias / (temperaturas.length - 1);

    // Determinar direccion
    let direccion = 'estable';
    if (promedioDiff > 0.2) {
        direccion = 'subiendo';
    } else if (promedioDiff < -0.2) {
        direccion = 'bajando';
    }

    // Determinar si se acerca o aleja de la deseada
    let acercando = null;
    if (tempActual !== null && tempDeseada !== null) {
        const diffActual = Math.abs(tempActual - tempDeseada);
        const diffAnterior = Math.abs(temperaturas[0] - tempDeseada);
        if (diffActual < diffAnterior - 0.1) {
            acercando = true;
        } else if (diffActual > diffAnterior + 0.1) {
            acercando = false;
        }
    }

    return { direccion, acercando };
}

/**
 * WT-9: Actualiza la flecha de tendencia
 */
function actualizarFlechaTendencia(flechaEl, tendencia) {
    flechaEl.classList.remove('subiendo', 'bajando', 'estable', 'acercando', 'alejando');
    flechaEl.classList.remove('glyphicon', 'glyphicon-arrow-up', 'glyphicon-arrow-down', 'glyphicon-minus');
    flechaEl.classList.add('glyphicon');

    const clasesFlecha = {
        'subiendo': ['glyphicon-arrow-up', 'subiendo'],
        'bajando': ['glyphicon-arrow-down', 'bajando'],
        'estable': ['glyphicon-minus', 'estable']
    };
    const clases = clasesFlecha[tendencia.direccion] || clasesFlecha['estable'];
    flechaEl.classList.add(...clases);

    if (tendencia.acercando === true) flechaEl.classList.add('acercando');
    if (tendencia.acercando === false) flechaEl.classList.add('alejando');

    flechaEl.classList.add('cambio');
    setTimeout(() => flechaEl.classList.remove('cambio'), 300);
}

/**
 * WT-9: Actualiza el icono del climatizador
 */
function actualizarIconoClimatizador(iconoEl, estadoClimatizador) {
    iconoEl.classList.remove('enfriando', 'calentando', 'apagado', 'encendido');
    iconoEl.classList.remove('glyphicon', 'glyphicon-asterisk', 'glyphicon-fire', 'glyphicon-off', 'glyphicon-ok');
    iconoEl.classList.add('glyphicon');

    const clasesIcono = {
        'enfriando': ['glyphicon-asterisk', 'enfriando'],
        'calentando': ['glyphicon-fire', 'calentando'],
        'encendido': ['glyphicon-ok', 'encendido'],
        'apagado': ['glyphicon-off', 'apagado']
    };
    const clases = clasesIcono[estadoClimatizador] || clasesIcono['apagado'];
    iconoEl.classList.add(...clases);
}

/**
 * WT-9: Genera el texto descriptivo de tendencia
 */
function generarTextoTendencia(tempActual, tempDeseada, estadoClimatizador, direccion) {
    const textos = {
        'enfriando': 'Enfriando hacia ' + tempDeseada + '°C',
        'calentando': 'Calentando hacia ' + tempDeseada + '°C'
    };
    if (textos[estadoClimatizador]) return textos[estadoClimatizador];
    if (direccion === 'subiendo') return 'Subiendo hacia ' + tempDeseada + '°C';
    if (direccion === 'bajando') return 'Bajando hacia ' + tempDeseada + '°C';
    if (Math.abs(tempActual - tempDeseada) < 1) return 'Temperatura estable en objetivo';
    return '';
}

/**
 * WT-9: Actualiza los indicadores visuales de tendencia
 */
function actualizarIndicadorTendencia(tempActual, tempDeseada, estadoClimatizador) {
    const flechaEl = document.getElementById('tendencia-flecha');
    const iconoEl = document.getElementById('tendencia-icono');
    const textoEl = document.getElementById('tendencia-texto');

    if (!flechaEl || !iconoEl || !textoEl) return;

    const tendencia = calcularTendencia(tempActual, tempDeseada);

    actualizarFlechaTendencia(flechaEl, tendencia);
    actualizarIconoClimatizador(iconoEl, estadoClimatizador);

    const textoDescriptivo = generarTextoTendencia(
        tempActual, tempDeseada, estadoClimatizador, tendencia.direccion
    );
    textoEl.textContent = textoDescriptivo;
    textoEl.classList.toggle('activo', textoDescriptivo !== '');
}

/**
 * WT-21: Procesa y muestra los datos recibidos de la API
 */
function procesarDatosRecibidos(datosOriginales) {
    const validacion = validarDatos(datosOriginales);
    const datos = validacion.datos;

    // Actualizar valores numericos (con datos validados)
    actualizarValor('valor-temp-ambiente', datos.temperatura_ambiente, '');
    actualizarValor('valor-temp-deseada', datos.temperatura_deseada, '');
    actualizarValor('valor-bateria', datos.carga_bateria, '');

    // Actualizar badges de estado (con datos validados)
    actualizarBadge('badge-climatizador', datos.estado_climatizador, 'estado-badge');
    actualizarBadge('badge-indicador', datos.indicador, 'nivel-badge');

    // WT-18: Actualizar card de bateria (solo si indicador es valido)
    if (typeof datos.indicador === 'string' && datos.indicador !== 'Error') {
        actualizarCardBateria(datosOriginales.indicador);
    }

    // Actualizar graficas y tendencia solo si los datos son validos
    if (!validacion.hayErrores) {
        if (typeof actualizarGraficaTemperatura === 'function') {
            actualizarGraficaTemperatura();
        }
        if (typeof actualizarGraficaClimatizador === 'function') {
            actualizarGraficaClimatizador();
        }
        actualizarIndicadorTendencia(
            datosOriginales.temperatura_ambiente,
            datosOriginales.temperatura_deseada,
            datosOriginales.estado_climatizador
        );
    }
}

/**
 * WT-19: Maneja el caso de fallo de conexion
 */
function manejarFalloConexion() {
    if (!ultimaActualizacion) {
        ultimaActualizacion = Date.now();
    }
    actualizarEstadoConexion('offline');
    actualizarTimestamp();
}

/**
 * Funcion principal que obtiene datos y actualiza el DOM
 */
async function actualizarDatos() {
    try {
        mostrarActualizando(true);
        const resultado = await obtenerEstado();

        if (resultado.success) {
            procesarDatosRecibidos(resultado.data);
            ultimaActualizacion = Date.now();
            actualizarEstadoConexion(resultado.from_cache ? 'offline' : 'online');
            actualizarTimestamp();
        } else {
            manejarFalloConexion();
        }
    } catch (error) {
        console.error('Error actualizando datos:', error);
        manejarFalloConexion();
    } finally {
        // WT-10: Ocultar icono de actualizacion
        mostrarActualizando(false);
    }
}

/**
 * Inicia el ciclo de actualizacion automatica
 */
function iniciarActualizacion() {
    // WT-19: Inicializar boton de cerrar del banner
    inicializarBannerCerrar();

    // WT-19: Verificar conexion inmediatamente al iniciar
    actualizarDatos();

    // Configurar intervalo de datos
    intervalId = setInterval(actualizarDatos, INTERVALO_MS);

    // WT-10: Configurar intervalo para actualizar timestamp cada segundo
    timestampIntervalId = setInterval(actualizarTimestamp, 1000);

    // WT-8: Inicializar tooltips de Bootstrap
    if (typeof $ !== 'undefined' && $.fn.tooltip) {
        $('[data-toggle="tooltip"]').tooltip();
    }

    // WT-9: Inicializar indicador de tendencia con valores del DOM
    const tempAmbEl = document.getElementById('valor-temp-ambiente');
    const tempDesEl = document.getElementById('valor-temp-deseada');
    const badgeClimEl = document.getElementById('badge-climatizador');
    if (tempAmbEl && tempDesEl && badgeClimEl) {
        const tempAmb = parseFloat(tempAmbEl.textContent) || 0;
        const tempDes = parseFloat(tempDesEl.textContent) || 0;
        const estadoClim = badgeClimEl.textContent.toLowerCase().trim();
        actualizarIndicadorTendencia(tempAmb, tempDes, estadoClim);
    }

    console.log('Actualizacion automatica iniciada (intervalo: ' + INTERVALO_MS + 'ms)');
}

/**
 * Detiene el ciclo de actualizacion
 */
function detenerActualizacion() {
    if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
    }
    // WT-10: Detener actualizacion de timestamp
    if (timestampIntervalId) {
        clearInterval(timestampIntervalId);
        timestampIntervalId = null;
    }
    console.log('Actualizacion automatica detenida');
}

// Iniciar cuando el DOM este listo
document.addEventListener('DOMContentLoaded', iniciarActualizacion);
