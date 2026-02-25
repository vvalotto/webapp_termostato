Feature: Implementar Inyección de Dependencias (US-002)
  Como desarrollador del equipo
  Quiero implementar inyección de dependencias en el backend
  Para reducir el acoplamiento, facilitar el testing con mocks y cumplir SOLID-D

  Background:
    Given la aplicación web está creada con la factory "create_app"

  # --- Criterios: MockApiClient ---

  Scenario: MockApiClient retorna datos configurados al ser inyectado
    Given un MockApiClient configurado con datos válidos del termostato
    When se llama al método get() del MockApiClient
    Then retorna los datos configurados
    And el contador de llamadas se incrementa en 1

  Scenario: MockApiClient registra el último path consultado
    Given un MockApiClient configurado con datos válidos del termostato
    When se llama a get() con el path "/termostato/"
    Then el atributo last_path del mock contiene "/termostato/"

  Scenario: TermostatoService usa el MockApiClient inyectado
    Given un MockApiClient configurado con datos válidos del termostato
    And un TermostatoService con el MockApiClient inyectado
    When se llama a obtener_estado()
    Then el servicio retorna los datos del mock sin realizar peticiones HTTP reales
    And from_cache es false

  Scenario: TermostatoService usa cache cuando el MockApiClient falla
    Given un MockApiClient configurado para lanzar ApiConnectionError
    And un MemoryCache con datos previos almacenados
    And un TermostatoService con el MockApiClient y el cache inyectados
    When se llama a obtener_estado()
    Then el servicio retorna los datos del cache
    And from_cache es true

  Scenario: TermostatoService retorna None cuando falla y el cache está vacío
    Given un MockApiClient configurado para lanzar ApiConnectionError
    And un MemoryCache vacío
    And un TermostatoService con el MockApiClient y el cache inyectados
    When se llama a obtener_estado()
    Then datos es None
    And from_cache es false

  # --- Criterios: Excepciones custom ---

  Scenario: RequestsApiClient lanza ApiConnectionError en error de red
    Given un RequestsApiClient configurado con una URL inaccesible
    When se llama a get() y la conexión es rechazada
    Then se lanza ApiConnectionError

  Scenario: RequestsApiClient lanza ApiTimeoutError cuando la petición excede el timeout
    Given un RequestsApiClient configurado con timeout muy bajo
    When se llama a get() y la petición tarda más del timeout
    Then se lanza ApiTimeoutError

  # --- Criterios: Application Factory con DI ---

  Scenario: create_app testing inyecta MockApiClient automáticamente
    Given la aplicación creada con create_app("testing")
    When se inspecciona el servicio inyectado en la aplicación
    Then el api_client del servicio es una instancia de MockApiClient
    And no se realizan peticiones HTTP reales al backend

  Scenario: Las rutas funcionan sin @patch cuando se usa create_app testing
    Given la aplicación creada con create_app("testing")
    When el usuario accede a la ruta principal "/"
    Then la respuesta tiene código HTTP 200
    And el dashboard muestra datos del termostato

  Scenario: La ruta /api/estado responde con MockApiClient inyectado
    Given la aplicación creada con create_app("testing")
    When se hace una petición GET a "/api/estado"
    Then la respuesta tiene código HTTP 200
    And la respuesta JSON contiene "success" igual a true
    And el campo "from_cache" es false

  # --- Criterios: MemoryCache con TTL ---

  Scenario: MemoryCache almacena y recupera un valor dentro del TTL
    Given un MemoryCache vacío
    When se almacena un valor con TTL de 60 segundos
    Then get() retorna el valor almacenado

  Scenario: MemoryCache retorna None para un valor con TTL expirado
    Given un MemoryCache vacío
    When se almacena un valor con TTL de 1 segundo y espera a que expire
    Then get() retorna None

  Scenario: MemoryCache es thread-safe bajo acceso concurrente
    Given un MemoryCache vacío
    When múltiples hilos escriben y leen simultáneamente
    Then no se producen condiciones de carrera
    And todos los valores son consistentes
