/**
 * Modulo de diferencia de temperatura (WT-11)
 * Calcula y muestra la diferencia entre temperatura actual y deseada
 */

/**
 * Calcula la diferencia y determina el estado
 * @param {number} tempActual - Temperatura ambiente actual
 * @param {number} tempDeseada - Temperatura objetivo
 * @returns {Object} { diferencia, diffAbsoluta, estado, porcentaje, texto }
 */
function calcularDiferencia(tempActual, tempDeseada) {
    const diferencia = tempActual - tempDeseada;
    const diffAbsoluta = Math.abs(diferencia);

    // Determinar estado: frio (actual < deseada), ok (cerca), calor (actual > deseada)
    let estado;
    if (diffAbsoluta <= 0.5) {
        estado = 'ok';
    } else if (diferencia < 0) {
        estado = 'frio';  // Actual esta por debajo de deseada
    } else {
        estado = 'calor'; // Actual esta por encima de deseada
    }

    // Calcular porcentaje para la barra (max 5C de diferencia = 0%)
    const maxDiff = 5;
    const porcentaje = Math.max(0, Math.min(100, (1 - diffAbsoluta / maxDiff) * 100));

    // Generar texto descriptivo
    let texto;
    if (diffAbsoluta <= 0.5) {
        texto = 'Temperatura en objetivo';
    } else if (diferencia < 0) {
        texto = '+' + diffAbsoluta.toFixed(1) + '\u00B0C para alcanzar objetivo';
    } else {
        texto = '-' + diffAbsoluta.toFixed(1) + '\u00B0C para alcanzar objetivo';
    }

    return {
        diferencia: diferencia,
        diffAbsoluta: diffAbsoluta,
        estado: estado,
        porcentaje: porcentaje,
        texto: texto
    };
}

/**
 * Actualiza el indicador de diferencia en el DOM
 * @param {number} tempActual - Temperatura ambiente actual
 * @param {number} tempDeseada - Temperatura objetivo
 */
export function actualizarDiferencia(tempActual, tempDeseada) {
    const resultado = calcularDiferencia(tempActual, tempDeseada);

    // Actualizar texto
    const textoEl = document.getElementById('diferencia-texto');
    if (textoEl) {
        textoEl.textContent = resultado.texto;
        textoEl.className = 'diferencia-texto ' + resultado.estado;
    }

    // Actualizar barra de progreso
    const barraEl = document.getElementById('diferencia-barra');
    if (barraEl) {
        barraEl.style.width = resultado.porcentaje + '%';
        barraEl.className = 'diferencia-barra ' + resultado.estado;
    }
}
