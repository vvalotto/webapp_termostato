# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Aplicacion web Flask para visualizacion de datos del termostato (webapp_termostato). Este es el componente frontend de una arquitectura cliente-servidor que consume la API REST del backend `app_termostato`. Parte de un caso de estudio academico/didactico demostrando arquitectura cliente-servidor.

**Stack tecnologico:**
- Python 3.12 con Flask
- Flask-Bootstrap para UI (Bootstrap 3)
- Flask-WTF para formularios
- Flask-Moment para manejo de fechas
- Requests para comunicacion con API
- Gunicorn para produccion
- Pytest para testing

## Commands

**Ejecutar la aplicacion (desarrollo):**
```bash
python app.py
```
La aplicacion corre en `http://localhost:5001`

**Instalar dependencias Python:**
```bash
pip install -r requirements.txt
```

**Instalar dependencias de desarrollo (incluye testing):**
```bash
pip install -r requirements-dev.txt
```

**Instalar dependencias de calidad web (opcional):**
```bash
npm install
```

**Ejecutar tests:**
```bash
pytest
pytest tests/test_app.py::TestRutaIndex::test_index_con_api_funcionando  # test especifico
pytest -k "test_index"  # por patron de nombre
```

**Ejecutar con Gunicorn (produccion):**
```bash
gunicorn app:app
```

## Architecture

**Rutas expuestas por el frontend:**
- `/` - Pagina principal (SSR con Flask + polling AJAX)
- `/api/estado` - Endpoint JSON para actualizacion AJAX sin recarga (cada 10s)
- `/api/historial?limite=N` - Historial de temperaturas (default: 60 registros)
- `/health` - Health check del sistema (verifica conexion con backend)

**API Backend:**
- El backend REST API corre en `http://localhost:5050` (configurable via `API_URL` o `URL_APP_API`)
- Endpoints consumidos:
  - `/termostato/` - Estado completo del termostato
  - `/termostato/historial/` - Historial de temperaturas
  - `/comprueba/` - Health check del backend

**Cache en memoria (webapp/__init__.py):**
`ultima_respuesta_valida` y `ultimo_timestamp` son variables globales de modulo que almacenan la ultima respuesta exitosa. Si el backend falla, se sirven datos cacheados con `from_cache=True`. Este cache se reinicia al reiniciar el servidor. Los tests deben usar la fixture `reset_cache` para limpiar el estado entre pruebas.

**TermostatoForm (forms.py):**
Se usa exclusivamente para renderizado en plantillas, no para validacion. Los campos se asignan como atributos de instancia dinamicamente en la vista (no como datos de formulario WTF).

**JavaScript modular (static/js/):**
Los modulos JS se cargan via `<script>` en `index.html` en orden de dependencias: `config.js` → modulos de feature (api.js, bateria.js, conexion.js, etc.) → `app.js` (coordinador). `app.js` asume que todos los demas modulos ya estan cargados. Las graficas estan en `static/js/graficas/` (temperatura.js, climatizador.js).

## Language

The codebase uses Spanish for variable names, comments, and UI labels. Maintain this convention.

## Jira Integration (MCP)

Este proyecto esta vinculado al proyecto Jira `webapp_termostato`. Usar las herramientas MCP de Atlassian para:

- **Buscar issues**: `mcp__atlassian__search` con query relacionado a "webapp_termostato"
- **Buscar con JQL**: `mcp__atlassian__searchJiraIssuesUsingJql` con `project = "WT"`
- **Obtener issue especifico**: `mcp__atlassian__getJiraIssue` con el issueIdOrKey (ej: WT-123)
- **Crear issues**: `mcp__atlassian__createJiraIssue` con projectKey="WT"

**Tipos de issue disponibles:**
- Tarea (id: 10037)
- Error (id: 10038)
- Historia (id: 10039)
- Epic (id: 10040)
- Subtarea (id: 10041)

Consultar Jira antes de implementar nuevas funcionalidades para verificar historias de usuario y requisitos.

## Quality Agent

El ambiente agentico de calidad de codigo esta integrado en este proyecto.

### Comandos Disponibles

| Comando                 | Descripcion                              |
|-------------------------|------------------------------------------|
| `/quality-check [path]` | Analisis rapido de calidad (Python + Web)|
| `/quality-report`       | Reporte completo en Markdown             |

### Herramientas de Analisis

**Python:**
- `radon cc` - Complejidad ciclomatica
- `radon mi` - Indice de mantenibilidad
- `pylint` - Linting y convenciones

**Web:**
- `htmlhint` - Linting de templates HTML
- `stylelint` - Linting de CSS
- `eslint` - Linting de JavaScript

### Configuracion

Los umbrales se configuran en `.claude/settings.json`:

```json
{
  "quality_gates": {
    "max_complexity": 10,
    "min_maintainability": 20,
    "min_pylint_score": 8.0,
    "max_function_lines": 50
  },
  "quality_gates_web": {
    "html": { "max_errors": 0, "max_warnings": 5 },
    "css": { "max_errors": 0, "max_warnings": 10 },
    "javascript": { "max_errors": 0, "max_warnings": 10 }
  }
}
```

### Hook Pre-Commit

Se ejecuta automaticamente validacion de calidad antes de cada `git commit` (configurado en `.claude/settings.json`).
