"""
Aplicación web Flask para visualización de datos del termostato.
Consume la API REST del backend (app_termostato) y muestra los datos en una interfaz web.
"""
import os

from flask import Flask, render_template
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


def obtener_dato_api(endpoint):
    """
    Obtiene datos de la API del termostato.

    Args:
        endpoint: Ruta del endpoint (ej: '/termostato/temperatura_ambiente/')

    Returns:
        dict: Respuesta JSON de la API o None si hay error
    """
    try:
        url = URL_APP_API + endpoint
        respuesta = requests.get(url, timeout=5)
        respuesta.raise_for_status()
        return respuesta.json()
    except requests.exceptions.RequestException:
        return None


@app.route("/")
def index():
    """Página principal que muestra el estado del termostato."""
    formulario = TermostatoForm()

    # Obtener datos de la API
    datos_ambiente = obtener_dato_api('/termostato/temperatura_ambiente/')
    datos_deseada = obtener_dato_api('/termostato/temperatura_deseada/')
    datos_bateria = obtener_dato_api('/termostato/bateria/')
    datos_indicador = obtener_dato_api('/termostato/indicador/')
    datos_climatizador = obtener_dato_api('/termostato/estado_climatizador/')

    # Asignar valores al formulario (con valores por defecto si hay error)
    formulario.temperatura_ambiente = datos_ambiente.get('temperatura_ambiente', 'N/A') if datos_ambiente else 'Error API'
    formulario.temperatura_deseada = datos_deseada.get('temperatura_deseada', 'N/A') if datos_deseada else 'Error API'
    formulario.carga_bateria = datos_bateria.get('carga_bateria', 'N/A') if datos_bateria else 'Error API'
    formulario.indicador_bateria = datos_indicador.get('indicador', 'N/A') if datos_indicador else 'Error API'
    formulario.estado_climatizador = datos_climatizador.get('estado_climatizador', 'N/A') if datos_climatizador else 'Error API'

    return render_template("index.html", form=formulario)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
