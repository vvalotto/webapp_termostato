"""
Aplicacion web Flask para visualizacion de datos del termostato.
Application Factory — ensambla capas, extensiones y blueprints.
"""
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from webapp.config import config
from webapp.cache.memory_cache import MemoryCache
from webapp.services.api_client import MockApiClient, RequestsApiClient
from webapp.services.termostato_service import TermostatoService

# Datos fijos usados por MockApiClient en entorno testing
_DATOS_MOCK_TESTING = {
    'temperatura_ambiente': 22,
    'temperatura_deseada': 24,
    'estado_climatizador': 'encendido',
    'carga_bateria': 3.8,
    'indicador': 'NORMAL',
}


def create_app(config_name: str = 'default') -> Flask:
    """Crear y configurar la aplicación Flask.

    Ensambla todas las capas:
    - Configuración según entorno
    - Extensiones Flask (Bootstrap, Moment)
    - Infraestructura (MemoryCache)
    - Servicios (RequestsApiClient, TermostatoService)
    - Blueprints (main, api, health)

    Args:
        config_name: Nombre del entorno de configuración.
            Valores: 'development', 'testing', 'production', 'default'.

    Returns:
        Instancia de Flask configurada y lista para usar.
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Inicializar extensiones
    Bootstrap(app)
    Moment(app)

    # Crear infraestructura
    cache = MemoryCache()
    if app.config.get('TESTING'):
        api_client = MockApiClient(_DATOS_MOCK_TESTING)
    else:
        api_client = RequestsApiClient(
            base_url=app.config['URL_APP_API'],
            timeout=app.config['API_TIMEOUT']
        )

    # Crear servicio e inyectar dependencias
    app.termostato_service = TermostatoService(  # type: ignore[attr-defined]
        api_client=api_client,
        cache=cache
    )

    # Registrar blueprints
    from webapp.routes import main_bp, api_bp, health_bp  # pylint: disable=import-outside-toplevel
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(health_bp)

    return app
