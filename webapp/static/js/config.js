/**
 * Configuracion global del modulo de actualizacion
 * WT-23: Refactorizacion modular
 */

// Intervalos de tiempo
export const INTERVALO_MS = 10000; // 10 segundos entre actualizaciones
export const UMBRAL_OBSOLETO_MS = 30000; // 30 segundos para considerar datos obsoletos

// Configuracion de graficas
export const VENTANA_TIEMPO_MS = 5 * 60 * 1000; // 5 minutos en milisegundos
export const TEMPERATURA_KEY = 'temperatura_historico';
export const CLIMATIZADOR_KEY = 'climatizador_historico';
export const RANGO_PREFERENCIA_KEY = 'grafica_rango_preferido';

// WT-15: Rangos de tiempo disponibles para graficas
export const RANGOS_TIEMPO = {
    '5min': { label: '5 min', ms: 5 * 60 * 1000, usaAPI: false },
    '1h': { label: '1 hora', ms: 60 * 60 * 1000, usaAPI: true, limite: 60 },
    '6h': { label: '6 horas', ms: 6 * 60 * 60 * 1000, usaAPI: true, limite: 360 },
    '24h': { label: '24 horas', ms: 24 * 60 * 60 * 1000, usaAPI: true, limite: 1440 }
};

// WT-22: Configuracion de reintentos
export const CONFIG_REINTENTOS = {
    maxReintentos: 3,
    timeouts: [2000, 4000, 8000] // Timeout progresivo en ms
};

// WT-21: Reglas de validacion para cada campo de la API
export const REGLAS_VALIDACION = {
    temperatura_ambiente: { tipo: 'number', min: 0, max: 50 },
    temperatura_deseada: { tipo: 'number', min: 15, max: 30 },
    carga_bateria: { tipo: 'number', min: 0, max: 5 },
    indicador: { tipo: 'enum', valores: ['NORMAL', 'BAJO', 'CRITICO'] },
    estado_climatizador: { tipo: 'enum', valores: ['apagado', 'encendido', 'enfriando', 'calentando'] }
};

// WT-18: Configuracion de tooltips segun nivel de bateria
export const TOOLTIPS_BATERIA = {
    normal: 'Bateria con carga suficiente',
    bajo: 'Bateria baja - Considere recargar pronto',
    critico: 'Bateria critica - Riesgo de apagado inminente'
};

// WT-19: Configuracion visual para cada estado de conexion
export const ESTADOS_CONEXION = {
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
