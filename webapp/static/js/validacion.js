/**
 * Modulo de validacion de datos de la API
 * WT-21: Validacion de datos de la API
 * WT-23: Refactorizacion modular
 */
import { REGLAS_VALIDACION } from './config.js';

/**
 * Valida un campo segun sus reglas
 * @param {string} campo - Nombre del campo a validar
 * @param {any} valor - Valor a validar
 * @returns {Object} {valido: boolean, valor: any, error: string|null}
 */
function validarCampo(campo, valor) {
    const regla = REGLAS_VALIDACION[campo];
    if (!regla) {
        return { valido: true, valor: valor, error: null };
    }

    // Validar tipo numerico
    if (regla.tipo === 'number') {
        if (typeof valor !== 'number' || isNaN(valor)) {
            console.warn('WT-21: Campo "' + campo + '" tipo invalido. Esperado: number, Recibido:', typeof valor, valor);
            return { valido: false, valor: 'Error', error: 'tipo_invalido' };
        }
        if (valor < regla.min || valor > regla.max) {
            console.warn('WT-21: Campo "' + campo + '" fuera de rango [' + regla.min + '-' + regla.max + ']. Valor:', valor);
            return { valido: false, valor: 'N/A', error: 'fuera_de_rango' };
        }
    }

    // Validar tipo enumerado
    if (regla.tipo === 'enum') {
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
 * Valida todos los datos recibidos de la API
 * @param {Object} datos - Datos recibidos de la API
 * @returns {Object} Datos validados con valores corregidos si es necesario
 */
export function validarDatos(datos) {
    const datosValidados = {};
    let hayErrores = false;

    for (const campo in REGLAS_VALIDACION) {
        if (Object.prototype.hasOwnProperty.call(REGLAS_VALIDACION, campo)) {
            const resultado = validarCampo(campo, datos[campo]);
            datosValidados[campo] = resultado.valor;
            if (!resultado.valido) {
                hayErrores = true;
            }
        }
    }

    return { datos: datosValidados, hayErrores: hayErrores };
}
