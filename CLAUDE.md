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
```

**Ejecutar con Gunicorn (produccion):**
```bash
gunicorn app:app
```

## Architecture

```
webapp_termostato/
├── app.py               # Punto de entrada (importa de webapp)
├── webapp/              # Aplicacion Flask
│   ├── __init__.py      # App Flask + rutas
│   ├── forms.py         # Definicion de formularios (TermostatoForm)
│   ├── templates/       # Templates Jinja2
│   │   ├── base.html    # Template base con navbar y layout
│   │   ├── index.html   # Pagina principal del termostato
│   │   ├── 404.html     # Pagina de error 404
│   │   └── 500.html     # Pagina de error 500
│   └── static/          # Archivos estaticos
│       ├── css/         # Estilos CSS modulares
│       ├── js/          # JavaScript modular
│       └── proyecto.ico # Favicon
├── tests/               # Tests unitarios
│   ├── __init__.py
│   └── test_app.py      # Tests de rutas y API
├── docs/                # Documentacion
├── quality/             # Sistema de calidad de codigo
│   ├── scripts/         # Scripts de analisis
│   └── reports/         # Reportes generados
└── .claude/             # Configuracion de Claude Code
    ├── settings.json    # Quality gates y hooks
    ├── agents/          # Agentes especializados
    └── commands/        # Comandos personalizados
```

**API Backend:**
- El backend REST API corre en `http://localhost:5050` (configurable via `API_URL` o `URL_APP_API`)
- Endpoints consumidos:
  - `/termostato/` - Estado completo del termostato
  - `/termostato/historial/` - Historial de temperaturas
  - `/comprueba/` - Health check del backend

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
