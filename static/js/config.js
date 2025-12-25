/**
 * Configuracion global del modulo de actualizacion
 * WT-23: Refactorizacion modular
 */
/* exported INTERVALO_MS, UMBRAL_OBSOLETO_MS, VENTANA_TIEMPO_MS, TEMPERATURA_KEY,
   CLIMATIZADOR_KEY, CONFIG_REINTENTOS, REGLAS_VALIDACION, TOOLTIPS_BATERIA,
   ESTADOS_CONEXION */

// Intervalos de tiempo
const INTERVALO_MS = 10000; // 10 segundos entre actualizaciones
const UMBRAL_OBSOLETO_MS = 30000; // 30 segundos para considerar datos obsoletos

// Configuracion de graficas
const VENTANA_TIEMPO_MS = 5 * 60 * 1000; // 5 minutos en milisegundos
const TEMPERATURA_KEY = 'temperatura_historico';
const CLIMATIZADOR_KEY = 'climatizador_historico';

// WT-22: Configuracion de reintentos
const CONFIG_REINTENTOS = {
    maxReintentos: 3,
    timeouts: [2000, 4000, 8000] // Timeout progresivo en ms
};

// WT-21: Reglas de validacion para cada campo de la API
const REGLAS_VALIDACION = {
    temperatura_ambiente: { tipo: 'number', min: 0, max: 50 },
    temperatura_deseada: { tipo: 'number', min: 15, max: 30 },
    carga_bateria: { tipo: 'number', min: 0, max: 5 },
    indicador: { tipo: 'enum', valores: ['NORMAL', 'BAJO', 'CRITICO'] },
    estado_climatizador: { tipo: 'enum', valores: ['apagado', 'encendido', 'enfriando', 'calentando'] }
};

// WT-18: Configuracion de tooltips segun nivel de bateria
const TOOLTIPS_BATERIA = {
    normal: 'Bateria con carga suficiente',
    bajo: 'Bateria baja - Considere recargar pronto',
    critico: 'Bateria critica - Riesgo de apagado inminente'
};

// WT-19: Configuracion visual para cada estado de conexion
const ESTADOS_CONEXION = {
    online: {
        clase: 'online',
        icono: 'glyphicon-ok',
        texto: 'En linea',
        datosObsoletos: false,
        mostrarBanner: false
    },
    offline: {
        clase: 'offline',
        icono: 'glyphicon-remove',
        texto: 'Sin conexion',
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
