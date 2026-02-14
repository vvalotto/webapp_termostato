# ADR-001: Refactorizar Backend en Arquitectura por Capas

**Estado:** 📋 Propuesto
**Fecha:** 2026-02-14
**Decisores:** Tech Lead, Backend Team
**Relacionado con:** US-001

---

## Contexto y Problema

El archivo `webapp/__init__.py` actual contiene **199 líneas** que mezclan múltiples responsabilidades:

- Configuración de aplicación Flask
- Variables globales de caché
- Lógica de negocio (obtener datos, transformar, cachear)
- Controladores/Rutas (4 endpoints)
- Cliente HTTP (requests)
- Manejo de errores

**Problemas identificados:**
- ❌ Baja cohesión (múltiples razones de cambio)
- ❌ Alto acoplamiento (todo depende de todo)
- ❌ Difícil de testear (mocks complejos)
- ❌ Violación de SRP (Single Responsibility Principle)
- ❌ Cache global con race conditions en multi-worker

**Código problemático:**

```python
# Todo mezclado en __init__.py
URL_APP_API = os.environ.get('API_URL', 'http://localhost:5050')
ultima_respuesta_valida = None  # Global
ultimo_timestamp = None  # Global

def obtener_estado_termostato():  # Lógica de negocio
    respuesta = requests.get(url, timeout=5)  # Cliente HTTP
    ultima_respuesta_valida = datos  # Cache
    return datos, ultimo_timestamp, False

@app.route("/")  # Controlador
def index():
    datos, timestamp, _ = obtener_estado_termostato()  # Business logic
    formulario.temperatura_ambiente = datos.get(...)  # Transformación
    return render_template(...)  # Vista
```

---

## Consideraciones

### Opción 1: Mantener Monolito (Status Quo)

**Pros:**
- ✅ No requiere cambios
- ✅ Simple para proyecto pequeño

**Contras:**
- ❌ Imposible escalar complejidad
- ❌ Tests difíciles (mocks globales)
- ❌ Violaciones SOLID continuas
- ❌ Race conditions en producción

**Puntuación:** 3/10

---

### Opción 2: Arquitectura por Capas (Clean Architecture simplificada)

**Estructura propuesta:**

```
webapp/
├── __init__.py              # Factory de app (create_app)
├── config.py                # Configuración centralizada
├── models/                  # Capa de Datos
│   ├── __init__.py
│   └── termostato_dto.py    # DTOs Pydantic
├── services/                # Capa de Negocio
│   ├── __init__.py
│   ├── api_client.py        # Abstracción HTTP
│   └── termostato_service.py # Lógica de dominio
├── routes/                  # Capa de Presentación
│   ├── __init__.py
│   ├── main.py              # Rutas principales
│   └── api.py               # Rutas API JSON
└── cache/                   # Infraestructura
    ├── __init__.py
    ├── cache_interface.py   # Abstracción
    └── memory_cache.py      # Implementación
```

**Pros:**
- ✅ Alta cohesión (1 capa = 1 responsabilidad)
- ✅ Bajo acoplamiento (dependencias explícitas)
- ✅ Testeable (inyección de mocks)
- ✅ Cumple SOLID
- ✅ Escalable (agregar features sin modificar existentes)
- ✅ Permite múltiples implementaciones (Redis cache, mock API)

**Contras:**
- ❌ Más archivos (complejidad estructural)
- ❌ Curva de aprendizaje inicial
- ❌ Requiere refactoring extenso (~40 horas)

**Puntuación:** 9/10

---

### Opción 3: Microservicios

**Pros:**
- ✅ Separación total

**Contras:**
- ❌ Overkill para proyecto pequeño
- ❌ Complejidad operacional (orquestación, networking)
- ❌ No resuelve problemas de diseño internos

**Puntuación:** 4/10

---

## Decisión

**Elegimos Opción 2: Arquitectura por Capas**

### Fundamento

La arquitectura por capas ofrece el mejor balance entre:
- Calidad de diseño (SOLID, cohesión, acoplamiento)
- Complejidad razonable (no overkill)
- Testabilidad (crítico para mantener 100% cobertura)
- Escalabilidad futura

### Principios de Diseño

1. **Dependency Inversion (SOLID-D):** Capas superiores dependen de abstracciones, no de implementaciones concretas

```python
# Antes (acoplamiento fuerte):
import requests
respuesta = requests.get(url)

# Después (abstracción):
from services.api_client import ApiClient
def __init__(self, api_client: ApiClient):
    self._client = api_client
```

2. **Single Responsibility (SOLID-S):** Cada módulo/clase tiene una única razón de cambio

- `routes/main.py` → Solo cambia si cambia la UI/HTTP
- `services/termostato_service.py` → Solo cambia si cambia lógica de negocio
- `cache/memory_cache.py` → Solo cambia si cambia estrategia de caché

3. **Open/Closed (SOLID-O):** Abierto a extensión, cerrado a modificación

```python
# Agregar nuevo endpoint sin modificar existentes:
# routes/configuracion.py
@bp.route("/configuracion")
def configuracion():
    # ...

# __init__.py
app.register_blueprint(configuracion_bp)  # Solo agregar
```

---

## Consecuencias

### Positivas

- ✅ **Testabilidad:** 90%+ de código testeable con mocks simples
- ✅ **Mantenibilidad:** Índice de mantenibilidad sube de 65 → 85
- ✅ **Extensibilidad:** Agregar features sin riesgo de regresiones
- ✅ **Onboarding:** Desarrolladores nuevos entienden estructura rápidamente
- ✅ **Debugging:** Trazabilidad clara (stack trace muestra capa exacta)

### Negativas

- ⚠️ **Complejidad estructural:** Más archivos para navegar (mitigado con IDE)
- ⚠️ **Overhead inicial:** 40 horas de refactoring (~1 sprint)
- ⚠️ **Imports más largos:** `from webapp.services.termostato_service import ...`

### Neutras

- 🔄 **Performance:** Sin impacto significativo (overhead de llamadas mínimo)
- 🔄 **Líneas de código:** Incremento ~20% (pero más legible)

---

## Plan de Implementación

### Fase 1: Crear Estructura (2 horas)

```bash
mkdir -p webapp/{models,services,routes,cache}
touch webapp/models/{__init__.py,termostato_dto.py}
touch webapp/services/{__init__.py,api_client.py,termostato_service.py}
touch webapp/routes/{__init__.py,main.py,api.py}
touch webapp/cache/{__init__.py,cache_interface.py,memory_cache.py}
touch webapp/config.py
```

### Fase 2: Migrar Código (8 horas)

1. **Configuración:** `__init__.py` → `config.py`
2. **DTOs:** Crear `models/termostato_dto.py`
3. **API Client:** Abstraer `requests` en `services/api_client.py`
4. **Cache:** Extraer globals a `cache/memory_cache.py`
5. **Service:** Lógica a `services/termostato_service.py`
6. **Routes:** Endpoints a `routes/main.py` y `routes/api.py`

### Fase 3: Inyección de Dependencias (4 horas)

```python
# __init__.py
def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Infraestructura
    cache = MemoryCache()
    api_client = RequestsApiClient(app.config['API_URL'])

    # Servicios (inyección)
    termostato_service = TermostatoService(api_client, cache)
    app.termostato_service = termostato_service

    # Rutas
    from .routes import main, api
    app.register_blueprint(main.bp)
    app.register_blueprint(api.bp)

    return app
```

### Fase 4: Tests (6 horas)

- Adaptar tests existentes
- Agregar tests unitarios por capa
- Mantener 100% cobertura

---

## Validación

### Criterios de Aceptación

- [ ] Pylint score ≥ 9.5/10
- [ ] Complejidad ciclomática < 5 por función
- [ ] 100% cobertura de tests
- [ ] 0 variables globales mutables
- [ ] Todos los servicios inyectables
- [ ] 0 imports de `requests` en routes
- [ ] mypy sin errores (strict mode)

### Métricas Esperadas

| Métrica | Antes | Después |
|---------|-------|---------|
| Archivos Python | 3 | 12 |
| Líneas por archivo (avg) | 66 | 30 |
| Cohesión (1-10) | 6 | 9 |
| Acoplamiento (1-10) | 5 | 8 |
| Violaciones SOLID | 8 | 1 |

---

## Referencias

- [Clean Architecture - Robert Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Flask Application Factories](https://flask.palletsprojects.com/en/2.3.x/patterns/appfactories/)
- [Dependency Injection in Python](https://python-dependency-injector.ets-labs.org/)

---

## Notas

- Esta decisión es **bloqueante** para ADR-002 (Inyección de Dependencias)
- Requiere coordinación con US-004 (DTOs Pydantic) y US-005 (Cache robusto)
- Debe implementarse en rama `feature/US-001-arquitectura-capas`

---

**Aprobadores:**
- [ ] Tech Lead
- [ ] Backend Developer
- [ ] QA Lead

**Fecha de Revisión:** Pendiente
**Estado Final:** Pendiente de aprobación
