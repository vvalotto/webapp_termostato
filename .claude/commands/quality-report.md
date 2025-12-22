# Quality Report Command

Genera un reporte completo de calidad de codigo Python y web en formato Markdown.

## Uso

```
/quality-report
```

## Instrucciones para el Agente

Cuando el usuario ejecute este comando, debes:

1. **Ejecutar analisis completo del proyecto**:
   ```bash
   python quality/scripts/calculate_metrics.py .
   python quality/scripts/calculate_web_metrics.py .
   ```

2. **Leer los archivos JSON generados** en `quality/reports/`:
   - `quality_*.json` (metricas Python)
   - `quality_web_*.json` (metricas Web)

3. **Generar un reporte Markdown detallado** que incluya:

### Estructura del Reporte

```markdown
# Reporte de Calidad de Codigo

**Proyecto:** webapp_termostato
**Fecha:** [fecha actual]
**Grado General Python:** [A/B/C/F]
**Grado General Web:** [A/B/C/F]

## Resumen Ejecutivo

- Quality Gates Python: X/3
- Quality Gates Web: X/3
- Gates Totales: X/6
- Issues Bloqueantes: N

---

## METRICAS PYTHON

## Metricas de Tamanio

| Metrica | Valor |
|---------|-------|
| Total LOC | XXX |
| Source LOC | XXX |
| Comentarios | XX% |

## Analisis de Complejidad

| Metrica | Valor |
|---------|-------|
| CC Promedio | X.X |
| CC Maximo | X |
| Funcion mas compleja | [nombre] |

### Distribucion por Grado
- A (1-5): XX funciones
- B (6-10): XX funciones
- C (11-20): XX funciones

## Indice de Mantenibilidad

| Metrica | Valor |
|---------|-------|
| MI Promedio | XX.X |
| MI Minimo | XX.X |
| Modulos bajo umbral | X |

## Analisis Pylint

| Metrica | Valor |
|---------|-------|
| Score | X.X/10 |
| Errores | X |
| Warnings | X |

## Quality Gates Python

| Gate | Estado | Valor | Umbral |
|------|--------|-------|--------|
| Complejidad | PASS/FAIL | X.X | <= 10 |
| Mantenibilidad | PASS/FAIL | XX.X | > 20 |
| Pylint | PASS/FAIL | X.X | >= 8.0 |

---

## METRICAS WEB

## Analisis HTML

| Metrica | Valor |
|---------|-------|
| Archivos analizados | X |
| Errores | X |
| Warnings | X |

## Analisis CSS

| Metrica | Valor |
|---------|-------|
| Archivos analizados | X |
| Errores | X |
| Warnings | X |

## Analisis JavaScript

| Metrica | Valor |
|---------|-------|
| Archivos analizados | X |
| Errores | X |
| Warnings | X |
| Complejidad maxima | X |

## Quality Gates Web

| Gate | Estado | Valor | Umbral |
|------|--------|-------|--------|
| HTML Errores | PASS/FAIL | X | 0 |
| CSS Errores | PASS/FAIL | X | 0 |
| JS Errores | PASS/FAIL | X | 0 |
| JS Complejidad | PASS/FAIL | X | <= 10 |

---

## Recomendaciones

[Lista de mejoras sugeridas basadas en los gates fallidos]
```

4. **Guardar el reporte** en `quality/reports/quality_report_[fecha].md`

5. **Mostrar resumen al usuario** con ubicacion del archivo generado

## Notas

- Este comando es util para documentacion y revisiones de codigo
- El reporte puede compartirse con el equipo
- Usar antes de releases o pull requests importantes
- Incluye metricas tanto de Python como de activos web (HTML/CSS/JS)
