# US-001: Refactorizar Backend en Arquitectura por Capas

**Epic:** Mejora de Arquitectura Backend
**Prioridad:** P0 - Crítico
**Story Points:** 13
**Sprint:** 1
**Estado:** 📋 Planificado

---

## Historia de Usuario

**Como** desarrollador del equipo
**Quiero** refactorizar el backend en arquitectura por capas
**Para** mejorar la cohesión, reducir el acoplamiento y facilitar el testing y mantenimiento del código

---

## Contexto Técnico

### Problema Actual

El archivo `webapp/__init__.py` contiene **199 líneas** con múltiples responsabilidades mezcladas:

- ✗ Configuración de aplicación
- ✗ Variables globales de caché
- ✗ Cliente HTTP (requests)
- ✗ Lógica de negocio
- ✗ 4 endpoints/controladores
- ✗ Transformación de datos
- ✗ Manejo de errores

**Métricas actuales:**
- Cohesión: 6/10
- Acoplamiento: 5/10
- Complejidad ciclomática: 2.0
- Violaciones SOLID: 8

### Solución Propuesta

Separar en **arquitectura por capas** (Clean Architecture simplificada):

```
webapp/
├── __init__.py              # Factory (create_app) - 30 líneas
├── config.py                # Configuración - 40 líneas
├── models/                  # Capa de Datos
│   └── termostato_dto.py    # DTOs - 25 líneas
├── services/                # Capa de Negocio
│   ├── api_client.py        # Cliente HTTP - 50 líneas
│   └── termostato_service.py # Lógica dominio - 60 líneas
├── routes/                  # Capa de Presentación
│   ├── main.py              # Rutas UI - 40 líneas
│   └── api.py               # Rutas API - 80 líneas
└── cache/                   # Infraestructura
    ├── cache_interface.py   # Abstracción - 20 líneas
    └── memory_cache.py      # Implementación - 40 líneas
```

**Métricas objetivo:**
- Cohesión: 9/10
- Acoplamiento: 8/10
- Complejidad ciclomática: < 1.5
- Violaciones SOLID: 1

---

## Criterios de Aceptación

### ✅ Funcionales

1. **[CRÍTICO]** Todas las funcionalidades actuales siguen funcionando:
   - [ ] GET / renderiza dashboard correctamente
   - [ ] GET /api/estado retorna JSON del termostato
   - [ ] GET /api/historial retorna historial con parámetro `limite`
   - [ ] GET /health retorna estado del sistema
   - [ ] Cache funciona cuando API falla
   - [ ] Valores inválidos se muestran como "Error API"

2. **[CRÍTICO]** Tests existentes pasan sin modificaciones de lógica:
   - [ ] `test_index_con_api_funcionando`
   - [ ] `test_index_con_api_caida`
   - [ ] `test_index_usa_cache_cuando_api_cae`
   - [ ] Todos los tests de `TestApiEstado`
   - [ ] Todos los tests de `TestApiHistorial`
   - [ ] Todos los tests de `TestHealth`

### ✅ No Funcionales

3. **[CRÍTICO]** Calidad de código:
   - [ ] Pylint score ≥ 9.5/10
   - [ ] Complejidad ciclomática < 5 por función
   - [ ] Cobertura de tests = 100%
   - [ ] mypy sin errores (strict mode)
   - [ ] 0 variables globales mutables

4. **[ALTO]** Principios de diseño:
   - [ ] Cada módulo tiene una única responsabilidad (SRP)
   - [ ] Ningún módulo depende de implementaciones concretas (DIP)
   - [ ] Agregar nuevo endpoint no requiere modificar existentes (OCP)
   - [ ] Cohesión funcional en cada módulo
   - [ ] Acoplamiento solo por interfaces explícitas

5. **[MEDIO]** Documentación:
   - [ ] Docstrings en todos los módulos públicos
   - [ ] Type hints en todas las funciones
   - [ ] README actualizado con nueva estructura
   - [ ] Diagrama de arquitectura en docs/

### ✅ Testing

6. **[ALTO]** Tests adaptados:
   - [ ] Tests unitarios por capa (services, cache, routes)
   - [ ] Tests usan inyección de mocks (no `@patch`)
   - [ ] Fixture `reset_cache` actualizado
   - [ ] Tests de integración end-to-end (E2E) creados

---

## Tareas Técnicas

### 1. Preparación (2 horas)

- [ ] Crear estructura de carpetas:
  ```bash
  mkdir -p webapp/{models,services,routes,cache}
  touch webapp/models/__init__.py
  touch webapp/services/__init__.py
  touch webapp/routes/__init__.py
  touch webapp/cache/__init__.py
  ```

- [ ] Crear rama: `feature/US-001-arquitectura-capas`
- [ ] Backup de `webapp/__init__.py` original

### 2. Capa de Datos - Models (1 hora)

- [ ] Crear `models/termostato_dto.py`:
  - [ ] Clase `TermostatoEstadoDTO` (puede ser simple dict por ahora)
  - [ ] Type hints completos
  - [ ] Docstrings

### 3. Capa de Infraestructura - Cache (2 horas)

- [ ] Crear `cache/cache_interface.py`:
  - [ ] ABC `Cache` con métodos `get()` y `set()`

- [ ] Crear `cache/memory_cache.py`:
  - [ ] Clase `MemoryCache` implementa `Cache`
  - [ ] Thread-safe con `threading.Lock`
  - [ ] Migrar variables globales `ultima_respuesta_valida`, `ultimo_timestamp`

- [ ] Tests unitarios de caché:
  - [ ] `test_memory_cache_set_get()`
  - [ ] `test_memory_cache_get_missing_key()`
  - [ ] `test_memory_cache_thread_safety()`

### 4. Capa de Servicios - API Client (2 horas)

- [ ] Crear `services/api_client.py`:
  - [ ] ABC `ApiClient` con método `get()`
  - [ ] Clase `RequestsApiClient` implementa `ApiClient`
  - [ ] Clase `MockApiClient` para testing

- [ ] Tests unitarios de API client:
  - [ ] `test_requests_client_success()`
  - [ ] `test_requests_client_timeout()`
  - [ ] `test_requests_client_connection_error()`
  - [ ] `test_mock_client_returns_data()`

### 5. Capa de Servicios - Business Logic (3 horas)

- [ ] Crear `services/termostato_service.py`:
  - [ ] Clase `TermostatoService`
  - [ ] Constructor con inyección: `__init__(api_client, cache)`
  - [ ] Migrar `obtener_estado_termostato()` → `obtener_estado()`
  - [ ] Métodos para cada endpoint del backend

- [ ] Tests unitarios de servicio:
  - [ ] `test_obtener_estado_exitoso()`
  - [ ] `test_obtener_estado_usa_cache()`
  - [ ] `test_obtener_historial()`
  - [ ] Tests con mocks inyectados (no `@patch`)

### 6. Capa de Presentación - Routes (3 horas)

- [ ] Crear `routes/main.py`:
  - [ ] Blueprint `main`
  - [ ] Migrar ruta `GET /`
  - [ ] Usar `current_app.termostato_service`

- [ ] Crear `routes/api.py`:
  - [ ] Blueprint `api` con prefix `/api`
  - [ ] Migrar rutas:
    - `GET /api/estado`
    - `GET /api/historial`
  - [ ] Usar `current_app.termostato_service`

- [ ] Crear `routes/health.py` (opcional):
  - [ ] Blueprint `health`
  - [ ] Migrar `GET /health`

### 7. Configuración (1 hora)

- [ ] Crear `config.py`:
  - [ ] Clases de configuración: `Config`, `DevelopmentConfig`, `TestingConfig`, `ProductionConfig`
  - [ ] Migrar configuración desde `__init__.py`

### 8. Application Factory (2 horas)

- [ ] Refactorizar `webapp/__init__.py`:
  - [ ] Función `create_app(config_name='default')`
  - [ ] Inicializar extensiones (Bootstrap, Moment)
  - [ ] Crear dependencias (cache, api_client)
  - [ ] Inyectar en servicios
  - [ ] Registrar blueprints
  - [ ] Eliminar todo el código legacy

### 9. Actualizar Tests (4 horas)

- [ ] Adaptar `tests/test_app.py`:
  - [ ] Usar `create_app()` en fixture `client`
  - [ ] Actualizar fixture `reset_cache` para usar nuevo sistema
  - [ ] Simplificar tests (no más `@patch('webapp.requests.get')`)
  - [ ] Agregar tests por capa

- [ ] Crear `tests/test_services.py`
- [ ] Crear `tests/test_cache.py`
- [ ] Crear `tests/test_api_client.py`

### 10. Documentación (2 horas)

- [ ] Actualizar `README.md`:
  - [ ] Nueva sección "Arquitectura"
  - [ ] Diagrama de capas
  - [ ] Flujo de datos

- [ ] Crear `docs/arquitectura.md`:
  - [ ] Descripción detallada de cada capa
  - [ ] Principios de diseño aplicados
  - [ ] Diagrama de dependencias

- [ ] Docstrings completos en todos los módulos

### 11. Validación Final (2 horas)

- [ ] Ejecutar suite completa de tests: `pytest`
- [ ] Verificar cobertura: `pytest --cov=webapp --cov-report=html`
- [ ] Análisis de calidad: `/quality-check webapp/`
- [ ] mypy: `mypy webapp/`
- [ ] Pylint: `pylint webapp/`
- [ ] Prueba manual en desarrollo: `python app.py`

---

## Estimación

| Tarea | Horas | Complejidad |
|-------|-------|-------------|
| Preparación | 2 | Baja |
| Models | 1 | Baja |
| Cache | 2 | Media |
| API Client | 2 | Media |
| Business Logic | 3 | Alta |
| Routes | 3 | Media |
| Config | 1 | Baja |
| App Factory | 2 | Alta |
| Tests | 4 | Alta |
| Documentación | 2 | Baja |
| Validación | 2 | Media |
| **TOTAL** | **24 horas** | - |

**Story Points:** 13 (Fibonacci: 13 ≈ 2-3 días de desarrollo)

---

## Definición de Hecho (DoD)

- [x] Código revisado por al menos 1 desarrollador senior
- [x] Tests unitarios y de integración pasan al 100%
- [x] Cobertura de código ≥ 100% (sin regresiones)
- [x] Pylint score ≥ 9.5/10
- [x] mypy sin errores (strict mode)
- [x] Documentación actualizada
- [x] ADR-001 marcado como "Implementado"
- [x] Desplegado en ambiente de staging
- [x] Pruebas manuales exitosas
- [x] Sin deuda técnica introducida

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Regresión funcional | Media | Crítico | Tests E2E exhaustivos antes de merge |
| Aumento complejidad percibida | Alta | Medio | Documentación clara + onboarding session |
| Incremento tiempo desarrollo | Media | Medio | Pair programming en partes críticas |
| Conflictos con otras ramas | Baja | Alto | Merge frecuente desde develop |
| Tests difíciles de adaptar | Media | Alto | Empezar con tests, luego código |

---

## Dependencias

### Bloquea a:
- US-002: Inyección de dependencias (depende de esta estructura)
- US-004: DTOs Pydantic (requiere capa de models)
- US-005: Cache robusto (requiere abstracción de cache)
- US-007: Blueprints (requiere separación de routes)

### Depende de:
- Ninguna (es la base)

---

## Notas Técnicas

### Migración de Variables Globales

**Antes:**
```python
# webapp/__init__.py
ultima_respuesta_valida = None
ultimo_timestamp = None
```

**Después:**
```python
# cache/memory_cache.py
class MemoryCache:
    def __init__(self):
        self._data = {}
        self._lock = threading.Lock()
```

### Migración de Lógica de Negocio

**Antes:**
```python
def obtener_estado_termostato():
    global ultima_respuesta_valida, ultimo_timestamp
    respuesta = requests.get(url, timeout=5)
    datos = respuesta.json()
    ultima_respuesta_valida = datos
    return datos, timestamp, False
```

**Después:**
```python
# services/termostato_service.py
class TermostatoService:
    def __init__(self, api_client: ApiClient, cache: Cache):
        self._api_client = api_client
        self._cache = cache

    def obtener_estado(self) -> Tuple[dict, str, bool]:
        try:
            datos = self._api_client.get('/termostato/')
            timestamp = datetime.utcnow().isoformat()
            self._cache.set('estado', (datos, timestamp))
            return datos, timestamp, False
        except:
            cached = self._cache.get('estado')
            if cached:
                return cached[0], cached[1], True
            return None, None, False
```

---

## Referencias

- ADR-001: Arquitectura por Capas
- [Clean Architecture - Robert Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Flask Blueprints](https://flask.palletsprojects.com/en/2.3.x/blueprints/)

---

**Asignado a:** -
**Fecha Inicio:** -
**Fecha Fin Estimada:** -
**Estado Actual:** 📋 Planificado
