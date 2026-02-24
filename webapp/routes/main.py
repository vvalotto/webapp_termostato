"""
Blueprint para la interfaz web principal del termostato.
Ruta: GET / — renderiza el dashboard con SSR.
"""
from flask import Blueprint, render_template, current_app

from webapp.forms import TermostatoForm

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Página principal que muestra el dashboard del termostato.

    Obtiene el estado del termostato via TermostatoService y lo
    presenta en el template usando Server-Side Rendering (SSR).

    Returns:
        HTML renderizado con el estado del termostato.
    """
    formulario = TermostatoForm()
    servicio = current_app.termostato_service

    datos, timestamp, _ = servicio.obtener_estado()

    if datos:
        formulario.temperatura_ambiente = datos.get('temperatura_ambiente', 'N/A')
        formulario.temperatura_deseada = datos.get('temperatura_deseada', 'N/A')
        formulario.carga_bateria = datos.get('carga_bateria', 'N/A')
        formulario.indicador_bateria = datos.get('indicador', 'N/A')
        formulario.estado_climatizador = datos.get('estado_climatizador', 'N/A')
    else:
        formulario.temperatura_ambiente = 'Error API'
        formulario.temperatura_deseada = 'Error API'
        formulario.carga_bateria = 'Error API'
        formulario.indicador_bateria = 'Error API'
        formulario.estado_climatizador = 'Error API'

    return render_template('index.html', form=formulario, timestamp=timestamp)
