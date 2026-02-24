Feature: Refactorizar backend en arquitectura por capas (US-001)
  Como desarrollador del equipo
  Quiero refactorizar el backend en arquitectura por capas
  Para mejorar la cohesión, reducir el acoplamiento y facilitar el testing

  Background:
    Given la aplicación web está iniciada con la nueva arquitectura por capas
    And el servicio de termostato está disponible

  # --- Criterios Funcionales ---

  Scenario: Dashboard renderiza correctamente con API disponible
    Given la API backend responde con datos válidos del termostato
    When el usuario accede a la ruta principal "/"
    Then la respuesta tiene código HTTP 200
    And el dashboard muestra la temperatura ambiente
    And el dashboard muestra la temperatura deseada
    And el dashboard muestra el estado del climatizador

  Scenario: Endpoint de estado retorna JSON del termostato
    Given la API backend responde con datos válidos del termostato
    When se hace una petición GET a "/api/estado"
    Then la respuesta tiene código HTTP 200
    And la respuesta JSON contiene "success" igual a true
    And la respuesta JSON contiene los datos del termostato
    And el campo "from_cache" es false

  Scenario: Endpoint de historial retorna datos con parámetro límite
    Given la API backend responde con historial de temperaturas
    When se hace una petición GET a "/api/historial?limite=10"
    Then la respuesta tiene código HTTP 200
    And la respuesta JSON contiene "success" igual a true
    And la respuesta JSON contiene la lista "historial"
    And la petición al backend incluye el parámetro "limite=10"

  Scenario: Endpoint de health retorna estado del sistema
    Given la API backend está disponible y responde al health check
    When se hace una petición GET a "/health"
    Then la respuesta tiene código HTTP 200
    And la respuesta JSON contiene "status" igual a "ok"
    And la respuesta incluye información del frontend y del backend

  Scenario: Cache actúa como fallback cuando la API falla
    Given la API backend respondió exitosamente en la última petición
    And la API backend ya no está disponible
    When el usuario accede a la ruta principal "/"
    Then la respuesta tiene código HTTP 200
    And el dashboard muestra los últimos datos cacheados

  Scenario: Valores inválidos se muestran como error en el dashboard
    Given la API backend no está disponible y no hay datos en caché
    When el usuario accede a la ruta principal "/"
    Then la respuesta tiene código HTTP 200
    And el dashboard muestra "Error API" en los campos de temperatura

  Scenario: API de estado retorna 503 cuando no hay datos ni caché
    Given la API backend no está disponible y no hay datos en caché
    When se hace una petición GET a "/api/estado"
    Then la respuesta tiene código HTTP 503
    And la respuesta JSON contiene "success" igual a false

  # --- Criterios de Arquitectura ---

  Scenario: El servicio de termostato es independiente del cliente HTTP
    Given existe una implementación mock del cliente API
    When se inyecta el mock en el servicio de termostato
    Then el servicio obtiene datos usando el cliente inyectado
    And no se realizan peticiones HTTP reales

  Scenario: El caché es una abstracción independiente
    Given existe una implementación en memoria del caché
    When se inyecta el caché en el servicio de termostato
    Then el servicio almacena y recupera datos usando el caché inyectado
    And el caché puede ser reemplazado sin modificar el servicio

  Scenario: Las rutas están organizadas en blueprints separados
    Given la aplicación está creada con la factory "create_app"
    When se inspeccionan los blueprints registrados
    Then existe un blueprint para las rutas de interfaz de usuario
    And existe un blueprint para las rutas de API JSON
