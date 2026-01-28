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

```mermaid
C4Component
    title Diagrama de Componentes - Backend (Flask)

    Container(spa, "Cliente Browser", "JavaScript")
    System_Ext(api_ext, "API Externa", "HTTP")

    Container_Boundary(flask_app, "Flask Application") {
        Component(routes, "Rutas (Views)", "webapp/__init__.py", "Maneja /, /api/estado, /health")
        Component(forms, "Formularios", "webapp/forms.py", "Definición de WTForms para la UI")
        Component(service, "Servicio de Datos", "obtener_estado_termostato()", "Lógica de petición HTTP y Caché en memoria")
        Component(templates, "Templates", "Jinja2 / HTML", "Estructura visual base")
    }

    Rel(spa, routes, "Solicita datos JSON", "/api/estado")
    Rel(routes, forms, "Instancia")
    Rel(routes, service, "Invoca")
    Rel(routes, templates, "Renderiza")
    Rel(service, api_ext, "Requests GET", "Timeout 5s")
```

### 3.2 Componentes del Cliente (JavaScript)

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

1.  **Caché en Memoria (Fallback)**:
    *   El servidor Flask mantiene una variable global `ultima_respuesta_valida`.
    *   Si la API externa falla (timeout o error 500), Flask sirve los últimos datos conocidos con un flag `from_cache=True`.
    *   Esto permite que el frontend detecte la desconexión pero siga mostrando datos útiles.

2.  **Polling vs WebSockets**:
    *   Se optó por **Polling (AJAX)** cada 10 segundos en lugar de WebSockets por simplicidad y robustez ante desconexiones inestables.
    *   El módulo `api.js` implementa una lógica de "Backoff exponencial" para reintentos si la conexión falla.

3.  **Validación en Capas**:
    *   El Frontend (`validacion.js`) valida rangos y tipos de datos antes de renderizar para evitar romper las gráficas con datos corruptos.
