"""
Blueprint para el health check del sistema (WT-27).
Ruta: GET /health
"""
from datetime import datetime

from flask import Blueprint, jsonify, current_app

from webapp.services.api_client import ApiError

# Versión del frontend — debe coincidir con webapp/__init__.py
VERSION = '2.0.0'

health_bp = Blueprint('health', __name__)


@health_bp.route('/health')
def health():
    """Health check del sistema completo (frontend + backend).

    Verifica la conectividad con el backend y retorna el estado
    de ambos componentes. Timeout de 2 segundos (requisito WT-27).

    Returns:
        200: JSON con status='ok' si el backend responde.
        503: JSON con status='degraded' si el backend no está disponible.
    """
    timestamp = datetime.utcnow().isoformat()
    servicio = current_app.termostato_service

    try:
        datos_backend = servicio.health_check()

        return jsonify({
            'status': 'ok',
            'timestamp': timestamp,
            'frontend': {
                'version': VERSION,
                'status': 'ok'
            },
            'backend': {
                'status': datos_backend.get('status', 'unknown'),
                'version': datos_backend.get('version', 'unknown'),
                'uptime_seconds': datos_backend.get('uptime_seconds'),
                'url': current_app.config['URL_APP_API']
            }
        }), 200

    except ApiError as e:
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
                'url': current_app.config['URL_APP_API']
            }
        }), 503
