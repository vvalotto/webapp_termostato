# Webapp Termostato

Aplicación web Flask para visualización del estado de un termostato. Actúa como frontend consumiendo la API REST del backend `app_termostato`.

## Descripción

Este proyecto es parte de un caso de estudio académico/didáctico que demuestra la arquitectura cliente-servidor con separación de frontend y backend.

La aplicación muestra:
- Temperatura ambiente actual
- Temperatura deseada configurada
- Estado del climatizador (encendido/apagado)
- Nivel de carga de la batería

## Arquitectura

```
┌─────────────────────┐         ┌─────────────────────┐
│  webapp_termostato  │  HTTP   │   app_termostato    │
│     (Frontend)      │ ──────► │     (Backend)       │
│     Puerto 5001     │  REST   │     Puerto 5050     │
└─────────────────────┘         └─────────────────────┘
```

## Requisitos

- Python 3.8+
- Flask
- Flask-Bootstrap
- Flask-Moment
- Flask-WTF
- Requests

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd webapp_termostato
```

2. Crear entorno virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install flask flask-bootstrap flask-moment flask-wtf requests
```

## Configuración

La aplicación usa variables de entorno para configuración:

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `SECRET_KEY` | Clave secreta para sesiones Flask | `clave-desarrollo-local` |
| `URL_APP_API` | URL del backend API | `http://localhost:5050` |

Ejemplo de configuración:
```bash
export SECRET_KEY="mi-clave-secreta"
export URL_APP_API="http://localhost:5050"
```

## Ejecución

1. Asegurarse de que el backend (`app_termostato`) esté ejecutándose en el puerto 5050.

2. Ejecutar la aplicación:
```bash
python lanzador.py
```

3. Acceder en el navegador: http://localhost:5001

## Estructura del Proyecto

```
webapp_termostato/
├── lanzador.py          # Punto de entrada de la aplicación
├── forms.py             # Definición de formularios WTForms
├── templates/
│   ├── base.html        # Template base con navbar
│   ├── index.html       # Página principal
│   ├── 404.html         # Página de error 404
│   └── 500.html         # Página de error 500
├── static/
│   └── styles.css       # Estilos personalizados
├── PLAN_MEJORAS.md      # Plan de mejoras del proyecto
└── README.md            # Este archivo
```

## Endpoints Consumidos

La aplicación consume los siguientes endpoints del backend:

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/termostato/temperatura_ambiente/` | Obtiene temperatura ambiente |
| GET | `/termostato/temperatura_deseada/` | Obtiene temperatura deseada |
| GET | `/termostato/bateria/` | Obtiene nivel de batería |
| GET | `/termostato/estado_climatizador/` | Obtiene estado del climatizador |

## Características

- **Auto-refresh**: La página se actualiza automáticamente cada 10 segundos
- **Manejo de errores**: Muestra "Error API" si el backend no responde
- **Diseño responsive**: Interfaz Bootstrap adaptable a diferentes dispositivos

## Proyecto Relacionado

Este frontend requiere el backend API:
- **app_termostato**: API REST que gestiona los datos del termostato

## Licencia

Proyecto académico/didáctico para el curso ISSE.
