"""
Tests de integración para webapp_termostato.
Validan el flujo HTTP completo: TestClient → Blueprint → TermostatoService → MemoryCache.
Solo se mockea la llamada HTTP externa (requests.get), el resto es real.
"""
import json
from unittest.mock import Mock, patch

import pytest
import requests

from webapp import create_app

# ---------------------------------------------------------------------------
# Respuestas simuladas del backend externo
# ---------------------------------------------------------------------------

RESPUESTA_ESTADO = {
    'temperatura_ambiente': 21.5,
    'temperatura_deseada': 23.0,
    'estado_climatizador': 'encendido',
    'carga_bateria': 3.9,
    'indicador': 'NORMAL',
}

RESPUESTA_HISTORIAL = {
    'historial': [
        {'timestamp': '2026-01-01T10:00:00', 'temperatura': 21.0},
        {'timestamp': '2026-01-01T10:01:00', 'temperatura': 21.5},
    ],
    'total': 2,
}

RESPUESTA_HEALTH = {
    'status': 'ok',
    'version': '1.1.0',
    'uptime_seconds': 3600,
}

_PATCH_TARGET = 'webapp.services.api_client.requests.get'


def _mock_get_exitoso(url, timeout=5, **kwargs):
    """Simula requests.get devolviendo respuesta válida según URL."""
    respuesta = Mock()
    respuesta.raise_for_status.return_value = None

    if '/termostato/historial/' in url:
        respuesta.json.return_value = RESPUESTA_HISTORIAL
    elif '/comprueba/' in url:
        respuesta.json.return_value = RESPUESTA_HEALTH
    else:
        respuesta.json.return_value = RESPUESTA_ESTADO

    return respuesta


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    """Aplicacion Flask de testing con estado limpio."""
    aplicacion = create_app('testing')
    yield aplicacion
    aplicacion.termostato_service._cache.clear()


@pytest.fixture
def cliente(app):
    """Cliente HTTP de testing."""
    return app.test_client()


# ---------------------------------------------------------------------------
# Tests de integración: flujo completo HTTP
# ---------------------------------------------------------------------------

class TestIntegracionRutaPrincipal:
    """Flujo: GET / → main_bp → TermostatoService → render template."""

    @patch(_PATCH_TARGET, side_effect=_mock_get_exitoso)
    def test_index_renderiza_con_datos_reales(self, _mock, cliente):
        """La ruta principal renderiza datos del servicio real."""
        respuesta = cliente.get('/')

        assert respuesta.status_code == 200

    @patch(_PATCH_TARGET,
           side_effect=requests.exceptions.ConnectionError('sin conexión'))
    def test_index_responde_200_aunque_api_caiga(self, _mock, cliente):
        """La ruta / responde 200 aunque la API esté caída (muestra estado de error)."""
        respuesta = cliente.get('/')

        assert respuesta.status_code == 200

    @patch(_PATCH_TARGET, side_effect=_mock_get_exitoso)
    def test_index_llama_api_en_cada_peticion(self, mock_get, cliente):
        """Cada petición a / llama al backend (caché es solo fallback ante fallos)."""
        cliente.get('/')
        cliente.get('/')

        # El servicio siempre pide datos frescos; la caché solo actúa si la API cae
        assert mock_get.call_count == 2


class TestIntegracionApiEstado:
    """Flujo: GET /api/estado → api_bp → TermostatoService → JSON."""

    @patch(_PATCH_TARGET, side_effect=_mock_get_exitoso)
    def test_api_estado_retorna_json_valido(self, _mock, cliente):
        """GET /api/estado retorna JSON con todos los campos del termostato."""
        respuesta = cliente.get('/api/estado')

        assert respuesta.status_code == 200
        envelope = json.loads(respuesta.data)
        assert envelope['success'] is True
        datos = envelope['data']
        assert datos['temperatura_ambiente'] == 21.5
        assert datos['indicador'] == 'NORMAL'

    @patch(_PATCH_TARGET, side_effect=_mock_get_exitoso)
    def test_api_estado_from_cache_es_false_en_respuesta_fresca(self, _mock, cliente):
        """Datos frescos: from_cache debe ser False."""
        respuesta = cliente.get('/api/estado')
        datos = json.loads(respuesta.data)

        assert datos.get('from_cache') is False

    @patch(_PATCH_TARGET,
           side_effect=requests.exceptions.ConnectionError('sin conexión'))
    def test_api_estado_retorna_503_sin_cache(self, _mock, cliente):
        """Si la API falla y no hay caché, /api/estado retorna 503."""
        respuesta = cliente.get('/api/estado')

        assert respuesta.status_code == 503

    def test_api_estado_sirve_cache_cuando_api_cae(self, cliente):
        """Si la API falla pero hay caché, retorna datos con from_cache=True."""
        # Primera petición: poblar caché con API funcionando
        with patch(_PATCH_TARGET, side_effect=_mock_get_exitoso):
            cliente.get('/api/estado')

        # Segunda petición: API caída — debe usar caché
        with patch(_PATCH_TARGET,
                   side_effect=requests.exceptions.ConnectionError('sin conexión')):
            respuesta = cliente.get('/api/estado')

        assert respuesta.status_code == 200
        datos = json.loads(respuesta.data)
        assert datos.get('from_cache') is True


class TestIntegracionApiHistorial:
    """Flujo: GET /api/historial → api_bp → TermostatoService → JSON."""

    @patch(_PATCH_TARGET, side_effect=_mock_get_exitoso)
    def test_historial_retorna_lista(self, _mock, cliente):
        """GET /api/historial retorna JSON con campo historial."""
        respuesta = cliente.get('/api/historial')

        assert respuesta.status_code == 200
        datos = json.loads(respuesta.data)
        assert 'historial' in datos
        assert len(datos['historial']) == 2

    @patch(_PATCH_TARGET, side_effect=_mock_get_exitoso)
    def test_historial_acepta_parametro_limite(self, mock_get, cliente):
        """GET /api/historial?limite=10 pasa el parámetro al backend."""
        cliente.get('/api/historial?limite=10')

        url_llamada = mock_get.call_args[0][0]
        assert 'limite=10' in url_llamada

    @patch(_PATCH_TARGET,
           side_effect=requests.exceptions.ConnectionError('sin conexión'))
    def test_historial_retorna_503_cuando_api_cae(self, _mock, cliente):
        """GET /api/historial retorna 503 si el backend no responde."""
        respuesta = cliente.get('/api/historial')

        assert respuesta.status_code == 503


class TestIntegracionHealth:
    """Flujo: GET /health → health_bp → TermostatoService.health_check() → JSON."""

    @patch(_PATCH_TARGET, side_effect=_mock_get_exitoso)
    def test_health_retorna_status_ok(self, _mock, cliente):
        """GET /health retorna status ok del backend."""
        respuesta = cliente.get('/health')

        assert respuesta.status_code == 200
        datos = json.loads(respuesta.data)
        assert datos['status'] == 'ok'

    @patch(_PATCH_TARGET,
           side_effect=requests.exceptions.ConnectionError('sin conexión'))
    def test_health_retorna_503_cuando_backend_cae(self, _mock, cliente):
        """GET /health retorna 503 si el backend no está disponible."""
        respuesta = cliente.get('/health')

        assert respuesta.status_code == 503

    @patch(_PATCH_TARGET,
           side_effect=requests.exceptions.Timeout('timeout'))
    def test_health_retorna_503_en_timeout(self, _mock, cliente):
        """GET /health retorna 503 si el backend no responde a tiempo."""
        respuesta = cliente.get('/health')

        assert respuesta.status_code == 503


class TestIntegracionCacheServiceInteraccion:
    """Tests que validan la interacción real entre TermostatoService y MemoryCache."""

    @patch(_PATCH_TARGET, side_effect=_mock_get_exitoso)
    def test_cache_se_popula_tras_peticion_exitosa(self, _mock, app, cliente):
        """Después de GET /api/estado, el caché del servicio tiene datos."""
        cliente.get('/api/estado')

        cache = app.termostato_service._cache
        assert cache.get('estado') is not None

    def test_cache_vacio_al_inicio(self, app):
        """El caché está vacío al iniciar la aplicación."""
        cache = app.termostato_service._cache
        assert cache.get('estado') is None

    @patch(_PATCH_TARGET, side_effect=_mock_get_exitoso)
    def test_clear_cache_fuerza_nueva_peticion(self, mock_get, app, cliente):
        """Limpiar el caché fuerza una nueva petición al backend."""
        cliente.get('/api/estado')
        app.termostato_service._cache.clear()
        cliente.get('/api/estado')

        assert mock_get.call_count == 2
