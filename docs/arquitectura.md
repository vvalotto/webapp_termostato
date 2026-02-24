# Arquitectura del Sistema - Modelo C4

Este documento describe la arquitectura de la aplicación **WebApp Termostato** utilizando el modelo C4.

## 1. Diagrama de Contexto (Nivel 1)

Muestra el sistema en el contexto de su entorno y sus interacciones con sistemas externos.

```mermaid
C4Context
    title Diagrama de Contexto - WebApp Termostato

    Person(user, "Usuario", "Usuario que monitorea el termostato")
    System(webapp, "WebApp Termostato", "Panel de control web para visualización de datos y estado.")
    System_Ext(backend_api, "API Termostato (Backend)", "Servicio REST que gestiona el hardware y provee datos.")

    Rel(user, webapp, "Visualiza dashboard", "HTTPS")
    Rel(webapp, backend_api, "Consulta estado e historial", "HTTP/JSON")
```

### Descripción
*   **Usuario**: Accede a la aplicación a través de un navegador web.
*   **WebApp Termostato**: El proyecto actual. Sirve la interfaz gráfica y actúa como proxy/cliente de los datos.
*   **API Termostato**: Sistema externo (puerto 5050) que interactúa con los sensores físicos.

---

## 2. Diagrama de Contenedores (Nivel 2)

Muestra las aplicaciones y almacenes de datos de alto nivel.

```mermaid
C4Container
    title Diagrama de Contenedores - WebApp Termostato

    Person(user, "Usuario", "Navegador Web")

    Container_Boundary(c1, "WebApp Termostato") {
        Container(spa, "Single Page Application", "JavaScript, Bootstrap, Chart.js", "Lógica de cliente, gráficas y actualizaciones AJAX.")
        Container(web_app, "Aplicación Web", "Python, Flask", "Sirve contenido estático, renderiza HTML inicial y proxy de API.")
    }

    System_Ext(backend_api, "API Termostato", "Python/Hardware")

    Rel(user, spa, "Interactúa", "Eventos DOM")
    Rel(user, web_app, "Carga página inicial", "HTTPS/HTML")
    Rel(spa, web_app, "Polling de datos (AJAX)", "JSON")
    Rel(web_app, backend_api, "Fetch de datos", "HTTP/requests")
```

### Descripción
*   **Single Page Application (JS)**: Ejecutada en el navegador del usuario. Gestiona la actualización en tiempo real (polling cada 10s), gráficas y alertas visuales sin recargar la página.
*   **Aplicación Web (Flask)**:
    *   Sirve los assets estáticos y templates Jinja2.
    *   Actúa como **BFF (Backend for Frontend)**: Expone endpoints locales (`/api/estado`) que hacen de puente hacia la API real, manejando timeouts y caché de emergencia.

---

## 3. Diagrama de Componentes (Nivel 3)

Detalla la estructura interna de la aplicación Flask y la organización modular del JavaScript.

### 3.1 Componentes del Servidor (Flask)

Arquitectura por capas implementada en **US-001** (Application Factory + DIP).

```mermaid
C4Component
    title Diagrama de Componentes - Backend (Flask) v3.0

    Container(spa, "Cliente Browser", "JavaScript")
    System_Ext(api_ext, "API Termostato", "HTTP/JSON")

    Container_Boundary(flask_app, "Flask Application") {
        Component(factory, "Application Factory", "webapp/__init__.py", "create_app() — ensambla capas e inyecta dependencias")
        Component(config, "Configuracion", "webapp/config.py", "Config / DevelopmentConfig / TestingConfig / ProductionConfig")

        Component(main_bp, "Blueprint Principal", "webapp/routes/main.py", "GET / — Dashboard SSR con Jinja2")
        Component(api_bp, "Blueprint API", "webapp/routes/api.py", "GET /api/estado, GET /api/historial")
        Component(health_bp, "Blueprint Health", "webapp/routes/health.py", "GET /health — estado frontend y backend")

        Component(service, "TermostatoService", "webapp/services/termostato_service.py", "Logica de negocio: estado, historial, health. DI via constructor.")
        Component(api_client, "RequestsApiClient", "webapp/services/api_client.py", "Cliente HTTP — implementa ApiClient ABC")
        Component(cache, "MemoryCache", "webapp/cache/memory_cache.py", "Cache fallback thread-safe — implementa Cache ABC")

        Component(forms, "TermostatoForm", "webapp/forms.py", "Solo renderizado Jinja2, sin validacion WTF")
        Component(templates, "Templates", "Jinja2 / HTML", "index.html, base.html, 404.html, 500.html")
    }

    Rel(spa, main_bp, "Carga inicial", "HTTPS/HTML")
    Rel(spa, api_bp, "Polling AJAX cada 10s", "JSON")
    Rel(main_bp, service, "obtener_estado()")
    Rel(main_bp, forms, "Instancia para renderizado")
    Rel(main_bp, templates, "Renderiza")
    Rel(api_bp, service, "obtener_estado() / obtener_historial()")
    Rel(health_bp, service, "health_check()")
    Rel(service, api_client, "get(path, timeout)")
    Rel(service, cache, "get / set 'estado'")
    Rel(api_client, api_ext, "HTTP GET", "Timeout configurable")
    Rel(factory, config, "Carga configuracion por entorno")
    Rel(factory, service, "Instancia y adjunta como app.termostato_service")
```

### 3.2 Diagrama de Clases — Inyeccion de Dependencias

Muestra las interfaces (ABCs) y sus implementaciones concretas que permiten el principio de inversion de dependencias (DIP).

```mermaid
classDiagram
    class Cache {
        <<ABC>>
        +get(key: str) Any
        +set(key: str, value: Any) None
        +clear() None
    }
    class MemoryCache {
        -_store: dict
        -_lock: Lock
        +get(key) Any
        +set(key, value) None
        +clear() None
    }
    class ApiClient {
        <<ABC>>
        +get(path: str, **kwargs) dict
    }
    class RequestsApiClient {
        -_base_url: str
        -_timeout: int
        +get(path, **kwargs) dict
    }
    class TermostatoService {
        -_api_client: ApiClient
        -_cache: Cache
        +obtener_estado() tuple
        +obtener_historial(limite) dict
        +health_check() dict
    }

    Cache <|-- MemoryCache : implementa
    ApiClient <|-- RequestsApiClient : implementa
    TermostatoService --> ApiClient : depende de
    TermostatoService --> Cache : depende de
```

### 3.3 Componentes del Cliente (JavaScript)

La lógica de cliente ha sido refactorizada en módulos (ES5/ES6 pattern) para mantenibilidad.

```mermaid
classDiagram
    class App {
        +iniciarActualizacion()
        +procesarDatos()
    }
    class API {
        +obtenerEstado()
        +fetchConTimeout()
    }
    class Conexion {
        +gestionarEstadoOffline()
        +reintentos()
    }
    class Graficas {
        +renderizarChartJS()
        +gestionarHistorial()
    }
    class UI_Utils {
        +actualizarDOM()
        +validarDatos()
    }

    App --> API : Usa
    App --> Conexion : Monitorea
    App --> Graficas : Actualiza
    App --> UI_Utils : Manipula DOM
    API ..> Conexion : Notifica errores
```

## Decisiones de Diseño Clave

1.  **Caché en Memoria como Fallback (MemoryCache)**:
    *   `MemoryCache` (en `webapp/cache/memory_cache.py`) almacena la última respuesta válida bajo la clave `'estado'` como tupla `(datos, timestamp)`.
    *   Implementa la interfaz `Cache` (ABC), permitiendo sustituirla por Redis u otro backend sin modificar `TermostatoService`.
    *   Usa `threading.Lock` para garantizar seguridad en entornos multi-hilo (Gunicorn).
    *   El servicio **siempre** intenta obtener datos frescos del backend; el caché solo actúa si la API lanza `RequestException` (fallback, no cache-first).
    *   El flag `from_cache=True` en la respuesta JSON permite que el frontend detecte la desconexión pero siga mostrando datos útiles.

2.  **Inversión de Dependencias (DIP)**:
    *   `TermostatoService` depende de las abstracciones `ApiClient` y `Cache`, no de implementaciones concretas.
    *   Esto permite inyectar mocks en tests sin `@patch` y facilita cambiar la implementación del cliente HTTP o del caché de forma independiente (ver ADR-001, ADR-002).

3.  **Application Factory**:
    *   `create_app(config_name)` en `webapp/__init__.py` elimina el estado global a nivel de módulo.
    *   Permite instanciar múltiples apps con configuraciones distintas (`'testing'`, `'development'`, `'production'`), esencial para tests aislados.

4.  **Polling vs WebSockets**:
    *   Se optó por **Polling (AJAX)** cada 10 segundos en lugar de WebSockets por simplicidad y robustez ante desconexiones inestables.
    *   El módulo `api.js` implementa una lógica de backoff exponencial para reintentos si la conexión falla.

5.  **Validación en Capas**:
    *   El frontend (`validacion.js`) valida rangos y tipos de datos antes de renderizar para evitar romper las gráficas con datos corruptos.

---

Fecha creación: 28/01/2026
Última actualización: 2026-02-24 (US-001 — Arquitectura por capas)
