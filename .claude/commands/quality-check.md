# Quality Check Command

Ejecuta analisis completo de calidad de codigo Python y activos web.

## Uso

```
/quality-check [ruta]
```

Si no se especifica ruta, analiza todo el proyecto.

## Instrucciones para el Agente

Cuando el usuario ejecute este comando, debes:

1. **Identificar el objetivo**:
   - Si se proporciona `$ARGUMENTS`, usar esa ruta
   - Si no, analizar el directorio actual (`.`)

### Analisis Python

2. **Ejecutar el script de metricas Python**:
   ```bash
   python quality/scripts/calculate_metrics.py $TARGET
   ```

### Analisis Web

3. **Ejecutar el script de metricas web** (si existen archivos web):
   ```bash
   python quality/scripts/calculate_web_metrics.py .
   ```

### Resumen y Validacion

4. **Mostrar el resumen unificado al usuario** con:
   - Grado general Python (A/B/C/F)
   - Grado general Web (A/B/C/F)
   - Estado de cada quality gate (PASS/FAIL)
   - Metricas clave de ambos analisis

5. **Si hay gates fallidos**, ejecutar validacion detallada:
   ```bash
   python quality/scripts/validate_gates.py quality/reports/quality_*.json
   ```

6. **Proporcionar recomendaciones** especificas para mejorar el codigo:
   - Indicar archivos/funciones problematicos
   - Sugerir acciones concretas de refactorizacion

## Ejemplo de Salida Esperada

```
ANALISIS DE CALIDAD - webapp_termostato
=======================================

=== PYTHON ===
Grado: A | Gates: 3/3

- Complejidad (CC): 1.08 [PASS]
- Mantenibilidad (MI): 100.0 [PASS]
- Pylint Score: 9.67/10 [PASS]

=== WEB ===
Grado: A | Gates: 3/3

- HTML: 0 errores, 0 warnings [PASS]
- CSS: 0 errores, 0 warnings [PASS]
- JS: 0 errores, CC max: 8 [PASS]

=== GENERAL ===
Grado Combinado: A
Gates Totales: 6/6

Estado: El codigo cumple con todos los estandares de calidad.
```

## Variables Disponibles

- `$ARGUMENTS`: Argumentos pasados al comando (ej: ruta del archivo/directorio)
