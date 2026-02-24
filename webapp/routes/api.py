"""
Blueprint para los endpoints JSON de la API interna del frontend.
Prefijo: /api
Rutas: GET /api/estado, GET /api/historial
"""
from flask import Blueprint, jsonify, request, current_app

import requests as req_lib

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/estado')
def api_estado():
    """Endpoint JSON para obtener el estado del termostato.

    Útil para actualización AJAX sin recargar la página (WT-12).
    Devuelve from_cache=True si los datos provienen del caché local.

    Returns:
        200: JSON con success=True y los datos del termostato.
        503: JSON con success=False si no hay conexión ni caché.
    """
    servicio = current_app.termostato_service
    datos, timestamp, from_cache = servicio.obtener_estado()

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


@api_bp.route('/historial')
def api_historial():
    """Endpoint para obtener el historial de temperaturas (WT-15).

    Query params:
        limite: Número máximo de registros (default: 60).

    Returns:
        200: JSON con success=True, historial y total.
        503: JSON con success=False si el backend no responde.
    """
    limite = request.args.get('limite', 60, type=int)
    servicio = current_app.termostato_service

    try:
        datos = servicio.obtener_historial(limite=limite)
        return jsonify({
            'success': True,
            'historial': datos.get('historial', []),
            'total': datos.get('total', 0)
        })
    except req_lib.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'No se pudo obtener historial: {str(e)}',
            'historial': []
        }), 503
