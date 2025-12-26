"""
Aplicación web Flask para visualización de datos del termostato.
Consume la API REST del backend (app_termostato) y muestra los datos en una interfaz web.
"""
import os

from datetime import datetime

from flask import Flask, render_template, jsonify, request
from flask_bootstrap import Bootstrap
from flask_moment import Moment
import requests

from forms import TermostatoForm

# Configuración de la aplicación
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave-desarrollo-local')

# Extensiones
bootstrap = Bootstrap(app)
moment = Moment(app)

# Configuración de la API (API_URL para Render, URL_APP_API como fallback)
URL_APP_API = os.environ.get('API_URL', os.environ.get('URL_APP_API', 'http://localhost:5050'))

# Cache para última respuesta válida
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
        # Cachear respuesta válida
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
    """Página principal que muestra el estado del termostato."""
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
        limite: Número máximo de registros a obtener (default: 60)

    Returns:
        JSON con el historial de temperaturas o error 503 si no hay conexión.
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
    Útil para actualización AJAX sin recargar la página (WT-12).

    Returns:
        JSON con los datos del termostato o error 503 si no hay conexión.
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
