# Plan de Implementación — US-003: Migrar JavaScript a Módulos ES6

**Fecha:** 2026-02-26
**Story Points:** 8
**Branch:** feature/US-003-es6-modules
**Estado:** ✅ COMPLETADO
**Fecha completado:** 2026-02-26

## Grafo de dependencias

```
config.js          (hoja, sin imports)
dom-utils.js       (hoja, sin imports)
diferencia.js      (hoja, sin imports)
validacion.js      → config.js
bateria.js         → config.js
tendencia.js       → config.js
historial.js       → config.js
graficas/config.js → config.js
conexion.js        → config.js, dom-utils.js
graficas/climatizador.js → config.js, graficas/config.js
graficas/temperatura.js  → config.js, graficas/config.js, historial.js
api.js             → config.js, conexion.js
app.js             → todos los anteriores (entry point)
```

## Tareas

| # | Tarea | Archivos | Complejidad | Estado |
|---|-------|----------|-------------|--------|
| T1 | Actualizar `.eslintrc.json` con `"sourceType": "module"` | `.eslintrc.json` | Baja | ⬜ |
| T2 | Migrar `config.js` | `config.js` | Baja | ⬜ |
| T3 | Migrar `dom-utils.js` | `dom-utils.js` | Baja | ⬜ |
| T4 | Migrar `diferencia.js` | `diferencia.js` | Baja | ⬜ |
| T5 | Migrar `validacion.js` | `validacion.js` | Baja | ⬜ |
| T6 | Migrar `bateria.js` | `bateria.js` | Baja | ⬜ |
| T7 | Migrar `tendencia.js` | `tendencia.js` | Baja | ⬜ |
| T8 | Migrar `historial.js` | `historial.js` | Media | ⬜ |
| T9 | Migrar `graficas/config.js` | `graficas/config.js` | Baja | ⬜ |
| T10 | Migrar `conexion.js` | `conexion.js` | Media | ⬜ |
| T11 | Migrar `graficas/climatizador.js` | `graficas/climatizador.js` | Media | ⬜ |
| T12 | Migrar `graficas/temperatura.js` | `graficas/temperatura.js` | Alta | ⬜ |
| T13 | Migrar `api.js` | `api.js` | Media | ⬜ |
| T14 | Migrar `app.js` (entry point) | `app.js` | Alta | ⬜ |
| T15 | Actualizar `index.html` | `index.html` | Baja | ⬜ |
| T16 | Ejecutar ESLint y corregir warnings | — | Media | ⬜ |
| T17 | Ejecutar suite pytest (regresión backend) | — | Baja | ⬜ |

## Invariantes críticos

- `$` y `jQuery` siguen siendo globales (Bootstrap/jQuery — dependencia externa)
- `Chart` sigue siendo global (Chart.js — dependencia externa)
- Ningún módulo exporta más de lo necesario
- No hay dependencias circulares

## Tareas completadas

| # | Tarea | Estado |
|---|-------|--------|
| T1 | Actualizar `.eslintrc.json` con `"sourceType": "module"` | ✅ |
| T2–T14 | Migrar 13 archivos JS a ES6 modules (exports/imports explícitos) | ✅ |
| T15 | Actualizar `index.html` → 1 `<script type="module">` + `<script nomodule>` | ✅ |
| T16 | ESLint: 0 errores, 0 warnings | ✅ |
| T17 | Pytest: 181/181, coverage 95% | ✅ |

## Métricas finales

| Métrica | Resultado |
|---------|-----------|
| Tests nuevos | 80 (60 unitarios + 13 integración + 7 BDD) |
| Tests totales | 181/181 ✅ |
| Coverage | 95% |
| Pylint | 8.73/10 |
| ESLint | 0 errores, 0 warnings |
| Variables globales JS eliminadas | 30+ → 0 (excepto jQuery, Chart) |
| Scripts en HTML | 11 → 1 |
