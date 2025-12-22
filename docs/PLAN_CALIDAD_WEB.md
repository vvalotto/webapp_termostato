# Plan de Implementacion: Sistema de Calidad Web

**Proyecto:** webapp_termostato
**Fecha:** 2025-12-22
**Objetivo:** Extender el sistema de calidad de codigo Python con analisis de activos web (HTML, CSS, JavaScript)

---

## Resumen Ejecutivo

Este plan extiende el sistema de calidad existente para incluir analisis completo del frontend:
- **HTML**: Validacion, accesibilidad, semantica (htmlhint)
- **CSS**: Linting, especificidad, buenas practicas (stylelint)
- **JavaScript**: Linting, complejidad, errores (eslint)

### Activos Web del Proyecto

| Tipo | Ubicacion | Archivos | Lineas |
|------|-----------|----------|--------|
| HTML | `templates/` | 4 | ~174 |
| CSS | `static/styles.css` | 1 | 265 |
| JS | `static/js/graficas.js` | 1 | 397 |

---

## Fase 1: Preparacion del Entorno

**Objetivo:** Instalar herramientas y crear configuraciones base.

### Paso 1.1: Crear package.json

**Archivo:** `package.json`

```json
{
  "name": "webapp-termostato-quality",
  "version": "1.0.0",
  "description": "Herramientas de calidad web para webapp_termostato",
  "private": true,
  "scripts": {
    "lint:html": "htmlhint 'templates/**/*.html' --format json",
    "lint:css": "stylelint 'static/**/*.css' --formatter json",
    "lint:js": "eslint 'static/**/*.js' --format json",
    "lint:all": "npm run lint:html && npm run lint:css && npm run lint:js"
  },
  "devDependencies": {
    "htmlhint": "^1.1.4",
    "stylelint": "^16.0.0",
    "stylelint-config-standard": "^36.0.0",
    "eslint": "^8.56.0"
  }
}
```

**Comando de verificacion:**
```bash
npm install
npm run lint:all
```

### Paso 1.2: Crear configuracion HTMLHint

**Archivo:** `.htmlhintrc`

```json
{
  "tagname-lowercase": true,
  "attr-lowercase": true,
  "attr-value-double-quotes": true,
  "doctype-first": false,
  "tag-pair": true,
  "spec-char-escape": false,
  "id-unique": true,
  "src-not-empty": true,
  "attr-no-duplication": true,
  "title-require": true,
  "alt-require": true,
  "id-class-value": "dash",
  "space-tab-mixed-disabled": "space"
}
```

**Notas:**
- `doctype-first: false` - Los templates Jinja2 extienden base.html
- `spec-char-escape: false` - Evita falsos positivos con sintaxis Jinja2

### Paso 1.3: Crear configuracion Stylelint

**Archivo:** `.stylelintrc.json`

```json
{
  "extends": "stylelint-config-standard",
  "rules": {
    "indentation": 2,
    "string-quotes": "double",
    "no-duplicate-selectors": true,
    "color-hex-case": "lower",
    "color-hex-length": "short",
    "selector-max-id": 1,
    "selector-max-compound-selectors": 4,
    "max-nesting-depth": 3,
    "declaration-block-no-duplicate-properties": true,
    "no-descending-specificity": null,
    "font-family-name-quotes": "always-where-recommended",
    "property-no-vendor-prefix": null,
    "selector-class-pattern": null
  }
}
```

### Paso 1.4: Crear configuracion ESLint

**Archivo:** `.eslintrc.json`

```json
{
  "env": {
    "browser": true,
    "es2021": true
  },
  "parserOptions": {
    "ecmaVersion": "latest"
  },
  "globals": {
    "Chart": "readonly",
    "$": "readonly",
    "jQuery": "readonly"
  },
  "rules": {
    "no-unused-vars": "error",
    "no-undef": "error",
    "eqeqeq": "warn",
    "no-var": "warn",
    "prefer-const": "warn",
    "no-console": "off",
    "complexity": ["error", 10],
    "max-depth": ["error", 4],
    "max-lines-per-function": ["warn", 50],
    "max-params": ["warn", 4]
  }
}
```

**Notas:**
- `globals`: Chart.js y jQuery disponibles via CDN
- `no-console: off` - El proyecto usa console para debugging

### Paso 1.5: Actualizar .gitignore

**Agregar a:** `.gitignore`

```
# Node.js
node_modules/
package-lock.json
```

---

## Fase 2: Script de Metricas Web

**Objetivo:** Crear script Python que ejecuta los linters y procesa resultados.

### Paso 2.1: Crear calculate_web_metrics.py

**Archivo:** `quality/scripts/calculate_web_metrics.py`

**Estructura de la clase:**

```python
#!/usr/bin/env python3
"""
Calculador de metricas de calidad para activos web (HTML, CSS, JavaScript).
Sigue el patron de calculate_metrics.py para integracion con el sistema existente.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class CalculadorMetricasWeb:
    """Calcula metricas de calidad para activos web."""

    def __init__(self, ruta_objetivo="."):
        self.ruta_objetivo = Path(ruta_objetivo)
        self.metricas = {
            "timestamp": datetime.now().isoformat(),
            "objetivo": str(self.ruta_objetivo),
            "html": {},
            "css": {},
            "javascript": {},
            "resumen_web": {}
        }
        self.settings = self._cargar_settings()

    def _cargar_settings(self):
        """Carga configuracion de .claude/settings.json"""
        pass

    def verificar_dependencias(self):
        """Verifica que npm y los linters esten instalados."""
        pass

    def calcular_metricas_html(self):
        """Ejecuta htmlhint y procesa resultados."""
        # Comando: npx htmlhint templates/**/*.html --format json
        pass

    def calcular_metricas_css(self):
        """Ejecuta stylelint y procesa resultados."""
        # Comando: npx stylelint "static/**/*.css" --formatter json
        pass

    def calcular_metricas_javascript(self):
        """Ejecuta eslint y procesa resultados."""
        # Comando: npx eslint "static/**/*.js" --format json
        pass

    def generar_resumen_web(self):
        """Genera resumen con estado PASS/FAIL para cada gate."""
        pass

    def ejecutar_todo(self):
        """Ejecuta todos los analisis."""
        pass

    def guardar_json(self):
        """Guarda metricas en quality/reports/quality_web_TIMESTAMP.json"""
        pass

    def imprimir_resumen(self):
        """Imprime resumen en consola."""
        pass


if __name__ == "__main__":
    ruta = sys.argv[1] if len(sys.argv) > 1 else "."
    calculador = CalculadorMetricasWeb(ruta)

    if not calculador.verificar_dependencias():
        print("Error: Dependencias npm no instaladas. Ejecutar: npm install")
        sys.exit(2)

    exito = calculador.ejecutar_todo()
    calculador.guardar_json()
    calculador.imprimir_resumen()

    sys.exit(0 if exito else 1)
```

**Estructura de salida JSON:**

```json
{
  "timestamp": "2025-12-22T...",
  "objetivo": ".",
  "html": {
    "archivos_analizados": 4,
    "errores": 0,
    "warnings": 2,
    "detalle": []
  },
  "css": {
    "archivos_analizados": 1,
    "errores": 0,
    "warnings": 3,
    "total_reglas": 85,
    "detalle": []
  },
  "javascript": {
    "archivos_analizados": 1,
    "errores": 0,
    "warnings": 4,
    "complejidad_maxima": 8,
    "detalle": []
  },
  "resumen_web": {
    "grado": "A",
    "gates_pasados": 3,
    "gates_totales": 3,
    "quality_gates": {
      "html": { "estado": "PASS", "errores": 0, "umbral": 0 },
      "css": { "estado": "PASS", "errores": 0, "umbral": 0 },
      "javascript": { "estado": "PASS", "errores": 0, "umbral": 0 }
    }
  }
}
```

---

## Fase 3: Configuracion de Quality Gates

**Objetivo:** Agregar umbrales de calidad web al sistema.

### Paso 3.1: Modificar settings.json

**Archivo:** `.claude/settings.json`

**Agregar despues de `quality_gates`:**

```json
{
  "version": "1.0",
  "project_name": "webapp_termostato",
  "quality_gates": {
    "max_complexity": 10,
    "min_maintainability": 20,
    "min_pylint_score": 8.0,
    "max_function_lines": 50
  },
  "quality_gates_web": {
    "html": {
      "max_errors": 0,
      "max_warnings": 5
    },
    "css": {
      "max_errors": 0,
      "max_warnings": 10
    },
    "javascript": {
      "max_errors": 0,
      "max_warnings": 10,
      "max_complexity": 10
    }
  },
  "metrics": {
    "tools": {
      "complexity": "radon cc",
      "maintainability": "radon mi",
      "size": "radon raw",
      "linting": "pylint",
      "html_lint": "htmlhint",
      "css_lint": "stylelint",
      "js_lint": "eslint"
    },
    "output_dir": "quality/reports/"
  }
}
```

---

## Fase 4: Actualizacion del Agente

**Objetivo:** Extender quality-agent para incluir analisis web.

### Paso 4.1: Modificar quality-agent.md

**Archivo:** `.claude/agents/quality-agent.md`

**Cambios a realizar:**

1. **Actualizar description (linea 3):**
```yaml
description: Analiza calidad de codigo Python y activos web usando metricas esenciales (CC, MI, Pylint, HTMLHint, Stylelint, ESLint).
```

2. **Agregar metricas web a "Tu Mision" (despues de linea 15):**
```markdown
### Web (HTML/CSS/JavaScript)
5. **HTMLHint** - Validacion HTML y accesibilidad
6. **Stylelint** - Calidad y consistencia CSS
7. **ESLint** - Calidad y complejidad JavaScript
```

3. **Agregar "Paso 2b: Calcular Metricas Web" (despues de linea 46):**
```markdown
### Paso 2b: Calcular Metricas Web

Si existen archivos web en el proyecto:

```bash
# Verificar dependencias npm
npm list htmlhint stylelint eslint 2>/dev/null || npm install

# Ejecutar analisis web
python quality/scripts/calculate_web_metrics.py $TARGET
```
```

4. **Agregar tabla de Quality Gates Web (despues de linea 57):**
```markdown
### Quality Gates Web

| Metrica | Umbral | Accion si Falla |
|---------|--------|-----------------|
| HTML Errores | 0 | BLOQUEAR |
| HTML Warnings | <= 5 | ADVERTENCIA |
| CSS Errores | 0 | BLOQUEAR |
| CSS Warnings | <= 10 | ADVERTENCIA |
| JS Errores | 0 | BLOQUEAR |
| JS Complejidad | <= 10 | BLOQUEAR |
```

---

## Fase 5: Actualizacion de Comandos

**Objetivo:** Integrar analisis web en los comandos existentes.

### Paso 5.1: Modificar quality-check.md

**Archivo:** `.claude/commands/quality-check.md`

**Agregar seccion de analisis web:**

```markdown
## Instrucciones

### 1. Analisis Python
```bash
python quality/scripts/calculate_metrics.py $ARGUMENTS
```

### 2. Analisis Web (si existen archivos web)
```bash
python quality/scripts/calculate_web_metrics.py .
```

### 3. Mostrar Resumen Unificado

Formato de salida:

```
ANALISIS DE CALIDAD - webapp_termostato
=======================================

=== PYTHON ===
Grado: A | Gates: 3/3

=== WEB ===
Grado: A | Gates: 3/3
- HTML: 0 errores, 2 warnings
- CSS: 0 errores, 3 warnings
- JS: 0 errores, CC max: 8

=== GENERAL ===
Grado Combinado: A
Gates Totales: 6/6
```
```

### Paso 5.2: Modificar quality-report.md

**Archivo:** `.claude/commands/quality-report.md`

**Agregar generacion de seccion web en el reporte Markdown.**

---

## Fase 6: Integracion Final

**Objetivo:** Asegurar que todo funcione de forma integrada.

### Paso 6.1: Actualizar hook de pre-commit (opcional)

**Archivo:** `.claude/settings.json` - seccion hooks

**Agregar validacion web al hook:**

```json
"hooks": {
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "cmd=$(cat | jq -r '.tool_input.command'); if echo \"$cmd\" | grep -q 'git commit'; then python quality/scripts/calculate_metrics.py . && python quality/scripts/calculate_web_metrics.py . && python quality/scripts/validate_gates.py quality/reports/quality_*.json || exit 2; fi"
        }
      ]
    }
  ]
}
```

### Paso 6.2: Crear requirements-web.txt

**Archivo:** `quality/requirements-web.txt`

```
# Dependencias para analisis de calidad web
# Instalacion: npm install (ver package.json)
#
# Herramientas utilizadas:
# - htmlhint: Validacion HTML
# - stylelint: Linting CSS
# - eslint: Linting JavaScript
#
# Nota: Estas herramientas se instalan via npm, no pip
```

---

## Checklist de Implementacion

### Fase 1: Preparacion del Entorno
- [ ] 1.1 Crear `package.json`
- [ ] 1.2 Crear `.htmlhintrc`
- [ ] 1.3 Crear `.stylelintrc.json`
- [ ] 1.4 Crear `.eslintrc.json`
- [ ] 1.5 Actualizar `.gitignore`
- [ ] Ejecutar `npm install`
- [ ] Verificar `npm run lint:all`

### Fase 2: Script de Metricas Web
- [ ] 2.1 Crear `quality/scripts/calculate_web_metrics.py`
- [ ] Probar ejecucion: `python quality/scripts/calculate_web_metrics.py .`
- [ ] Verificar JSON generado en `quality/reports/`

### Fase 3: Configuracion de Quality Gates
- [ ] 3.1 Modificar `.claude/settings.json`
- [ ] Validar JSON con `python -m json.tool .claude/settings.json`

### Fase 4: Actualizacion del Agente
- [ ] 4.1 Modificar `.claude/agents/quality-agent.md`

### Fase 5: Actualizacion de Comandos
- [ ] 5.1 Modificar `.claude/commands/quality-check.md`
- [ ] 5.2 Modificar `.claude/commands/quality-report.md`
- [ ] Probar `/quality-check`
- [ ] Probar `/quality-report`

### Fase 6: Integracion Final
- [ ] 6.1 Actualizar hook de pre-commit (opcional)
- [ ] 6.2 Crear `quality/requirements-web.txt`
- [ ] Prueba completa end-to-end

---

## Salida Esperada

### Ejemplo de /quality-check

```
ANALISIS DE CALIDAD - webapp_termostato
=======================================

=== METRICAS PYTHON ===
Grado: A
Quality Gates: 3/3 pasaron

- Complejidad (CC): 1.08 [PASS]
- Mantenibilidad (MI): 100.0 [PASS]
- Pylint Score: 9.67/10 [PASS]

=== METRICAS WEB ===
Grado: A
Quality Gates: 3/3 pasaron

HTML (4 archivos):
- Errores: 0 [PASS]
- Warnings: 2 (umbral: 5)

CSS (1 archivo):
- Errores: 0 [PASS]
- Warnings: 3 (umbral: 10)

JavaScript (1 archivo):
- Errores: 0 [PASS]
- Complejidad max: 8 (umbral: 10) [PASS]

=== RESUMEN GENERAL ===
Grado Combinado: A
Quality Gates: 6/6 pasaron
Estado: El codigo cumple con todos los estandares de calidad.
```

---

## Archivos Creados/Modificados

### Archivos Nuevos (6)
| Archivo | Fase |
|---------|------|
| `package.json` | 1.1 |
| `.htmlhintrc` | 1.2 |
| `.stylelintrc.json` | 1.3 |
| `.eslintrc.json` | 1.4 |
| `quality/scripts/calculate_web_metrics.py` | 2.1 |
| `quality/requirements-web.txt` | 6.2 |

### Archivos Modificados (5)
| Archivo | Fase |
|---------|------|
| `.gitignore` | 1.5 |
| `.claude/settings.json` | 3.1 |
| `.claude/agents/quality-agent.md` | 4.1 |
| `.claude/commands/quality-check.md` | 5.1 |
| `.claude/commands/quality-report.md` | 5.2 |
