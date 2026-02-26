Feature: Dashboard del termostato funciona tras migración a ES6 (US-003)
  Como usuario del sistema
  Quiero que el dashboard siga funcionando correctamente
  Para no perder funcionalidad tras la modernización del código JavaScript

  Scenario: El dashboard se carga y muestra datos actualizados
    Given el usuario abre el dashboard del termostato
    When la página termina de cargar
    Then se muestran los datos de temperatura y climatizador
    And el indicador de conexión muestra "Conectado"

  Scenario: Los datos se actualizan automáticamente cada 10 segundos
    Given el usuario tiene el dashboard abierto
    When transcurren 10 segundos
    Then los datos se actualizan sin recargar la página

  Scenario: Se muestran reintentos cuando la API falla temporalmente
    Given el usuario tiene el dashboard abierto
    When la API no responde en el primer intento
    Then se muestra el indicador de reintentando
    And el sistema vuelve a intentarlo automáticamente

  Scenario: El banner de desconexión aparece cuando la API falla
    Given el usuario tiene el dashboard abierto
    When la API deja de responder
    Then aparece el banner de desconexión
    And el usuario puede cerrarlo manualmente

  Scenario: Las gráficas de temperatura y climatizador se renderizan
    Given el usuario tiene el dashboard abierto
    When la página termina de cargar
    Then la gráfica de temperatura es visible
    And la gráfica de climatizador es visible

  Scenario: El selector de rango de tiempo actualiza las gráficas
    Given el usuario tiene el dashboard con gráficas visibles
    When selecciona un rango de tiempo diferente
    Then las gráficas se actualizan con el nuevo rango

  Scenario: Navegador sin soporte ES6 recibe mensaje claro
    Given un usuario con un navegador que no soporta módulos ES6
    When abre el dashboard
    Then ve un mensaje indicando que debe actualizar su navegador
