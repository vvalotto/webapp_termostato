# Reporte de Calidad de Codigo

**Proyecto:** webapp_termostato
**Fecha:** 2025-12-27
**Version:** 2.0.0
**Hito:** Despliegue en Google Cloud Platform

| Metrica | Valor |
|---------|-------|
| **Grado General Python** | A |
| **Grado General Web** | A |
| **Quality Gates Totales** | 6/6 |

---

## Resumen Ejecutivo

| Categoria | Gates Pasados | Estado |
|-----------|---------------|--------|
| Python | 3/3 | PASS |
| Web | 3/3 | PASS |
| **Total** | **6/6** | **PASS** |

**Issues Bloqueantes:** 0

---

## METRICAS PYTHON

### Metricas de Tamanio

| Metrica | Valor |
|---------|-------|
| Total LOC | 1939 |
| Source LOC | 1340 |
| Comentarios | 106 |
| Lineas en blanco | 374 |
| Ratio comentarios | 5.47% |

### Analisis de Complejidad

| Metrica | Valor |
|---------|-------|
| CC Promedio | 4.45 |
| CC Maximo | 15 |
| Funcion mas compleja | `calculate_metrics.py:178 calcular_pylint_score` |
| Total funciones | 67 |

#### Distribucion por Grado

| Grado | Rango CC | Funciones |
|-------|----------|-----------|
| A | 1-5 | 47 |
| B | 6-10 | 18 |
| C | 11-20 | 2 |
| D | 21-30 | 0 |
| E | 31-40 | 0 |
| F | 40+ | 0 |

### Indice de Mantenibilidad

| Metrica | Valor |
|---------|-------|
| MI Promedio | 68.41 |
| MI Minimo | 33.73 |
| Archivo con MI minimo | `calculate_web_metrics.py` |
| Modulos bajo umbral (< 20) | 0 |

### Analisis Pylint

| Metrica | Valor |
|---------|-------|
| Score | 8.74/10 |
| Errores | 3 |
| Warnings | 14 |
| Refactor | 0 |
| Convencion | 0 |
| Total mensajes | 17 |

### Quality Gates Python

| Gate | Estado | Valor | Umbral |
|------|--------|-------|--------|
| Complejidad | PASS | 4.45 | <= 10 |
| Mantenibilidad | PASS | 68.41 | > 20 |
| Pylint | PASS | 8.74 | >= 8.0 |

---

## METRICAS WEB

### Analisis HTML

| Metrica | Valor |
|---------|-------|
| Archivos analizados | 4 (templates/) |
| Errores | 0 |
| Warnings | 0 |

### Analisis CSS

| Metrica | Valor |
|---------|-------|
| Archivos analizados | 5 (static/css/) |
| Errores | 0 |
| Warnings | 0 |

### Analisis JavaScript

| Metrica | Valor |
|---------|-------|
| Archivos analizados | 5 (static/js/) |
| Errores | 0 |
| Warnings | 0 |
| Complejidad maxima | 0 |

### Quality Gates Web

| Gate | Estado | Valor | Umbral |
|------|--------|-------|--------|
| HTML Errores | PASS | 0 | 0 |
| CSS Errores | PASS | 0 | 0 |
| JS Errores | PASS | 0 | 0 |

---

## Entorno de Produccion

| Componente | URL |
|------------|-----|
| Frontend | https://webapp-termostato-1090421346746.us-central1.run.app |
| Backend | https://app-termostato-1090421346746.us-central1.run.app |

**Plataforma:** Google Cloud Run
**Region:** us-central1
**CI/CD:** GitHub -> Cloud Build -> Cloud Run

---

## Cobertura de Tests

| Metrica | Valor |
|---------|-------|
| Cobertura | 100% |
| Tests unitarios | Si |
| Tests de integracion | Si |

---

## Conclusiones

El proyecto **webapp_termostato v2.0.0** cumple con todos los quality gates establecidos:

1. **Codigo Python de alta calidad**: Grado A con CC promedio de 4.45 y MI de 68.41
2. **Activos web limpios**: Sin errores en HTML, CSS ni JavaScript
3. **Pylint satisfactorio**: Score de 8.74/10
4. **Cobertura completa**: 100% de cobertura en tests
5. **Despliegue exitoso**: Aplicacion funcionando en Google Cloud Run con CI/CD

El proyecto esta listo para produccion.

---

*Reporte generado automaticamente el 2025-12-27*
