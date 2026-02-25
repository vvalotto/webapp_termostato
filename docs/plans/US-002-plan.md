# Plan de Implementación: US-002 — Implementar Inyección de Dependencias

**Patrón:** Layered Architecture (Flask BFF)
**Producto:** webapp_termostato
**Estimación Total:** 1h 55min

---

## Contexto

US-001 implementó la estructura base de DI (ABCs, `TermostatoService`, `create_app`).
El **delta real de US-002** se concentra en:
- Excepciones custom para desacoplar el servicio de `requests`
- `MockApiClient` para eliminar `@patch` en tests de rutas
- TTL y `delete()` en la abstracción de caché
- Actualizar `create_app('testing')` para inyectar el mock automáticamente

---

## Componentes a Implementar

### 1. Excepciones custom + MockApiClient (Capa de Servicios)

- [x] `webapp/services/api_client.py` — Agregar excepciones custom (15 min)
  - `ApiError(Exception)` — base de todos los errores de API
  - `ApiConnectionError(ApiError)` — error de red o conexión rechazada
  - `ApiTimeoutError(ApiError)` — petición excede el timeout
  - Actualizar `RequestsApiClient.get()` para capturar `requests.exceptions.*`
    y re-lanzar como excepciones custom

- [x] `webapp/services/api_client.py` — Agregar `MockApiClient` (20 min)
  - `MockApiClient(ApiClient)` con constructor `(mock_data: dict)`
  - Atributos de introspección: `call_count: int`, `last_path: str | None`
  - Soporte para modo error: `MockApiClient(mock_data, raise_error=ApiConnectionError)`
  - `get()` devuelve `mock_data` o lanza `raise_error` si está configurado

### 2. TTL y delete() en la abstracción de caché (Capa de Caché)

- [x] `webapp/cache/cache_interface.py` — Extender la interfaz (10 min)
  - Agregar parámetro `ttl: Optional[int] = None` a `set()`
  - Agregar método abstracto `delete(key: str) -> None`

- [x] `webapp/cache/memory_cache.py` — Implementar TTL y delete (20 min)
  - Cambiar estructura interna: `_data[key] = {'value': ..., 'expires': datetime | None}`
  - `set()`: calcular `expires = now + timedelta(seconds=ttl)` si `ttl` es provisto
  - `get()`: verificar expiración antes de devolver; si expirado, eliminar y devolver `None`
  - `delete()`: eliminar clave si existe, ignorar si no existe

### 3. Desacoplar TermostatoService de requests (Capa de Servicios)

- [x] `webapp/services/termostato_service.py` — Reemplazar excepción capturada (10 min)
  - Eliminar `import requests`
  - Reemplazar `except requests.exceptions.RequestException:` por
    `except ApiError:` (usando las nuevas excepciones custom)

### 4. Application Factory con MockApiClient en testing

- [x] `webapp/__init__.py` — Inyectar `MockApiClient` en entorno testing (20 min)
  - En `create_app('testing')`: instanciar `MockApiClient` con datos válidos predefinidos
    (temperatura, batería, climatizador) en lugar de `RequestsApiClient`
  - Extraer datos de mock a constante `DATOS_MOCK_TESTING` dentro del módulo
  - Verificar que `create_app('development')` y `create_app('production')`
    siguen usando `RequestsApiClient`

---

## Integración

- [x] `webapp/routes/api.py` — capturar `ApiError` en lugar de `requests.exceptions.RequestException` (5 min)
- [x] `webapp/routes/health.py` — capturar `ApiError` en lugar de `requests.exceptions.RequestException` (5 min)
- [x] Verificar imports en `webapp/services/__init__.py` y `webapp/cache/__init__.py` (5 min)
  - Exponer `MockApiClient`, `ApiError`, `ApiConnectionError`, `ApiTimeoutError`
    desde `webapp/services/`
  - Exponer `MemoryCache` desde `webapp/cache/`

- [x] Verificar que `tests/test_app.py` puede eliminar `@patch` (15 min)
  - Confirmar que `create_app('testing')` inyecta `MockApiClient`
    y las rutas responden con los datos del mock sin decoradores `@patch`
  - El fixture `reset_cache` sigue siendo necesario (cache persiste entre peticiones)

---

## Orden de Ejecución (bottom-up)

```
1. api_client.py  → excepciones custom + MockApiClient          ✅
2. cache_interface.py → TTL + delete()                          ✅
3. memory_cache.py    → implementar TTL + delete()              ✅
4. termostato_service.py → desacoplar de requests               ✅
5. __init__.py         → MockApiClient en testing               ✅
6. routes/api.py + routes/health.py → capturar ApiError         ✅
7. Verificar exports e imports                                   ✅
8. Eliminar @patch de tests/test_app.py                         ✅
```

**Estado:** 8/8 tareas completadas ✅

> Tests → Fase 4 (unitarios), Fase 5 (integración), Fase 6 (BDD)
> Quality gates → Fase 7
