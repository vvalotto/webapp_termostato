# Webapp Termostato

Aplicación web Flask para visualización del estado de un termostato. Actúa como frontend consumiendo la API REST del backend `app_termostato`.

## Descripción

Este proyecto es parte de un caso de estudio académico/didáctico que demuestra la arquitectura cliente-servidor con separación de frontend y backend.

La aplicación muestra en un **dashboard moderno tipo IoT**:
- Temperatura ambiente actual
- Temperatura deseada configurada
- Estado del climatizador (encendido/apagado)
- Voltaje de la batería (en voltios)
- Nivel de carga de batería (normal/bajo)
- **Gráfica de evolución de temperatura** (últimos 5 minutos)
- **Gráfica de historial del climatizador** (últimos 5 minutos)

## Arquitectura

```
┌─────────────────────┐         ┌─────────────────────┐
│  webapp_termostato  │  HTTP   │   app_termostato    │
│     (Frontend)      │ ──────► │     (Backend)       │
│     Puerto 5001     │  REST   │     Puerto 5050     │
└─────────────────────┘         └─────────────────────┘
```

## Requisitos

- Python 3.8+
- Flask
- Flask-Bootstrap
- Flask-Moment
- Flask-WTF
- Requests

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd webapp_termostato
```

2. Crear entorno virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

O manualmente:
```bash
pip install flask flask-bootstrap flask-moment flask-wtf requests
```

## Configuración

La aplicación usa variables de entorno para configuración:

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `SECRET_KEY` | Clave secreta para sesiones Flask | `clave-desarrollo-local` |
| `API_URL` | URL del backend API (Render) | `http://localhost:5050` |
| `URL_APP_API` | URL del backend API (alternativo) | `http://localhost:5050` |

**Nota**: La aplicación prioriza `API_URL` sobre `URL_APP_API` para compatibilidad con Render.

Ejemplo de configuración:
```bash
export SECRET_KEY="mi-clave-secreta"
export API_URL="http://localhost:5050"
```

## Ejecución

1. Asegurarse de que el backend (`app_termostato`) esté ejecutándose en el puerto 5050.

2. Ejecutar la aplicación:
```bash
python lanzador.py
```

3. Acceder en el navegador: http://localhost:5001

## Estructura del Proyecto

```
webapp_termostato/
├── lanzador.py          # Punto de entrada de la aplicación
├── forms.py             # Definición de formularios WTForms
├── templates/
│   ├── base.html        # Template base con navbar, CSS y Chart.js
│   ├── index.html       # Dashboard principal con cards y gráficas
│   ├── 404.html         # Página de error 404
│   └── 500.html         # Página de error 500
├── static/
│   ├── js/
│   │   └── graficas.js  # Módulo JavaScript para gráficas (Chart.js)
│   ├── styles.css       # Estilos CSS personalizados (dashboard moderno)
│   └── proyecto.ico     # Favicon de la aplicación
├── requirements.txt     # Dependencias Python
├── DEPLOY_RENDER.md     # Guía de despliegue en Render
└── README.md            # Este archivo
```

## Endpoints Consumidos

La aplicación consume los siguientes endpoints del backend:

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/termostato/temperatura_ambiente/` | Obtiene temperatura ambiente |
| GET | `/termostato/temperatura_deseada/` | Obtiene temperatura deseada |
| GET | `/termostato/bateria/` | Obtiene voltaje de la batería |
| GET | `/termostato/nivel_de_carga/` | Obtiene nivel de carga (normal/bajo) |
| GET | `/termostato/estado_climatizador/` | Obtiene estado del climatizador |

## Características

### Interfaz de Usuario
- **Dashboard moderno**: Diseño tipo IoT con cards horizontales y colores distintivos
- **Cards interactivas**: Tres zonas visuales (Ambiente, Climatizador, Batería)
- **Iconos Glyphicon**: Iconos semitransparentes de fondo en cada card
- **Efectos visuales**: Sombras, bordes redondeados, y efecto hover
- **Badges dinámicos**:
  - Estado del climatizador: Verde (encendido) / Gris (apagado)
  - Nivel de batería: Azul (normal) / Rojo pulsante (bajo)
- **Diseño responsive**: Se adapta a desktop (3 columnas), tablet y móvil (apiladas)
- **Fondo degradado**: Gradiente violeta/púrpura moderno

### Funcionalidad
- **Auto-refresh**: La página se actualiza automáticamente cada 10 segundos
- **Manejo de errores**: Muestra "Error API" si el backend no responde
- **Métricas grandes**: Números destacados para fácil lectura
- **Unidades claras**: °C para temperaturas, V para voltaje de batería
- **Gráficas en tiempo real**: Visualización histórica de los últimos 5 minutos
- **Persistencia local**: Datos almacenados en localStorage del navegador
- **Limpieza automática**: Solo se guardan datos de los últimos 5 minutos

### Gráficas Interactivas
- **Gráfica de Temperatura**:
  - Línea suave con relleno (color turquesa)
  - Muestra evolución de temperatura ambiente
  - Se actualiza cada 10 segundos
  - Ventana temporal: últimos 5 minutos
- **Gráfica de Climatizador**:
  - Línea escalonada (ideal para estados binarios)
  - Código de colores: Verde (encendido) / Gris (apagado)
  - Puntos coloreados según el estado
  - Ventana temporal: últimos 5 minutos

### Tecnologías UI
- Bootstrap 3 (grid system y componentes)
- CSS3 (animaciones, gradientes, transformaciones)
- Jinja2 (templates con lógica condicional para badges)
- Chart.js 4.4 (gráficas interactivas)
- JavaScript modular (código organizado en módulos)
- LocalStorage API (persistencia de datos en el navegador)

## Vista del Dashboard

El dashboard presenta tres cards principales dispuestas horizontalmente:

### 🌡️ Card Ambiente (Azul)
- Icono de fuego de fondo
- Temperatura Actual en °C
- Temperatura Deseada en °C
- Números grandes para fácil lectura

### ⚡ Card Climatizador (Verde)
- Icono de refresh de fondo
- Estado del sistema con badge dinámico
- Verde brillante cuando está encendido
- Gris cuando está apagado

### 🔋 Card Batería (Naranja)
- Icono de rayo de fondo
- Voltaje de la batería (en voltios)
- Badge de nivel de carga:
  - Azul para nivel "NORMAL"
  - Rojo pulsante para nivel "BAJO" (con animación de alerta)

### 📊 Gráficas de Evolución
Debajo de las cards principales se muestran dos gráficas:
- **Gráfica de Temperatura**: Evolución temporal con línea suave
- **Gráfica de Climatizador**: Historial de estados (encendido/apagado) con línea escalonada

**Diseño responsive**: En móviles las cards se apilan verticalmente para mejor visualización.

## Proyecto Relacionado

Este frontend requiere el backend API:
- **app_termostato**: API REST que gestiona los datos del termostato

## Notas Técnicas

### Formato de Respuestas de la API

La aplicación espera que el backend devuelva respuestas JSON con el siguiente formato:

```json
// /termostato/temperatura_ambiente/
{"temperatura_ambiente": "22"}

// /termostato/temperatura_deseada/
{"temperatura_deseada": "25"}

// /termostato/bateria/
{"carga_bateria": "12.6"}  // Voltaje en voltios

// /termostato/nivel_de_carga/
{"nivel_de_carga": "normal"}  // o "bajo"

// /termostato/estado_climatizador/
{"estado_climatizador": "encendido"}  // o "apagado"
```

### Troubleshooting

**Los estilos no se cargan correctamente**:
- Asegúrate de hacer un refresh forzado del navegador (Ctrl+Shift+R o Cmd+Shift+R)
- Verifica que el archivo `static/styles.css` exista
- Verifica que `base.html` incluya el link al CSS

**Error "Error API" en los campos**:
- Verifica que el backend esté ejecutándose en el puerto configurado
- Revisa que la variable `API_URL` o `URL_APP_API` apunte a la URL correcta
- Verifica la conectividad de red entre frontend y backend

**El dashboard no se actualiza**:
- La página tiene auto-refresh cada 10 segundos
- Si el backend no responde, mostrará "Error API"

**Las gráficas no se muestran o están vacías**:
- Las gráficas necesitan al menos un dato para mostrarse
- Espera 10 segundos (un ciclo de auto-refresh) para que se capture el primer dato
- Abre la consola del navegador (F12) y busca errores de JavaScript
- Verifica que Chart.js se haya cargado correctamente desde el CDN

**Limpiar el histórico de las gráficas**:
Para borrar todos los datos almacenados en localStorage, abre la consola del navegador y ejecuta:
```javascript
localStorage.removeItem('temperatura_historico');
localStorage.removeItem('climatizador_historico');
```

**Cambiar la ventana de tiempo de las gráficas**:
Por defecto, las gráficas muestran los últimos 5 minutos. Para cambiar este valor:
1. Edita el archivo `static/js/graficas.js`
2. Modifica la constante `VENTANA_TIEMPO_MS` en la línea 9:
```javascript
const VENTANA_TIEMPO_MS = 10 * 60 * 1000; // 10 minutos
```

## Arquitectura del Código JavaScript

El módulo `static/js/graficas.js` está organizado de manera modular:

### Configuración Global
- `VENTANA_TIEMPO_MS`: Ventana temporal de 5 minutos
- `filtrarPorTiempo()`: Función utilitaria para filtrar datos antiguos

### Módulo de Temperatura
- `obtenerTemperaturaActual()`: Extrae temperatura del DOM
- `cargarHistoricoTemperatura()`: Lee y filtra datos de localStorage
- `guardarHistoricoTemperatura()`: Guarda solo datos recientes
- `agregarTemperatura()`: Agrega punto y limpia histórico
- `actualizarGraficaTemperatura()`: Renderiza gráfica con Chart.js

### Módulo de Climatizador
- `obtenerEstadoClimatizador()`: Extrae estado del DOM
- `cargarHistoricoClimatizador()`: Lee y filtra datos de localStorage
- `guardarHistoricoClimatizador()`: Guarda solo datos recientes
- `agregarEstadoClimatizador()`: Agrega punto y limpia histórico
- `actualizarGraficaClimatizador()`: Renderiza gráfica con Chart.js

### Inicialización
- `inicializarGraficas()`: Punto de entrada ejecutado al cargar el DOM

Este diseño sigue los principios de:
- **Alta cohesión**: Cada función tiene una responsabilidad única
- **Bajo acoplamiento**: Módulos independientes
- **Separación de responsabilidades**: HTML (estructura), CSS (presentación), JS (comportamiento)

## Licencia

Proyecto académico/didáctico para el curso ISSE.
