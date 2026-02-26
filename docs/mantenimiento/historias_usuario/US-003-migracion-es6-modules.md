# US-003: Migrar JavaScript a Módulos ES6

**Epic:** Modernización Frontend
**Prioridad:** P1 - Alto
**Story Points:** 8
**Sprint:** 3
**Estado:** 📋 Planificado

---

## Historia de Usuario

**Como** desarrollador frontend
**Quiero** migrar el código JavaScript de variables globales a módulos ES6
**Para** eliminar la contaminación del namespace global, hacer las dependencias explícitas y mejorar la mantenibilidad

---

## Contexto Técnico

### Problema Actual

**10 archivos JavaScript** usando variables globales para comunicación:

```javascript
// config.js - Exporta 11 variables globales
/* exported INTERVALO_MS, UMBRAL_OBSOLETO_MS, VENTANA_TIEMPO_MS,
   TEMPERATURA_KEY, CLIMATIZADOR_KEY, RANGO_PREFERENCIA_KEY,
   RANGOS_TIEMPO, CONFIG_REINTENTOS, REGLAS_VALIDACION,
   TOOLTIPS_BATERIA, ESTADOS_CONEXION */

// app.js - Depende de 17+ funciones globales
/* global INTERVALO_MS, validarDatos, obtenerEstado, actualizarValor,
   actualizarBadge, actualizarCardBateria, ... */
```

**Problemas:**
- ❌ Namespace global contaminado (30+ variables)
- ❌ Orden de carga de scripts crítico (rompe si se cambia)
- ❌ Dependencias implícitas (difícil saber quién usa qué)
- ❌ No se puede usar tree-shaking (dead code elimination)
- ❌ Incompatible con bundlers modernos (Webpack, Vite)
- ❌ Acoplamiento alto (todos dependen de globals)

**Estructura actual:**

```html
<!-- base.html - Orden crítico -->
<script src="{{ url_for('static', filename='js/config.js') }}"></script>
<script src="{{ url_for('static', filename='js/dom-utils.js') }}"></script>
<script src="{{ url_for('static', filename='js/validacion.js') }}"></script>
<script src="{{ url_for('static', filename='js/api.js') }}"></script>
<script src="{{ url_for('static', filename='js/bateria.js') }}"></script>
<script src="{{ url_for('static', filename='js/conexion.js') }}"></script>
<!-- ... 5 scripts más ... -->
<script src="{{ url_for('static', filename='js/app.js') }}"></script> <!-- DEBE ser último -->
```

### Solución Propuesta

**Migrar a módulos ES6** con imports/exports explícitos:

```javascript
// config.js
export const INTERVALO_MS = 10000;
export const CONFIG_REINTENTOS = { ... };

// api.js
import { CONFIG_REINTENTOS } from './config.js';

export async function obtenerEstado() {
    // ...
}

// app.js
import { obtenerEstado } from './api.js';
import { validarDatos } from './validacion.js';
import { INTERVALO_MS } from './config.js';
```

**Template actualizado:**

```html
<!-- base.html - Un solo entry point -->
<script type="module" src="{{ url_for('static', filename='js/app.js') }}"></script>
```

---

## Criterios de Aceptación

### ✅ Funcionales

1. **[CRÍTICO]** Todas las funcionalidades JavaScript funcionan:
   - [ ] Actualización automática cada 10 segundos
   - [ ] Reintentos automáticos en fallos de API
   - [ ] Validación de datos con reglas configuradas
   - [ ] Indicadores de tendencia y diferencia
   - [ ] Gestión de estado de conexión
   - [ ] Banner de desconexión
   - [ ] Notificaciones de reconexión
   - [ ] Gráficas de temperatura y climatizador
   - [ ] Selector de rango de tiempo
   - [ ] Tooltips de Bootstrap

2. **[ALTO]** Compatibilidad navegadores:
   - [ ] Chrome 90+ ✓
   - [ ] Firefox 88+ ✓
   - [ ] Safari 14+ ✓
   - [ ] Edge 90+ ✓
   - [ ] Mensaje de error en navegadores antiguos

### ✅ No Funcionales

3. **[CRÍTICO]** Calidad de código:
   - [ ] ESLint sin errores ni warnings
   - [ ] 0 variables globales (excepto polyfills necesarios)
   - [ ] Todas las dependencias explícitas (import/export)
   - [ ] Orden de scripts irrelevante

4. **[ALTO]** Arquitectura de módulos:
   - [ ] Cada módulo exporta solo lo público
   - [ ] Dependencias unidireccionales (no circulares)
   - [ ] Separación clara de responsabilidades
   - [ ] Cohesión alta por módulo

5. **[MEDIO]** Performance:
   - [ ] Bundle size total < 100KB
   - [ ] Tiempo de carga < 500ms (3G)
   - [ ] Sin impacto en LCP (Largest Contentful Paint)

### ✅ Documentación

6. **[ALTO]** Documentación técnica:
   - [ ] README actualizado con info de módulos ES6
   - [ ] Comentarios JSDoc en funciones exportadas
   - [ ] Diagrama de dependencias de módulos

---

## Tareas Técnicas

### 1. Preparación (1 hora)

- [ ] Crear rama: `feature/US-003-es6-modules`
- [ ] Backup de archivos JS actuales
- [ ] Crear `webapp/static/js/polyfills.js` para navegadores antiguos
- [ ] Configurar ESLint para módulos ES6:
  ```json
  {
    "parserOptions": {
      "ecmaVersion": 2020,
      "sourceType": "module"
    }
  }
  ```

### 2. Migrar config.js (30 min)

**Antes:**
```javascript
/* exported INTERVALO_MS, CONFIG_REINTENTOS, ... */
const INTERVALO_MS = 10000;
const CONFIG_REINTENTOS = { ... };
```

**Después:**
```javascript
export const INTERVALO_MS = 10000;
export const UMBRAL_OBSOLETO_MS = 30000;
export const CONFIG_REINTENTOS = {
    maxReintentos: 3,
    timeouts: [2000, 4000, 8000]
};
export const REGLAS_VALIDACION = { ... };
export const TOOLTIPS_BATERIA = { ... };
export const ESTADOS_CONEXION = { ... };
export const RANGOS_TIEMPO = { ... };
```

### 3. Migrar dom-utils.js (30 min)

**Antes:**
```javascript
/* exported actualizarValor, actualizarBadge, tiempoTranscurrido */
function actualizarValor(elementId, valor, sufijo) { ... }
```

**Después:**
```javascript
export function actualizarValor(elementId, valor, sufijo) {
    // ...
}

export function actualizarBadge(elementId, valor, claseBase) {
    // ...
}

export function tiempoTranscurrido(timestamp) {
    // ...
}
```

### 4. Migrar validacion.js (30 min)

**Antes:**
```javascript
/* global REGLAS_VALIDACION */
/* exported validarDatos */
function validarDatos(datos) { ... }
```

**Después:**
```javascript
import { REGLAS_VALIDACION } from './config.js';

export function validarDatos(datos) {
    // ...
}

function validarCampo(campo, valor) {
    // ... (privada, no exportada)
}
```

### 5. Migrar api.js (1 hora)

**Antes:**
```javascript
/* global CONFIG_REINTENTOS, mostrarReintentando */
/* exported obtenerEstado */
async function obtenerEstado() { ... }
```

**Después:**
```javascript
import { CONFIG_REINTENTOS } from './config.js';
import { mostrarReintentando } from './conexion.js';

export async function obtenerEstado() {
    // ...
}

function fetchConTimeout(url, timeout) {
    // ... (privada)
}
```

### 6. Migrar bateria.js (30 min)

**Antes:**
```javascript
/* global TOOLTIPS_BATERIA, $ */
/* exported actualizarCardBateria */
```

**Después:**
```javascript
import { TOOLTIPS_BATERIA } from './config.js';

export function actualizarCardBateria(indicador) {
    // ...
    // jQuery sigue siendo global (dependencia externa)
}
```

### 7. Migrar conexion.js (1.5 horas)

**Antes:**
```javascript
/* global ESTADOS_CONEXION, CONFIG_REINTENTOS, tiempoTranscurrido, UMBRAL_OBSOLETO_MS */
/* exported mostrarReintentando, actualizarEstadoConexion, ... */
```

**Después:**
```javascript
import { ESTADOS_CONEXION, CONFIG_REINTENTOS, UMBRAL_OBSOLETO_MS } from './config.js';
import { tiempoTranscurrido } from './dom-utils.js';

export function mostrarReintentando(visible, intento) {
    // ...
}

export function actualizarEstadoConexion(estado) {
    // ...
}

// ... otras exportaciones

// Variables privadas del módulo
let ultimaActualizacion = null;
let estadoAnterior = 'online';
let bannerCerradoManualmente = false;
```

### 8. Migrar módulos restantes (2 horas)

- [ ] `tendencia.js` → imports/exports
- [ ] `diferencia.js` → imports/exports
- [ ] `historial.js` → imports/exports
- [ ] Módulos de gráficas (si existen)

### 9. Migrar app.js - Entry Point (2 horas)

**Antes:**
```javascript
/* global INTERVALO_MS, validarDatos, obtenerEstado, actualizarValor, ... */
function actualizarDatos() { ... }
```

**Después:**
```javascript
// Entry point - importa todo lo necesario
import { INTERVALO_MS } from './config.js';
import { obtenerEstado } from './api.js';
import { validarDatos } from './validacion.js';
import { actualizarValor, actualizarBadge } from './dom-utils.js';
import {
    actualizarEstadoConexion,
    actualizarTimestamp,
    mostrarActualizando,
    inicializarBannerCerrar,
    setUltimaActualizacion,
    getUltimaActualizacion
} from './conexion.js';
import { actualizarCardBateria } from './bateria.js';
import { actualizarIndicadorTendencia } from './tendencia.js';
import { actualizarDiferencia } from './diferencia.js';
import {
    actualizarGraficaTemperatura,
    actualizarGraficaClimatizador
} from './graficas.js';
import {
    inicializarSelectorRango,
    cambiarRangoGrafica
} from './historial.js';

// Variables privadas del módulo
let intervalId = null;
let timestampIntervalId = null;

// Funciones privadas
function procesarDatosRecibidos(datosOriginales) {
    // ...
}

function manejarFalloConexion() {
    // ...
}

async function actualizarDatos() {
    // ...
}

function iniciarActualizacion() {
    // ...
}

// Exportar solo lo público (para tests)
export function detenerActualizacion() {
    // ...
}

// Auto-inicialización
document.addEventListener('DOMContentLoaded', iniciarActualizacion);
```

### 10. Actualizar Templates (1 hora)

**Antes (base.html):**
```html
<script src="{{ url_for('static', filename='js/config.js') }}"></script>
<script src="{{ url_for('static', filename='js/dom-utils.js') }}"></script>
<!-- ... 8 scripts más ... -->
<script src="{{ url_for('static', filename='js/app.js') }}"></script>
```

**Después:**
```html
<!-- Polyfill para navegadores antiguos (opcional) -->
<script nomodule>
    alert('Tu navegador no soporta módulos ES6. Por favor actualiza a Chrome 90+, Firefox 88+ o Safari 14+');
</script>

<!-- Entry point único -->
<script type="module" src="{{ url_for('static', filename='js/app.js') }}"></script>
```

### 11. Testing Manual (2 horas)

- [ ] Probar en Chrome 90+
- [ ] Probar en Firefox 88+
- [ ] Probar en Safari 14+
- [ ] Probar en Edge 90+
- [ ] Probar con DevTools cerrados (producción-like)
- [ ] Verificar console sin errores
- [ ] Verificar Network tab (scripts cargados correctamente)
- [ ] Probar todas las funcionalidades:
  - Actualización automática
  - Gráficas
  - Banner de desconexión
  - Tooltips
  - Selector de rango

### 12. Actualizar ESLint (1 hora)

- [ ] Actualizar `.eslintrc.json`:
  ```json
  {
    "env": {
      "browser": true,
      "es2020": true
    },
    "parserOptions": {
      "ecmaVersion": 2020,
      "sourceType": "module"
    },
    "rules": {
      "no-var": "error",
      "prefer-const": "warn",
      "no-implicit-globals": "error"
    }
  }
  ```

- [ ] Ejecutar: `npm run lint:js`
- [ ] Corregir todos los warnings

### 13. Documentación (1.5 horas)

- [ ] Actualizar `README.md`:
  - Sección "Tecnologías Frontend"
  - Requisitos de navegador

- [ ] Crear `docs/frontend-arquitectura.md`:
  - Diagrama de dependencias entre módulos
  - Explicación de cada módulo
  - Convenciones de imports/exports

- [ ] JSDoc en funciones exportadas:
  ```javascript
  /**
   * Obtiene el estado del termostato desde la API con reintentos
   * @returns {Promise<Object>} Datos del estado
   * @throws {Error} Si todos los reintentos fallan
   */
  export async function obtenerEstado() {
      // ...
  }
  ```

---

## Estimación

| Tarea | Horas | Complejidad |
|-------|-------|-------------|
| Preparación | 1 | Baja |
| config.js | 0.5 | Baja |
| dom-utils.js | 0.5 | Baja |
| validacion.js | 0.5 | Baja |
| api.js | 1 | Media |
| bateria.js | 0.5 | Baja |
| conexion.js | 1.5 | Alta |
| Módulos restantes | 2 | Media |
| app.js | 2 | Alta |
| Templates | 1 | Baja |
| Testing manual | 2 | Media |
| ESLint | 1 | Baja |
| Documentación | 1.5 | Baja |
| **TOTAL** | **15 horas** | - |

**Story Points:** 8 (Fibonacci: 8 ≈ 1.5-2 días)

---

## Definición de Hecho (DoD)

- [x] Código revisado por desarrollador frontend senior
- [x] ESLint sin errores ni warnings
- [x] 0 variables globales (excepto jQuery, Bootstrap)
- [x] Probado en Chrome, Firefox, Safari, Edge
- [x] Documentación actualizada
- [x] ADR-003 marcado como "Implementado"
- [x] Desplegado en staging
- [x] Pruebas manuales exitosas

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Incompatibilidad navegadores antiguos | Baja | Medio | Mensaje de advertencia claro |
| Dependencias circulares | Media | Alto | Diagrama de dependencias antes de empezar |
| Regresión funcional | Media | Crítico | Testing exhaustivo en todos los navegadores |
| jQuery como global | Alta | Bajo | Aceptable (dependencia externa) |

---

## Dependencias

### Bloquea a:
- US-008: Patrón Observer (más fácil con modules)

### Depende de:
- Ninguna (puede ejecutarse independientemente)

---

## Referencias

- ADR-003: Módulos ES6
- [MDN: JavaScript Modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)
- [Can I Use: ES6 Modules](https://caniuse.com/es6-module)

---

**Asignado a:** Equipo de desarrollo
**Fecha Inicio:** 2026-02-26
**Fecha Fin Real:** 2026-02-26
**Estado Actual:** ✅ Completado
