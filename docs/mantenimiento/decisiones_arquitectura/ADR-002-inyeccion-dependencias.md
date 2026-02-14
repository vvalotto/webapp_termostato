# ADR-002: Implementar Inyección de Dependencias

**Estado:** 📋 Propuesto
**Fecha:** 2026-02-14
**Decisores:** Tech Lead, Backend Team
**Relacionado con:** US-002, ADR-001
**Depende de:** ADR-001 (Arquitectura por Capas)

---

## Contexto y Problema

El código actual tiene **acoplamiento fuerte** con implementaciones concretas:

```python
# webapp/__init__.py
import requests  # ← Dependencia concreta hardcodeada

def obtener_estado_termostato():
    respuesta = requests.get(url, timeout=5)  # ← Imposible mockear sin monkey-patching
    return respuesta.json()

# Tests actuales (test_app.py)
@patch('webapp.requests.get')  # ← Monkey-patching frágil
def test_index_con_api_funcionando(self, mock_get, client):
    mock_response = Mock()
    mock_get.return_value = mock_response
```

**Problemas:**

1. **Violación de Dependency Inversion Principle (SOLID-D):**
   - Módulos de alto nivel dependen de módulos de bajo nivel
   - No hay abstracciones entre capas

2. **Difícil de testear:**
   - Requiere `@patch` en cada test
   - No se pueden inyectar mocks sin monkey-patching
   - Tests frágiles (dependen de paths internos)

3. **Difícil de cambiar implementación:**
   - Para usar `httpx` en lugar de `requests`: reescribir todo
   - Para agregar retry logic: modificar múltiples lugares
   - Para agregar métricas: tocar código de negocio

4. **Imposible configurar para diferentes entornos:**
   - Testing: mock client
   - Desarrollo: requests con timeout largo
   - Producción: requests con retry + circuit breaker

---

## Consideraciones

### Opción 1: Mantener acoplamiento directo (Status Quo)

```python
import requests

def obtener_estado():
    return requests.get(url, timeout=5).json()
```

**Pros:**
- ✅ Simple
- ✅ Menos código

**Contras:**
- ❌ Violación SOLID-D
- ❌ Tests frágiles (monkey-patching)
- ❌ Imposible cambiar implementación
- ❌ No configurable por entorno

**Puntuación:** 3/10

---

### Opción 2: Dependency Injection Container (Dependency Injector)

**Librería:** [dependency-injector](https://python-dependency-injector.ets-labs.org/)

```python
# containers.py
from dependency_injector import containers, providers
from .services import TermostatoService, RequestsApiClient
from .cache import MemoryCache

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Infraestructura
    cache = providers.Singleton(MemoryCache)
    api_client = providers.Factory(
        RequestsApiClient,
        base_url=config.api.url
    )

    # Servicios
    termostato_service = providers.Factory(
        TermostatoService,
        api_client=api_client,
        cache=cache
    )

# __init__.py
container = Container()
container.config.from_yaml('config.yml')

app.container = container
```

**Pros:**
- ✅ DI framework maduro
- ✅ Configuración declarativa
- ✅ Soporte para singletons, factories, scopes
- ✅ Wiring automático

**Contras:**
- ❌ Dependencia externa nueva
- ❌ Curva de aprendizaje
- ❌ Overkill para app pequeña
- ❌ Magic (auto-wiring oculta dependencias)

**Puntuación:** 7/10

---

### Opción 3: Manual Dependency Injection (Constructor Injection)

```python
# services/api_client.py
from abc import ABC, abstractmethod

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
        self._api_client = api_client  # ← Inyección por constructor
        self._cache = cache

    def obtener_estado(self) -> dict:
        try:
            datos = self._api_client.get('/termostato/')
            self._cache.set('estado', datos)
            return datos
        except Exception:
            return self._cache.get('estado')

# __init__.py (Factory Pattern)
def create_app(config_name='default'):
    app = Flask(__name__)

    # Crear dependencias
    cache = MemoryCache()
    api_client = RequestsApiClient(
        base_url=app.config['API_URL'],
        timeout=app.config['API_TIMEOUT']
    )

    # Inyectar en servicios
    termostato_service = TermostatoService(api_client, cache)
    app.termostato_service = termostato_service

    return app

# Tests (simple y explícito)
def test_obtener_estado():
    mock_client = MockApiClient({'temperatura': 22})
    cache = MemoryCache()
    service = TermostatoService(mock_client, cache)  # ← Inyección directa

    resultado = service.obtener_estado()
    assert resultado['temperatura'] == 22
```

**Pros:**
- ✅ Sin dependencias externas
- ✅ Explícito (fácil de entender)
- ✅ Control total
- ✅ Testeable trivialmente
- ✅ Cumple SOLID-D
- ✅ Flexible (cambiar implementación sin recompilar)

**Contras:**
- ⚠️ Más boilerplate (crear manualmente)
- ⚠️ Responsabilidad del desarrollador (no automático)

**Puntuación:** 9/10

---

## Decisión

**Elegimos Opción 3: Manual Dependency Injection (Constructor Injection)**

### Fundamento

Para un proyecto de este tamaño:
- Manual DI es suficiente (no necesitamos framework complejo)
- Explícito > Implícito (principle of least surprise)
- Sin dependencias externas = menos riesgo
- Más fácil de debuggear (no magic)

Si el proyecto crece significativamente (10+ servicios), podemos migrar a Dependency Injector.

---

## Implementación

### 1. Definir Abstracciones (Interfaces)

```python
# services/api_client.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class ApiClient(ABC):
    """Contrato para clientes HTTP"""

    @abstractmethod
    def get(self, path: str, timeout: int = None) -> Dict[str, Any]:
        """Realiza petición GET"""
        pass

# cache/cache_interface.py
from abc import ABC, abstractmethod
from typing import Any, Optional

class Cache(ABC):
    """Contrato para sistemas de caché"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = None):
        pass
```

### 2. Implementaciones Concretas

```python
# services/api_client.py
class RequestsApiClient(ApiClient):
    def __init__(self, base_url: str, timeout: int = 5):
        self.base_url = base_url
        self.default_timeout = timeout

    def get(self, path: str, timeout: int = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        timeout = timeout or self.default_timeout
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()

class MockApiClient(ApiClient):
    """Mock para testing"""
    def __init__(self, mock_data: Dict[str, Any]):
        self.mock_data = mock_data

    def get(self, path: str, timeout: int = None) -> Dict[str, Any]:
        return self.mock_data
```

### 3. Servicios con Constructor Injection

```python
# services/termostato_service.py
class TermostatoService:
    def __init__(self, api_client: ApiClient, cache: Cache):
        """
        Args:
            api_client: Cliente HTTP (abstracción)
            cache: Sistema de caché (abstracción)
        """
        self._api_client = api_client
        self._cache = cache

    def obtener_estado(self) -> Tuple[Optional[dict], bool]:
        """
        Returns:
            (datos, from_cache)
        """
        try:
            datos = self._api_client.get('/termostato/')
            self._cache.set('estado', datos, ttl=60)
            return datos, False
        except Exception as e:
            logger.warning(f"API error: {e}, using cache")
            cached = self._cache.get('estado')
            return cached, cached is not None
```

### 4. Application Factory con DI

```python
# __init__.py
def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Inicializar extensiones
    bootstrap.init_app(app)
    moment.init_app(app)

    # Infraestructura (implementaciones concretas)
    cache = create_cache(app.config)
    api_client = create_api_client(app.config)

    # Servicios (inyección)
    termostato_service = TermostatoService(api_client, cache)

    # Registrar en app
    app.termostato_service = termostato_service

    # Registrar blueprints
    from .routes import main, api
    app.register_blueprint(main.bp)
    app.register_blueprint(api.bp)

    return app

def create_cache(config) -> Cache:
    """Factory de cache según entorno"""
    if config.get('TESTING'):
        return MemoryCache()
    elif config.get('REDIS_URL'):
        return RedisCache(redis_url=config['REDIS_URL'])
    else:
        return MemoryCache()

def create_api_client(config) -> ApiClient:
    """Factory de API client según entorno"""
    if config.get('TESTING'):
        return MockApiClient({'temperatura_ambiente': 22})
    else:
        return RequestsApiClient(
            base_url=config['API_URL'],
            timeout=config.get('API_TIMEOUT', 5)
        )
```

### 5. Uso en Routes (sin cambios para el controlador)

```python
# routes/main.py
from flask import Blueprint, render_template, current_app

bp = Blueprint('main', __name__)

@bp.route("/")
def index():
    # Obtener servicio desde app
    service = current_app.termostato_service
    datos, from_cache = service.obtener_estado()

    return render_template("index.html", datos=datos)
```

### 6. Testing Simplificado

```python
# tests/test_termostato_service.py
def test_obtener_estado_exitoso():
    # Arrange
    mock_data = {'temperatura_ambiente': 22, 'carga_bateria': 3.8}
    mock_client = MockApiClient(mock_data)
    cache = MemoryCache()
    service = TermostatoService(mock_client, cache)

    # Act
    resultado, from_cache = service.obtener_estado()

    # Assert
    assert resultado['temperatura_ambiente'] == 22
    assert from_cache is False

def test_obtener_estado_usa_cache_cuando_api_falla():
    # Arrange
    failing_client = FailingApiClient()  # Siempre lanza excepción
    cache = MemoryCache()
    cache.set('estado', {'temperatura_ambiente': 20})
    service = TermostatoService(failing_client, cache)

    # Act
    resultado, from_cache = service.obtener_estado()

    # Assert
    assert resultado['temperatura_ambiente'] == 20
    assert from_cache is True
```

---

## Consecuencias

### Positivas

- ✅ **SOLID-D cumplido:** Dependencia de abstracciones
- ✅ **Testabilidad:** Tests simples sin `@patch`
- ✅ **Flexibilidad:** Cambiar implementación sin tocar código de negocio
- ✅ **Configurabilidad:** Diferentes implementaciones por entorno
- ✅ **Mantenibilidad:** Fácil agregar logging, métricas, retries

### Negativas

- ⚠️ **Boilerplate:** Más código de configuración (~100 líneas adicionales)
- ⚠️ **Indirección:** Una capa más de abstracción

### Riesgos

- ⚠️ **Over-engineering inicial:** Puede parecer complejo para equipo nuevo
  - **Mitigación:** Documentación exhaustiva + ejemplos

---

## Validación

### Criterios de Aceptación

- [ ] Todas las dependencias externas inyectadas (0 imports de `requests` en services)
- [ ] Tests sin `@patch` (excepto integraciones)
- [ ] Abstracciones (ABC) para: ApiClient, Cache
- [ ] Factory functions documentadas
- [ ] 100% cobertura mantenida

---

## Referencias

- [Dependency Inversion Principle - Martin](https://en.wikipedia.org/wiki/Dependency_inversion_principle)
- [Dependency Injection in Python](https://github.com/ets-labs/python-dependency-injector)
- [Flask Application Factories](https://flask.palletsprojects.com/en/2.3.x/patterns/appfactories/)

---

**Aprobadores:**
- [ ] Tech Lead
- [ ] Backend Developer

**Fecha de Revisión:** Pendiente
