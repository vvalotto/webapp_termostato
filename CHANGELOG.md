# Changelog

Todos los cambios notables de este proyecto seran documentados en este archivo.

El formato esta basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [2.0.0] - 2025-12-26

### Agregado

#### Sprint 1: Fundacion Tecnica
- **WT-12**: Actualizacion sin recarga de pagina
  - Reemplazar meta refresh por AJAX/Fetch
  - Actualizar solo valores que cambian
  - Mantener graficas sin reinicializar
  - Indicador visual de "actualizando..."

- **WT-13**: Usar endpoint unificado de la API
  - Consumir `/termostato/` en lugar de 5 llamadas separadas
  - Crear endpoint local `/api/estado` que proxea a la API
  - Cachear ultima respuesta valida
  - Agregar timestamp de ultima actualizacion

- **WT-10**: Estado de conexion visible
  - Indicador "En linea" / "Sin conexion" visible
  - Timestamp de ultima actualizacion exitosa
  - Cambio visual cuando datos tienen mas de 30s
  - Icono pulsante cuando esta actualizando

#### Sprint 2: Comunicacion Clara
- **WT-8**: Leyenda explicativa del funcionamiento
  - Seccion "Como funciona?" colapsable
  - Explicacion de los 4 estados del climatizador
  - Explicacion de los 3 niveles de bateria
  - Iconos visuales para cada estado

- **WT-9**: Indicadores visuales de tendencia
  - Flecha junto a temperatura actual (subiendo/bajando)
  - Color verde si se acerca a deseada, rojo si se aleja
  - Texto descriptivo: "Subiendo hacia 22C"
  - Icono coherente con estado_climatizador

- **WT-18**: Alerta visual de bateria baja
  - Card verde para NORMAL, naranja para BAJO, rojo para CRITICO
  - Icono de advertencia visible en BAJO y CRITICO
  - Animacion de pulso segun nivel
  - Tooltip con recomendacion

- **WT-19**: Alerta visual de perdida de conexion
  - Banner de advertencia en la parte superior
  - Mostrar "Ultimo dato: hace X minutos"
  - Atenuar cards con datos obsoletos
  - Notificacion cuando se recupera conexion

#### Sprint 3: Robustez
- **WT-21**: Validacion de datos de la API
  - Validar cada campo segun su rango/valores permitidos
  - Mostrar "N/A" si dato esta fuera de rango
  - Mostrar "Error" si dato tiene tipo incorrecto
  - Log en consola de datos invalidos

- **WT-22**: Reintentos automaticos en API
  - 3 reintentos con backoff exponencial
  - Timeout progresivo (2s, 4s, 8s)
  - Mostrar datos anteriores durante reintentos
  - Indicador de "reintentando..."

- **WT-23**: Refactorizar funciones JavaScript largas
  - Dividir funciones de graficas en modulos
  - Ninguna funcion > 50 lineas
  - CSS modularizado en archivos separados
  - 0 warnings en ESLint

#### Sprint 4: Mejoras de Visualizacion
- **WT-11**: Diferencia entre temperatura actual y deseada
  - Mostrar diferencia: "+2.5C para alcanzar objetivo"
  - Barra de progreso visual
  - Colores: azul (frio), verde (OK), rojo (calor)

- **WT-15**: Ventana de tiempo configurable con historial
  - Selector: 5min (localStorage), 1h, 6h, 24h (API historial)
  - Usar `/termostato/historial/?limite=N` para rangos largos
  - Combinar datos locales con historial del servidor
  - Persistir preferencia en localStorage

- **WT-16**: Zona de confort en grafica
  - Linea horizontal en temperatura deseada
  - Zona sombreada de confort (+/-1C de la deseada)
  - Leyenda explicativa
  - Actualizar si cambia temperatura deseada

- **WT-24**: Dashboard responsive mejorado
  - Cards apiladas verticalmente en movil
  - Graficas con scroll horizontal si necesario
  - Botones de tamano tactil (minimo 44px)
  - Fuentes legibles sin zoom

- **WT-26**: Tests unitarios basicos
  - Test de ruta `/` con API funcionando
  - Test de ruta `/` con API caida
  - Test de `/api/estado`
  - Cobertura: 100%

- **WT-27**: Health check endpoint
  - GET `/health` para monitoreo
  - Verificar conexion con `/comprueba/` del backend
  - Retornar 200 si OK, 503 si falla
  - Incluir version frontend y estado backend

### Cambiado

- **Refactoring de estructura del proyecto**
  - Reorganizar codigo en carpeta `webapp/`
  - Renombrar `lanzador.py` a `app.py`
  - Modularizar CSS en archivos separados
  - Modularizar JavaScript en modulos ES6

- **Endpoint unificado**
  - Usar `/termostato/` en lugar de 5 endpoints separados
  - Agregar cache de respuestas

### Desestimado

Las siguientes historias fueron desestimadas por decision del equipo:

- **WT-14**: Transiciones animadas en cambios (Prioridad: Baja)
- **WT-17**: Correlacion temperatura-climatizador (Prioridad: Baja)
- **WT-20**: Alerta visual de temperatura extrema (Prioridad: Media)
- **WT-25**: Modo oscuro (Prioridad: Baja)

## [1.0.0] - 2025-11-26

### Agregado

- Dashboard inicial con cards de temperatura, climatizador y bateria
- Graficas de evolucion de temperatura y climatizador
- Auto-refresh cada 10 segundos
- Integracion con API REST del backend
- Estilos Bootstrap 3 con CSS personalizado
