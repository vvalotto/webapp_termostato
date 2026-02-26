# Webapp Termostato

**Version 3.0.0**

Aplicacion web Flask para visualizacion del estado de un termostato IoT. Actua como frontend consumiendo la API REST del backend `app_termostato`.

## Descripcion

Este proyecto es parte de un caso de estudio academico/didactico que demuestra la arquitectura cliente-servidor con separacion de frontend y backend.

La aplicacion muestra en un **dashboard moderno tipo IoT**:
- Temperatura ambiente actual con indicador de tendencia
- Temperatura deseada configurada
- Diferencia entre temperatura actual y objetivo
- Estado del climatizador (apagado/encendido/enfriando/calentando)
- Voltaje de la bateria con alertas visuales
- Nivel de carga de bateria (NORMAL/BAJO/CRITICO)
- Grafica de evolucion de temperatura con zona de confort
- Grafica de historial del climatizador
- Estado de conexion en tiempo real

## Demo en Produccion

La aplicacion esta desplegada en Google Cloud Run:

| Componente | URL |
|------------|-----|
| **Frontend** | https://webapp-termostato-1090421346746.us-central1.run.app |
| **Backend** | https://app-termostato-1090421346746.us-central1.run.app |

Despliegue continuo desde GitHub: cada push a `master` actualiza automaticamente.

## Arquitectura

```
+---------------------+         +---------------------+
|  webapp_termostato  |  HTTP   |   app_termostato    |
|     (Frontend)      | ------> |     (Backend)       |
|     Puerto 5001     |  REST   |     Puerto 5050     |
+---------------------+         +---------------------+
```

**Patron BFF (Backend for Frontend) con arquitectura por capas** (v3.0.0):

```
webapp/
├── __init__.py     # Application Factory: create_app(config_name)
├── config.py       # Config / DevelopmentConfig / TestingConfig / ProductionConfig
├── forms.py        # TermostatoForm (solo renderizado)
├── models/         # DTOs: TermostatoEstadoDTO
├── cache/          # ABC Cache + MemoryCache thread-safe con TTL
├── services/       # ABC ApiClient + RequestsApiClient + MockApiClient + TermostatoService
└── routes/         # Blueprints: main_bp (/) + api_bp (/api) + health_bp (/health)
```

### Arquitectura en Produccion (GCP)

```
GitHub (push) --> Cloud Build --> Cloud Run (Frontend)
                                        |
                                        v
                                  Cloud Run (Backend)
```

## Estructura del Proyecto

```
webapp_termostato/
├── app.py                  # Punto de entrada
├── webapp/                 # Aplicacion Flask (arquitectura por capas)
│   ├── __init__.py         # Application Factory
│   ├── config.py           # Configuracion por entorno
│   ├── forms.py            # TermostatoForm (renderizado)
│   ├── cache/              # Cache ABC + MemoryCache
│   ├── models/             # DTOs
│   ├── routes/             # Blueprints Flask
│   ├── services/           # ApiClient + TermostatoService
│   ├── templates/          # Templates Jinja2
│   └── static/             # CSS + JS (modulos ES6 nativos)
├── tests/                  # Tests unitarios, BDD e integracion (181 tests)
├── docs/                   # Documentacion y ADRs
├── requirements.txt        # Dependencias produccion
├── requirements-dev.txt    # Dependencias desarrollo
└── pytest.ini              # Configuracion pytest (coverage automatico)
```

## Requisitos

- Python 3.12+
- Flask 3.x
- Node.js (opcional, para linting web)

## Instalacion

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
pip install -r requirements.txt
```

4. Para desarrollo (incluye testing):
```bash
pip install -r requirements-dev.txt
```

## Configuracion

| Variable | Descripcion | Valor por defecto |
|----------|-------------|-------------------|
| `SECRET_KEY` | Clave secreta para sesiones Flask | `clave-desarrollo-local` |
| `API_URL` | URL del backend API | `http://localhost:5050` |

```bash
export SECRET_KEY="mi-clave-secreta"
export API_URL="http://localhost:5050"
```

## Ejecucion

1. Asegurarse de que el backend (`app_termostato`) este ejecutandose.

2. Ejecutar la aplicacion:
```bash
python app.py
```

3. Acceder en el navegador: http://localhost:5001

### Produccion

```bash
gunicorn app:app
```

## Tests

```bash
# Ejecutar todos los tests
pytest

# Con cobertura detallada
pytest --cov=webapp --cov-report=html
```

**Suite: 181 tests — 95% cobertura**

## API Endpoints

### Frontend (webapp_termostato)

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | `/` | Dashboard principal |
| GET | `/api/estado` | Estado del termostato (JSON) |
| GET | `/api/historial` | Historial de temperaturas |
| GET | `/health` | Health check del servicio |

### Health Check

```json
GET /health

// Respuesta OK (200)
{
  "status": "ok",
  "timestamp": "2025-12-26T19:48:29",
  "frontend": {"version": "3.0.0", "status": "ok"},
  "backend": {"status": "ok", "version": "1.1.0", "uptime_seconds": 3600}
}

// Respuesta degradada (503)
{
  "status": "degraded",
  "frontend": {"version": "3.0.0", "status": "ok"},
  "backend": {"status": "unavailable", "error": "..."}
}
```

### Backend consumido

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | `/termostato/` | Estado completo del termostato |
| GET | `/termostato/historial/` | Historial de temperaturas |
| GET | `/comprueba/` | Health check del backend |

## Caracteristicas

### Dashboard v2.0

- **Estado de conexion visible**: Indicador online/offline con timestamp
- **Indicadores de tendencia**: Flechas de temperatura subiendo/bajando
- **Diferencia de temperatura**: Barra visual hacia el objetivo
- **Alertas de bateria**: Colores y animaciones segun nivel
- **Alerta de desconexion**: Banner cuando se pierde conexion
- **Zona de confort en grafica**: Banda sombreada alrededor de temperatura deseada
- **Ventana de tiempo configurable**: 5min, 1h, 6h, 24h con historial del servidor
- **Panel de ayuda**: Explicacion de estados del climatizador y bateria
- **Dashboard responsive**: Optimizado para moviles (min 44px tactil)

### Tecnologias

- Flask 3.x con Blueprints
- Bootstrap 3 + CSS modular
- Chart.js 4.4 para graficas
- JavaScript modular (ES6)
- Pytest para testing
- Pylint + ESLint + Stylelint para calidad

## Calidad de Codigo

El proyecto incluye herramientas de analisis de calidad:

```bash
# Analisis Python
python quality/scripts/calculate_metrics.py webapp/

# Analisis Web (requiere npm install)
python quality/scripts/calculate_web_metrics.py .
```

**Metricas actuales:**
- Pylint: 10.00/10
- Cobertura: 95%
- Complejidad ciclomatica: 1.66 promedio

## Proyecto Relacionado

Este frontend requiere el backend API:
- **app_termostato**: API REST que gestiona los datos del termostato (v1.1.0)

## Licencia

Proyecto academico/didactico para el curso ISSE.
