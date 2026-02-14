# US-002: Implementar Inyección de Dependencias

**Epic:** Mejora de Arquitectura Backend
**Prioridad:** P0 - Crítico
**Story Points:** 8
**Sprint:** 1-2
**Estado:** 📋 Planificado

---

## Historia de Usuario

**Como** desarrollador del equipo
**Quiero** implementar inyección de dependencias en el backend
**Para** reducir el acoplamiento, facilitar el testing con mocks y cumplir el Principio de Inversión de Dependencias (SOLID-D)

---

## Contexto Técnico

### Problema Actual

Dependencias hardcodeadas en el código:

```python
# webapp/__init__.py
import requests  # ← Acoplamiento fuerte

def obtener_estado_termostato():
    respuesta = requests.get(url, timeout=5)  # ← Imposible inyectar mock
    return respuesta.json()

# tests/test_app.py - Testing frágil
@patch('webapp.requests.get')  # ← Monkey-patching
def test_index_con_api_funcionando(self, mock_get, client):
    mock_response = Mock()
    mock_get.return_value = mock_response  # ← Frágil
```

**Problemas:**
- ❌ Violación de Dependency Inversion Principle (SOLID-D)
- ❌ Tests frágiles (dependen de `@patch` con paths mágicos)
- ❌ Imposible cambiar implementación HTTP sin reescribir código
- ❌ No configurable por entorno (testing, desarrollo, producción)

### Solución Propuesta

**Inyección de dependencias manual** con abstracciones:

```python
# services/api_client.py
class ApiClient(ABC):
    """Abstracción de cliente HTTP"""
    @abstractmethod
    def get(self, path: str) -> dict:
        pass

class RequestsApiClient(ApiClient):
    def __init__(self, base_url: str, timeout: int = 5):
        self.base_url = base_url
        self.timeout = timeout

    def get(self, path: str) -> dict:
        response = requests.get(f"{self.base_url}{path}", timeout=self.timeout)
        response.raise_for_status()
        return response.json()

# services/termostato_service.py
class TermostatoService:
    def __init__(self, api_client: ApiClient, cache: Cache):
        self._api_client = api_client  # ← Inyección
        self._cache = cache

# __init__.py - Application Factory
def create_app(config_name='default'):
    # Crear dependencias
    api_client = RequestsApiClient(base_url=app.config['API_URL'])
    cache = MemoryCache()

    # Inyectar en servicio
    termostato_service = TermostatoService(api_client, cache)
    app.termostato_service = termostato_service

# Tests - Simple y explícito
def test_obtener_estado():
    mock_client = MockApiClient({'temperatura': 22})
    service = TermostatoService(mock_client, MemoryCache())
    resultado = service.obtener_estado()
    assert resultado['temperatura'] == 22  # ← Sin @patch
```

---

## Criterios de Aceptación

### ✅ Funcionales

1. **[CRÍTICO]** Todas las funcionalidades actuales siguen funcionando:
   - [ ] API calls usan abstracción `ApiClient`
   - [ ] Cache usa abstracción `Cache`
   - [ ] Configuración inyectada (no hardcodeada)
   - [ ] Sin regresiones funcionales

### ✅ Arquitectura

2. **[CRÍTICO]** Abstracciones definidas:
   - [ ] `ApiClient` (ABC) con implementaciones:
     - `RequestsApiClient` (producción)
     - `MockApiClient` (testing)
   - [ ] `Cache` (ABC) con implementaciones:
     - `MemoryCache` (single-worker)
     - `RedisCache` (multi-worker, futuro)

3. **[ALTO]** Inyección por constructor:
   - [ ] Todos los servicios reciben dependencias en `__init__`
   - [ ] No hay `import requests` en capa de servicios
   - [ ] No hay variables globales para cache
   - [ ] Factory functions para crear dependencias

4. **[ALTO]** Application Factory Pattern:
   - [ ] Función `create_app(config_name='default')`
   - [ ] Configuración por entorno:
     - Testing: MockApiClient + MemoryCache
     - Development: RequestsApiClient + MemoryCache
     - Production: RequestsApiClient + RedisCache (futuro)

### ✅ Testing

5. **[CRÍTICO]** Tests sin monkey-patching:
   - [ ] 0 usos de `@patch('webapp.requests.get')`
   - [ ] Mocks inyectados directamente en constructor
   - [ ] Tests independientes (no comparten estado)
   - [ ] Coverage ≥ 100% mantenido

### ✅ Calidad

6. **[ALTO]** Calidad de código:
   - [ ] Type hints en todas las abstracciones
   - [ ] Docstrings en ABCs explicando contrato
   - [ ] mypy sin errores (strict mode)
   - [ ] Pylint score ≥ 9.5/10

---

## Tareas Técnicas

### 1. Preparación (1 hora)

- [ ] Crear rama: `feature/US-002-inyeccion-dependencias`
- [ ] Verificar que US-001 (Arquitectura Capas) esté completo
- [ ] Crear estructura de archivos:
  ```
  webapp/
  ├── services/
  │   ├── api_client.py      # ← Crear
  │   └── termostato_service.py  # ← Ya existe de US-001
  └── cache/
      ├── cache_interface.py  # ← Crear
      └── memory_cache.py     # ← Ya existe de US-001
  ```

### 2. Definir Abstracción ApiClient (2 horas)

**Archivo:** `webapp/services/api_client.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ApiClient(ABC):
    """
    Abstracción de cliente HTTP para comunicación con API backend.

    Permite inyectar diferentes implementaciones según el entorno:
    - RequestsApiClient: Producción (usa librería requests)
    - MockApiClient: Testing (retorna datos predefinidos)
    - HttpxApiClient: Futuro (async con httpx)
    """

    @abstractmethod
    def get(self, path: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Realiza petición GET al path especificado.

        Args:
            path: Path relativo (ej: '/termostato/')
            timeout: Timeout en segundos (None usa default)

        Returns:
            Datos JSON parseados como dict

        Raises:
            ApiConnectionError: Error de conexión
            ApiTimeoutError: Timeout excedido
            ApiError: Otros errores HTTP
        """
        pass
```

**Implementación RequestsApiClient:**

```python
import requests
from typing import Dict, Any, Optional

class RequestsApiClient(ApiClient):
    """Implementación de ApiClient usando librería requests"""

    def __init__(self, base_url: str, default_timeout: int = 5):
        """
        Args:
            base_url: URL base de la API (ej: 'http://localhost:5050')
            default_timeout: Timeout por defecto en segundos
        """
        self.base_url = base_url.rstrip('/')
        self.default_timeout = default_timeout

    def get(self, path: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        timeout = timeout or self.default_timeout

        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise ApiTimeoutError(f"Timeout accessing {url}")
        except requests.exceptions.ConnectionError as e:
            raise ApiConnectionError(f"Connection error: {e}")
        except requests.exceptions.RequestException as e:
            raise ApiError(f"API error: {e}")
```

**Implementación MockApiClient:**

```python
class MockApiClient(ApiClient):
    """Mock de ApiClient para testing"""

    def __init__(self, mock_data: Dict[str, Any]):
        """
        Args:
            mock_data: Datos a retornar en todas las llamadas
        """
        self.mock_data = mock_data
        self.call_count = 0
        self.last_path = None

    def get(self, path: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        self.call_count += 1
        self.last_path = path
        return self.mock_data
```

**Tests:**

- [ ] `test_requests_client_get_success()`
- [ ] `test_requests_client_timeout()`
- [ ] `test_requests_client_connection_error()`
- [ ] `test_mock_client_returns_data()`
- [ ] `test_mock_client_tracks_calls()`

### 3. Definir Abstracción Cache (1.5 horas)

**Archivo:** `webapp/cache/cache_interface.py`

```python
from abc import ABC, abstractmethod
from typing import Any, Optional

class Cache(ABC):
    """
    Abstracción de sistema de caché.

    Permite diferentes backends:
    - MemoryCache: En memoria (single-worker)
    - RedisCache: Redis (multi-worker, futuro)
    """

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Obtiene valor de caché o None si no existe"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Guarda valor en caché.

        Args:
            key: Clave única
            value: Valor a guardar (debe ser serializable)
            ttl: Time-to-live en segundos (None = sin expiración)
        """
        pass

    @abstractmethod
    def delete(self, key: str):
        """Elimina valor de caché"""
        pass

    @abstractmethod
    def clear(self):
        """Limpia todo el caché"""
        pass
```

**Implementación MemoryCache:**

```python
from threading import Lock
from datetime import datetime, timedelta
from typing import Any, Optional, Dict

class MemoryCache(Cache):
    """Caché en memoria thread-safe"""

    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                return None

            # Verificar expiración
            if entry['expires'] and entry['expires'] < datetime.now():
                del self._data[key]
                return None

            return entry['value']

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        with self._lock:
            expires = datetime.now() + timedelta(seconds=ttl) if ttl else None
            self._data[key] = {'value': value, 'expires': expires}

    def delete(self, key: str):
        with self._lock:
            self._data.pop(key, None)

    def clear(self):
        with self._lock:
            self._data.clear()
```

**Tests:**

- [ ] `test_memory_cache_set_get()`
- [ ] `test_memory_cache_get_missing_returns_none()`
- [ ] `test_memory_cache_ttl_expiration()`
- [ ] `test_memory_cache_delete()`
- [ ] `test_memory_cache_clear()`
- [ ] `test_memory_cache_thread_safety()`

### 4. Inyectar en TermostatoService (2 horas)

**Archivo:** `webapp/services/termostato_service.py`

**Antes (US-001):**
```python
class TermostatoService:
    def __init__(self):
        self._api_url = URL_APP_API  # ← Global
        # Usar requests directamente
```

**Después:**
```python
from typing import Tuple, Optional, Dict, Any
from .api_client import ApiClient
from ..cache import Cache

class TermostatoService:
    """Servicio de lógica de negocio para termostato"""

    def __init__(self, api_client: ApiClient, cache: Cache):
        """
        Args:
            api_client: Cliente HTTP (abstracción)
            cache: Sistema de caché (abstracción)
        """
        self._api_client = api_client
        self._cache = cache

    def obtener_estado(self) -> Tuple[Optional[Dict[str, Any]], Optional[str], bool]:
        """
        Obtiene estado del termostato desde API o caché.

        Returns:
            (datos, timestamp, from_cache)
        """
        try:
            datos = self._api_client.get('/termostato/', timeout=5)
            timestamp = datetime.utcnow().isoformat()

            # Cachear respuesta válida
            self._cache.set('estado', (datos, timestamp), ttl=60)

            return datos, timestamp, False

        except (ApiError, ApiTimeoutError, ApiConnectionError) as e:
            logger.warning(f"API error: {e}, using cache")
            cached = self._cache.get('estado')

            if cached:
                return cached[0], cached[1], True

            return None, None, False

    def obtener_historial(self, limite: int = 60) -> Dict[str, Any]:
        """Obtiene historial desde API"""
        try:
            return self._api_client.get(f'/termostato/historial/?limite={limite}', timeout=10)
        except ApiError as e:
            logger.error(f"Error obtaining historial: {e}")
            return {'success': False, 'historial': [], 'error': str(e)}

    def health_check(self) -> Dict[str, Any]:
        """Verifica salud del backend"""
        try:
            return self._api_client.get('/comprueba/', timeout=2)
        except ApiError as e:
            return {'status': 'unavailable', 'error': str(e)}
```

**Tests (sin @patch):**

```python
def test_obtener_estado_exitoso():
    # Arrange
    mock_data = {'temperatura_ambiente': 22, 'carga_bateria': 3.8}
    mock_client = MockApiClient(mock_data)
    cache = MemoryCache()
    service = TermostatoService(mock_client, cache)

    # Act
    datos, timestamp, from_cache = service.obtener_estado()

    # Assert
    assert datos['temperatura_ambiente'] == 22
    assert from_cache is False
    assert mock_client.call_count == 1

def test_obtener_estado_usa_cache_cuando_falla():
    # Arrange
    failing_client = FailingApiClient()  # Siempre lanza ApiError
    cache = MemoryCache()
    cache.set('estado', ({'temperatura_ambiente': 20}, '2026-02-14T10:00:00'))
    service = TermostatoService(failing_client, cache)

    # Act
    datos, timestamp, from_cache = service.obtener_estado()

    # Assert
    assert datos['temperatura_ambiente'] == 20
    assert from_cache is True
```

### 5. Application Factory con DI (2 horas)

**Archivo:** `webapp/__init__.py`

```python
from flask import Flask
from .services.api_client import RequestsApiClient, MockApiClient
from .services.termostato_service import TermostatoService
from .cache import MemoryCache
from .config import config

def create_app(config_name='default'):
    """
    Factory de aplicación Flask con inyección de dependencias.

    Args:
        config_name: Nombre de configuración ('default', 'testing', 'production')

    Returns:
        Aplicación Flask configurada
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Inicializar extensiones
    from flask_bootstrap import Bootstrap
    from flask_moment import Moment
    Bootstrap(app)
    Moment(app)

    # Crear dependencias según entorno
    api_client = _create_api_client(app.config)
    cache = _create_cache(app.config)

    # Inyectar en servicios
    termostato_service = TermostatoService(api_client, cache)
    app.termostato_service = termostato_service

    # Registrar blueprints
    from .routes import main, api
    app.register_blueprint(main.bp)
    app.register_blueprint(api.bp)

    return app

def _create_api_client(config):
    """Factory de ApiClient según entorno"""
    if config.get('TESTING'):
        # En tests, usar mock con datos válidos
        return MockApiClient({
            'temperatura_ambiente': 22,
            'temperatura_deseada': 24,
            'estado_climatizador': 'encendido',
            'carga_bateria': 3.8,
            'indicador': 'NORMAL'
        })
    else:
        return RequestsApiClient(
            base_url=config['API_URL'],
            default_timeout=config.get('API_TIMEOUT', 5)
        )

def _create_cache(config):
    """Factory de Cache según entorno"""
    # Por ahora siempre MemoryCache
    # Futuro: if config.get('REDIS_URL'): return RedisCache(...)
    return MemoryCache()

# Para desarrollo directo (python app.py)
app = create_app()
```

### 6. Actualizar Tests (3 horas)

**Antes:**
```python
@patch('webapp.requests.get')
def test_index_con_api_funcionando(self, mock_get, client):
    mock_response = Mock()
    mock_response.json.return_value = DATOS_API_VALIDOS
    mock_get.return_value = mock_response
    # ...
```

**Después:**
```python
def test_index_con_api_funcionando(client):
    # El mock ya está inyectado vía create_app('testing')
    response = client.get('/')

    assert response.status_code == 200
    assert b'22' in response.data  # temperatura mock
```

**Fixture actualizado:**

```python
@pytest.fixture
def client():
    """Cliente de pruebas con DI"""
    app = create_app('testing')  # ← Inyecta MockApiClient automáticamente
    with app.test_client() as test_client:
        yield test_client

@pytest.fixture
def app_with_custom_mock():
    """Para tests que necesitan mock específico"""
    def _create(mock_data):
        app = Flask(__name__)
        app.config['TESTING'] = True

        mock_client = MockApiClient(mock_data)
        cache = MemoryCache()
        service = TermostatoService(mock_client, cache)
        app.termostato_service = service

        # ... registrar blueprints

        return app

    return _create
```

### 7. Documentación (2 horas)

- [ ] Actualizar `README.md`:
  - Sección "Arquitectura - Inyección de Dependencias"
  - Diagrama de dependencias

- [ ] Crear `docs/inyeccion-dependencias.md`:
  - Explicación de abstracciones
  - Cómo agregar nueva implementación
  - Ejemplos de testing

- [ ] Docstrings completos en ABCs

---

## Estimación

| Tarea | Horas |
|-------|-------|
| Preparación | 1 |
| ApiClient abstraction + impls | 2 |
| Cache abstraction + impls | 1.5 |
| Inyectar en Service | 2 |
| Application Factory | 2 |
| Actualizar tests | 3 |
| Documentación | 2 |
| **TOTAL** | **13.5 horas** |

**Story Points:** 8 (Fibonacci: 8 ≈ 1.5-2 días)

---

## Definición de Hecho (DoD)

- [x] 0 imports de `requests` en `services/`
- [x] 0 usos de `@patch` en tests (excepto externos)
- [x] ABCs definidas para ApiClient y Cache
- [x] Implementaciones: RequestsApiClient, MockApiClient, MemoryCache
- [x] Application Factory con `create_app()`
- [x] Tests 100% cobertura
- [x] mypy sin errores
- [x] Pylint ≥ 9.5/10
- [x] Documentación completa

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Tests difíciles de adaptar | Media | Alto | Empezar con tests, luego código |
| Over-abstraction | Baja | Medio | Mantener ABCs simples (solo lo necesario) |
| Configuración compleja | Baja | Medio | Defaults sensatos, documentación clara |

---

**Dependencias:**
- Depende de: US-001 (Arquitectura Capas)
- Bloquea a: Todas las US de backend

---

**Asignado a:** -
**Estado Actual:** 📋 Planificado
