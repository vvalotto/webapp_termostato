# Reporte Final — US-002: Implementar Inyección de Dependencias

**Fecha:** 2026-02-25
**Branch:** feature/US-002-inyeccion-dependencias
**Estado:** COMPLETADO

---

## Resumen Ejecutivo

US-002 implementa los tres pilares de inyección de dependencias que faltaban tras US-001:
1. **MockApiClient** — cliente de test sin `@patch`
2. **Excepciones custom** — jerarquía `ApiError` desacoplada de `requests`
3. **MemoryCache con TTL** — expiración nativa de entradas

---

## Cambios Implementados

### Producción (webapp/)

| Archivo | Cambio |
|---------|--------|
| `services/api_client.py` | + `ApiError`, `ApiConnectionError`, `ApiTimeoutError`; + `MockApiClient`; `RequestsApiClient` relanza custom exceptions |
| `cache/cache_interface.py` | + `ttl` en `set()`; + método abstracto `delete()` |
| `cache/memory_cache.py` | Implementa TTL con `datetime`; implementa `delete()` |
| `services/termostato_service.py` | Captura `ApiError` en lugar de `requests.exceptions.RequestException` |
| `services/__init__.py` | Exporta `ApiError`, `ApiConnectionError`, `ApiTimeoutError`, `MockApiClient` |
| `routes/api.py` | Captura `ApiError` en lugar de `req_lib.exceptions.RequestException` |
| `routes/health.py` | Captura `ApiError` en lugar de `req_lib.exceptions.RequestException` |
| `__init__.py` | `create_app('testing')` inyecta `MockApiClient` automáticamente |

### Tests

| Archivo | Cambio |
|---------|--------|
| `tests/test_api_client.py` | + `TestMockApiClient` (9 tests); actualiza asserts de excepciones |
| `tests/test_cache.py` | + `TestMemoryCacheTTL` (5 tests); + `TestMemoryCacheDelete` (3 tests) |
| `tests/test_services.py` | Mocks usan `ApiConnectionError`/`ApiTimeoutError`; quita import requests |
| `tests/test_app.py` | Elimina todos los `@patch`; usa `MockApiClient` via `create_app('testing')` |
| `tests/integration/test_termostato_integration.py` | Reescrito: sin `@patch`, usa `MockApiClient` directo |
| `tests/step_defs/test_us001_steps.py` | Elimina `@patch`; usa `_inyectar_mock()` con `MockApiClient` |
| `tests/step_defs/test_us002_steps.py` | **Nuevo** — 13 escenarios BDD para US-002 |
| `tests/.pylintrc` | **Nuevo** — suprime W0621/W0212 (falsos positivos pytest) |
| `tests/features/US-002-inyeccion-dependencias.feature` | **Nuevo** — 13 escenarios Gherkin |

### Documentación

| Archivo | Cambio |
|---------|--------|
| `docs/plans/US-002-plan.md` | **Nuevo** — plan de implementación |
| `CLAUDE.md` | Actualizado: excepciones custom, MockApiClient, tests sin @patch |

---

## Métricas de Calidad

| Indicador | Valor | Gate | Estado |
|-----------|-------|------|--------|
| Tests totales | 101 | — | 101/101 passing |
| Cobertura | 95% | — | — |
| Complejidad CC máx. (producción) | 4 | ≤ 10 | PASS |
| Índice mantenibilidad mín. | 43.37 | ≥ 20 | PASS |
| Pylint (global) | 8.38/10 | ≥ 8.0 | PASS |
| Función más larga | 47 LOC | ≤ 50 | PASS |

---

## Decisiones de Diseño

**MockApiClient en lugar de @patch:**
El `@patch` de `requests.get` es frágil: acopla los tests al detalle de implementación HTTP. `MockApiClient` es una implementación real de la interfaz `ApiClient` — si la interfaz cambia, el mock falla en compilación, no en runtime.

**Jerarquía ApiError:**
`requests` es un detalle de infraestructura. `TermostatoService` y las rutas no deben saber que el transporte es HTTP. Con `ApiError` se puede cambiar el backend de `requests` a `httpx` o a cualquier otro cliente sin tocar una sola línea de lógica de negocio.

**TTL en MemoryCache:**
El caché sin TTL es un memory leak latente en producción. El TTL permite controlar la frescura de los datos sin lógica externa.

---

## Tests por Capa

```
tests/test_api_client.py    → 19 tests  (RequestsApiClient + MockApiClient)
tests/test_cache.py         → 17 tests  (MemoryCache: set/get, clear, TTL, delete, concurrencia)
tests/test_services.py      → 13 tests  (TermostatoService DI)
tests/test_app.py           → 13 tests  (rutas Flask sin @patch)
tests/integration/          → 16 tests  (flujo HTTP completo)
tests/step_defs/ (US-001)   → 10 tests  (BDD US-001)
tests/step_defs/ (US-002)   → 13 tests  (BDD US-002)
─────────────────────────────────────────
TOTAL                       → 101 tests
```
