"""
Aplicacion web Flask para visualizacion de datos del termostato.
Consume la API REST del backend (app_termostato) y muestra los datos en una interfaz web.
"""
import os
from datetime import datetime

from flask import Flask, render_template, jsonify, request
from flask_bootstrap import Bootstrap
from flask_moment import Moment
import requests

from .forms import TermostatoForm

# Version del frontend
VERSION = '2.0.0'

# Configuracion de la aplicacion
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave-desarrollo-local')

# Extensiones
bootstrap = Bootstrap(app)
moment = Moment(app)

# Configuracion de la API (API_URL para Render, URL_APP_API como fallback)
URL_APP_API = os.environ.get('API_URL', os.environ.get('URL_APP_API', 'http://localhost:5050'))

# Cache para ultima respuesta valida
ultima_respuesta_valida = None
ultimo_timestamp = None


def obtener_estado_termostato():
    """
    Obtiene todos los datos del termostato en una sola llamada al endpoint unificado.

    Returns:
        tuple: (datos, timestamp, from_cache) donde datos es el dict con todos los valores,
               from_cache indica si son datos cacheados (backend no responde).
               Retorna (None, None, False) si hay error y no hay cache disponible.
    """
    global ultima_respuesta_valida, ultimo_timestamp
    try:
        url = URL_APP_API + '/termostato/'
        respuesta = requests.get(url, timeout=5)
        respuesta.raise_for_status()
        datos = respuesta.json()
        # Cachear respuesta valida
        ultima_respuesta_valida = datos
        ultimo_timestamp = datetime.utcnow().isoformat()
        return datos, ultimo_timestamp, False
    except requests.exceptions.RequestException:
        # Retornar cache si existe
        if ultima_respuesta_valida:
            return ultima_respuesta_valida, ultimo_timestamp, True
        return None, None, False


@app.route("/")
def index():
    """Pagina principal que muestra el estado del termostato."""
    formulario = TermostatoForm()

    # Obtener todos los datos en una sola llamada
    datos, timestamp, _ = obtener_estado_termostato()

    if datos:
        # Asignar valores al formulario desde el endpoint unificado
        formulario.temperatura_ambiente = datos.get('temperatura_ambiente', 'N/A')
        formulario.temperatura_deseada = datos.get('temperatura_deseada', 'N/A')
        formulario.carga_bateria = datos.get('carga_bateria', 'N/A')
        formulario.indicador_bateria = datos.get('indicador', 'N/A')
        formulario.estado_climatizador = datos.get('estado_climatizador', 'N/A')
    else:
        # Sin datos ni cache disponible
        formulario.temperatura_ambiente = 'Error API'
        formulario.temperatura_deseada = 'Error API'
        formulario.carga_bateria = 'Error API'
        formulario.indicador_bateria = 'Error API'
        formulario.estado_climatizador = 'Error API'

    return render_template("index.html", form=formulario, timestamp=timestamp)


@app.route("/api/historial")
def api_historial():
    """
    Endpoint para obtener el historial de temperaturas desde la API backend (WT-15).

    Query params:
        limite: Numero maximo de registros a obtener (default: 60)

    Returns:
        JSON con el historial de temperaturas o error 503 si no hay conexion.
    """
    limite = request.args.get('limite', 60, type=int)
    try:
        url = f"{URL_APP_API}/termostato/historial/?limite={limite}"
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()
        return jsonify({
            'success': True,
            'historial': datos.get('historial', []),
            'total': datos.get('total', 0)
        })
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'No se pudo obtener historial: {str(e)}',
            'historial': []
        }), 503


@app.route("/api/estado")
def api_estado():
    """
    Endpoint JSON para obtener el estado del termostato.
    Util para actualizacion AJAX sin recargar la pagina (WT-12).

    Returns:
        JSON con los datos del termostato o error 503 si no hay conexion.
        Incluye from_cache=True si los datos son cacheados (backend no responde).
    """
    datos, timestamp, from_cache = obtener_estado_termostato()

    if datos:
        return jsonify({
            'success': True,
            'data': datos,
            'timestamp': timestamp,
            'from_cache': from_cache
        })

    return jsonify({
        'success': False,
        'error': 'No se pudo conectar con la API del termostato',
        'timestamp': timestamp
    }), 503


@app.route("/health")
def health():
    """
    Health check endpoint para monitoreo del servicio (WT-27).

    Verifica la conexion con el backend y retorna el estado del sistema.
    Timeout de 2 segundos para cumplir con el requisito de respuesta rapida.

    Returns:
        200: Sistema saludable, backend responde
        503: Backend no disponible
    """
    timestamp = datetime.utcnow().isoformat()
    backend_status = None
    backend_version = None
    backend_uptime = None

    try:
        url = f"{URL_APP_API}/comprueba/"
        respuesta = requests.get(url, timeout=2)
        respuesta.raise_for_status()
        datos_backend = respuesta.json()

        backend_status = datos_backend.get('status', 'unknown')
        backend_version = datos_backend.get('version', 'unknown')
        backend_uptime = datos_backend.get('uptime_seconds')

        return jsonify({
            'status': 'ok',
            'timestamp': timestamp,
            'frontend': {
                'version': VERSION,
                'status': 'ok'
            },
            'backend': {
                'status': backend_status,
                'version': backend_version,
                'uptime_seconds': backend_uptime,
                'url': URL_APP_API
            }
        }), 200

    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'degraded',
            'timestamp': timestamp,
            'frontend': {
                'version': VERSION,
                'status': 'ok'
            },
            'backend': {
                'status': 'unavailable',
                'error': str(e),
                'url': URL_APP_API
            }
        }), 503
