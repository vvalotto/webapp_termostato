# Plan de Implementación: US-001 — Refactorizar Backend en Arquitectura por Capas

**Patrón:** BFF (Backend for Frontend) + Arquitectura por capas
**Producto:** webapp_termostato
**Estimación Total:** 24h (según US-001)
**Prioridad:** P0 — Crítico

---

## Contexto

Refactorizar `webapp/__init__.py` (199 líneas, 8 violaciones SOLID) en una
arquitectura limpia por capas. Sin cambios funcionales — los tests actuales deben
pasar sin modificar su lógica de negocio.

**Estrategia:** Bottom-up — capas inferiores primero, sin romper funcionalidad
en ningún momento.

---

## Componentes a Implementar

### 1. Configuración — `webapp/config.py` (30 min)

- [ ] `webapp/config.py`
  - Clase `Config` (base): `SECRET_KEY`, `URL_APP_API`
  - Clase `DevelopmentConfig(Config)`: `DEBUG = True`
  - Clase `TestingConfig(Config)`: `TESTING = True`, `WTF_CSRF_ENABLED = False`
  - Clase `ProductionConfig(Config)`: `DEBUG = False`
  - Dict `config` para lookup por nombre

### 2. Capa de Datos — `webapp/models/` (25 min)

- [ ] `webapp/models/__init__.py` — vacío
- [ ] `webapp/models/termostato_dto.py`
  - `TypedDict` `TermostatoEstadoDTO` con campos: `temperatura_ambiente`,
    `temperatura_deseada`, `carga_bateria`, `indicador`, `estado_climatizador`
  - Type hints completos
  - Docstrings

### 3. Capa de Infraestructura — `webapp/cache/` (60 min)

- [ ] `webapp/cache/__init__.py` — vacío
- [ ] `webapp/cache/cache_interface.py`
  - ABC `Cache` con métodos `get(key: str)` y `set(key: str, value: Any)`
  - Método `clear()` para tests

- [ ] `webapp/cache/memory_cache.py`
  - Clase `MemoryCache(Cache)` con `threading.Lock`
  - Migra las variables globales `ultima_respuesta_valida`, `ultimo_timestamp`
  - Almacena tupla `(datos, timestamp)` bajo clave `'estado'`

### 4. Capa de Servicios — `webapp/services/` (90 min)

- [ ] `webapp/services/__init__.py` — vacío
- [ ] `webapp/services/api_client.py`
  - ABC `ApiClient` con método `get(path: str, **kwargs) -> dict`
  - Clase `RequestsApiClient(ApiClient)`:
    - Constructor: `__init__(self, base_url: str)`
    - Implementa `get()` usando `requests.get()` con timeout 5s
    - Lanza `requests.exceptions.RequestException` sin atraparla

- [ ] `webapp/services/termostato_service.py`
  - Clase `TermostatoService`:
    - Constructor: `__init__(self, api_client: ApiClient, cache: Cache)`
    - `obtener_estado() -> tuple[dict|None, str|None, bool]`
      — migra la lógica de `obtener_estado_termostato()`
    - `obtener_historial(limite: int = 60) -> dict`
    - `health_check() -> dict`

### 5. Capa de Presentación — `webapp/routes/` (80 min)

- [ ] `webapp/routes/__init__.py` — vacío
- [ ] `webapp/routes/main.py`
  - Blueprint `main_bp = Blueprint('main', __name__)`
  - `GET /` → migra `index()`, usa `current_app.termostato_service`

- [ ] `webapp/routes/api.py`
  - Blueprint `api_bp = Blueprint('api', __name__, url_prefix='/api')`
  - `GET /api/estado` → migra `api_estado()`
  - `GET /api/historial` → migra `api_historial()`

- [ ] `webapp/routes/health.py`
  - Blueprint `health_bp = Blueprint('health', __name__)`
  - `GET /health` → migra `health()`

### 6. Application Factory — `webapp/__init__.py` (45 min)

- [ ] Refactorizar `webapp/__init__.py` completamente:
  - Función `create_app(config_name: str = 'default') -> Flask`
  - Inicializa extensiones: `Bootstrap`, `Moment`
  - Crea dependencias: `MemoryCache()`, `RequestsApiClient(url)`
  - Instancia `TermostatoService(api_client, cache)` y lo adjunta a `app`
    como `app.termostato_service`
  - Registra blueprints: `main_bp`, `api_bp`, `health_bp`
  - Mantiene `VERSION = '2.0.0'`

- [ ] Actualizar `app.py`:
  - Cambiar `from webapp import app` → `from webapp import create_app`
  - `app = create_app('development')`

---

## Integración y Compatibilidad

### Tests existentes (no modificar lógica)

- [ ] Actualizar `tests/test_app.py`:
  - Fixture `client`: usar `create_app('testing')` en lugar de importar `app` directamente
  - Fixture `reset_cache`: usar `app.termostato_service._cache.clear()`
  - Cambiar `@patch('webapp.requests.get')` → `@patch('webapp.services.api_client.requests.get')`
  - Sin cambios en los asserts — misma lógica de negocio

### Nuevos archivos de test

- [ ] `tests/test_cache.py` — tests unitarios de `MemoryCache`
  - `test_memory_cache_set_get()`
  - `test_memory_cache_miss_retorna_none()`
  - `test_memory_cache_clear()`

- [ ] `tests/test_api_client.py` — tests unitarios de `RequestsApiClient`
  - `test_get_exitoso()`
  - `test_get_timeout()`
  - `test_get_connection_error()`

- [ ] `tests/test_services.py` — tests unitarios de `TermostatoService`
  - Usa mocks inyectados (sin `@patch`)
  - `test_obtener_estado_exitoso()`
  - `test_obtener_estado_usa_cache_cuando_falla_api()`
  - `test_obtener_estado_retorna_none_sin_cache()`
  - `test_obtener_historial()`
  - `test_health_check_ok()`
  - `test_health_check_backend_caido()`

---

## Validación

- [ ] Ejecutar suite completa: `pytest` (todos los tests deben pasar)
- [ ] Cobertura: `pytest --cov=webapp --cov-report=term-missing`
- [ ] Quality check: `/quality-check webapp/`
- [ ] Pylint: `pylint webapp/`
- [ ] Prueba manual: `python app.py`
- [ ] Validación BDD: escenarios en `tests/features/US-001-*.feature`

---

## Orden de Implementación (Bottom-Up)

```
1. config.py          ← sin dependencias
2. models/            ← sin dependencias
3. cache/             ← sin dependencias
4. services/          ← depende de cache/
5. routes/            ← depende de services/
6. __init__.py        ← ensambla todo
7. app.py             ← actualiza punto de entrada
8. tests/             ← adaptar y crear nuevos
```

---

**Estado:** 34/34 tareas completadas ✅
**Fecha Creación:** 2026-02-24
**Referencia:** US-001, ADR-001
