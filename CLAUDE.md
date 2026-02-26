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

**Patron BFF (Backend for Frontend) con arquitectura por capas** (desde US-001 v3.0.0):

```
webapp/
├── __init__.py           # Application Factory: create_app(config_name)
├── config.py             # Config / DevelopmentConfig / TestingConfig / ProductionConfig
├── forms.py              # TermostatoForm (solo renderizado, sin validacion WTF)
├── models/               # DTOs: TermostatoEstadoDTO (TypedDict)
├── cache/                # Interfaz Cache (ABC) + MemoryCache (threading.Lock)
├── services/             # ApiClient (ABC) + RequestsApiClient + TermostatoService
└── routes/               # Blueprints: main_bp (/) + api_bp (/api) + health_bp (/health)
```

**Application Factory:**
`create_app(config_name)` en `webapp/__init__.py` instancia `MemoryCache`, `RequestsApiClient` y `TermostatoService`, los ensambla y los adjunta a `app.termostato_service`. Usar `create_app('testing')` en fixtures de tests.

**Rutas expuestas:**
- `GET /` - Dashboard SSR (main_bp → TermostatoService.obtener_estado())
- `GET /api/estado` - JSON `{success, data, timestamp, from_cache}` (api_bp)
- `GET /api/historial?limite=N` - JSON con historial (api_bp, default: 60)
- `GET /health` - JSON `{status, frontend, backend}` (health_bp)

**Cache como fallback (MemoryCache):**
El servicio siempre intenta obtener datos frescos del backend. Solo usa el cache si la API lanza `ApiError`. El cache se limpia llamando `app.termostato_service._cache.clear()` en los tests. `MemoryCache.set(key, value, ttl=None)` acepta TTL en segundos; sin TTL el valor no expira.

**Excepciones custom (desde US-002):**
`ApiError` (base) → `ApiConnectionError`, `ApiTimeoutError`. Las rutas capturan `ApiError` para retornar 503. No usar `requests.exceptions.*` fuera de `api_client.py`.

**Inyeccion de dependencias:**
`TermostatoService(api_client=..., cache=...)` acepta cualquier implementacion de `ApiClient` y `Cache` (ABCs en `webapp/services/api_client.py` y `webapp/cache/cache_interface.py`). Los tests inyectan mocks directamente — no usar `@patch` en tests de rutas o servicios.

**MockApiClient (desde US-002):**
`MockApiClient(mock_data, raise_error=None)` — cliente de test con `call_count`, `last_path`, y `raise_error`. `create_app('testing')` inyecta `MockApiClient` automaticamente. Para escenarios de error: `app.termostato_service._api_client = MockApiClient({}, raise_error=ApiConnectionError)`.

**Tests:**
- `tests/test_app.py` — tests de rutas con `create_app('testing')` (sin `@patch`)
- `tests/test_cache.py`, `tests/test_api_client.py`, `tests/test_services.py` — tests unitarios de capas
- `tests/test_es6_modules.py` — tests de estructura JS y template ES6 (US-003)
- `tests/integration/` — tests HTTP end-to-end con Flask test client y MockApiClient
- `tests/step_defs/` — step definitions BDD (pytest-bdd 8.x): US-001, US-002 y US-003
- `tests/features/` — escenarios Gherkin
- `tests/.pylintrc` — suprime W0621/W0212 (falsos positivos de pytest fixtures)

**TermostatoForm (forms.py):**
Se usa exclusivamente para renderizado en plantillas, no para validacion. Los campos se asignan como atributos de instancia dinamicamente en la vista.

**JavaScript — Modulos ES6 nativos (desde US-003):**
Los 13 archivos JS usan `import`/`export` explícitos. El template `index.html` carga un unico entry point:
```html
<script nomodule>alert('Actualiza tu navegador...');</script>
<script type="module" src=".../js/app.js"></script>
```
Grafo de dependencias: `config.js` (hoja) → modulos intermedios → `app.js` (orchestrador).
jQuery, Bootstrap y Chart.js siguen siendo globales (dependencias externas).
Las graficas estan en `static/js/graficas/`.

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
