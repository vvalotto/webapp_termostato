"""
Tests de rutas para webapp_termostato.
WT-26: Tests unitarios básicos

US-002: Eliminado @patch — los tests usan MockApiClient inyectado
via create_app('testing') o directamente sobre el servicio.

pylint: disable=redefined-outer-name
"""
import pytest

from webapp import create_app
from webapp.services.api_client import ApiConnectionError, ApiTimeoutError, MockApiClient

# ---------------------------------------------------------------------------
# Datos de mock por escenario
# ---------------------------------------------------------------------------

DATOS_ESTADO_VALIDOS = {
    'temperatura_ambiente': 22,
    'temperatura_deseada': 24,
    'estado_climatizador': 'encendido',
    'carga_bateria': 3.8,
    'indicador': 'NORMAL',
}

DATOS_HISTORIAL_VALIDOS = {
    'historial': [
        {'timestamp': '2025-12-26T10:30:00', 'temperatura': 22},
        {'timestamp': '2025-12-26T10:31:00', 'temperatura': 22.5},
    ],
    'total': 2,
}

DATOS_HEALTH_BACKEND = {
    'status': 'ok',
    'timestamp': '2025-12-26T10:30:00',
    'uptime_seconds': 3600,
    'version': '1.1.0',
}

# ---------------------------------------------------------------------------
# Fixtures base
# ---------------------------------------------------------------------------


@pytest.fixture
def app():
    """App Flask para testing — inyecta MockApiClient con datos de estado."""
    return create_app('testing')


@pytest.fixture
def client(app):
    """Cliente HTTP de pruebas."""
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def reset_cache(app):
    """Limpiar caché entre tests."""
    app.termostato_service._cache.clear()
    yield
    app.termostato_service._cache.clear()


# ---------------------------------------------------------------------------
# TestRutaIndex
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures('reset_cache')
class TestRutaIndex:
    """Tests para la ruta principal /"""

    def test_index_con_api_funcionando(self, client):
        """Dashboard renderiza correctamente con MockApiClient inyectado."""
        response = client.get('/')

        assert response.status_code == 200
        assert b'Dashboard Termostato' in response.data
        assert b'22' in response.data    # temperatura_ambiente
        assert b'24' in response.data    # temperatura_deseada
        assert b'ENCENDIDO' in response.data  # estado_climatizador

    def test_index_con_api_caida(self, app, client):
        """Dashboard muestra error cuando la API lanza ApiConnectionError."""
        app.termostato_service._api_client = MockApiClient(
            {}, raise_error=ApiConnectionError
        )

        response = client.get('/')

        assert response.status_code == 200
        assert b'Dashboard Termostato' in response.data
        assert b'Error API' in response.data

    def test_index_con_api_timeout(self, app, client):
        """Dashboard muestra error cuando la API lanza ApiTimeoutError."""
        app.termostato_service._api_client = MockApiClient(
            {}, raise_error=ApiTimeoutError
        )

        response = client.get('/')

        assert response.status_code == 200
        assert b'Error API' in response.data

    def test_index_usa_cache_cuando_api_cae(self, app, client):
        """Dashboard muestra datos cacheados cuando la API falla."""
        # Primera petición: API ok → datos al caché
        response1 = client.get('/')
        assert response1.status_code == 200
        assert b'22' in response1.data

        # Swap: API ahora falla
        app.termostato_service._api_client = MockApiClient(
            {}, raise_error=ApiConnectionError
        )

        # Segunda petición: debe usar caché
        response2 = client.get('/')
        assert response2.status_code == 200
        assert b'22' in response2.data  # datos del caché


# ---------------------------------------------------------------------------
# TestApiEstado
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures('reset_cache')
class TestApiEstado:
    """Tests para el endpoint /api/estado"""

    def test_api_estado_funcionando(self, client):
        """Endpoint retorna success=True con MockApiClient inyectado."""
        response = client.get('/api/estado')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['temperatura_ambiente'] == 22
        assert data['from_cache'] is False

    def test_api_estado_con_api_caida(self, app, client):
        """Endpoint retorna 503 cuando API falla y caché está vacío."""
        app.termostato_service._api_client = MockApiClient(
            {}, raise_error=ApiConnectionError
        )

        response = client.get('/api/estado')

        assert response.status_code == 503
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data

    def test_api_estado_usa_cache(self, app, client):
        """Endpoint retorna datos cacheados con from_cache=True cuando API falla."""
        # Primera petición exitosa → carga el caché
        client.get('/api/estado')

        # Swap: API falla
        app.termostato_service._api_client = MockApiClient(
            {}, raise_error=ApiConnectionError
        )

        response = client.get('/api/estado')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['from_cache'] is True


# ---------------------------------------------------------------------------
# TestApiHistorial
# ---------------------------------------------------------------------------


class TestApiHistorial:
    """Tests para el endpoint /api/historial"""

    @pytest.fixture
    def app_historial(self):
        """App con MockApiClient configurado para devolver historial."""
        app = create_app('testing')
        app.termostato_service._api_client = MockApiClient(DATOS_HISTORIAL_VALIDOS)
        return app

    @pytest.fixture
    def client_historial(self, app_historial):
        """Cliente para tests de historial."""
        with app_historial.test_client() as test_client:
            yield test_client

    def test_api_historial_funcionando(self, client_historial):
        """Endpoint retorna historial con datos válidos."""
        response = client_historial.get('/api/historial')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['historial']) == 2
        assert data['total'] == 2

    def test_api_historial_con_limite(self, app_historial, client_historial):
        """El path consultado al backend incluye el parámetro límite."""
        client_historial.get('/api/historial?limite=100')

        assert 'limite=100' in app_historial.termostato_service._api_client.last_path

    def test_api_historial_con_api_caida(self, app_historial, client_historial):
        """Endpoint retorna 503 cuando API lanza ApiConnectionError."""
        app_historial.termostato_service._api_client = MockApiClient(
            {}, raise_error=ApiConnectionError
        )

        response = client_historial.get('/api/historial')

        assert response.status_code == 503
        data = response.get_json()
        assert data['success'] is False
        assert data['historial'] == []


# ---------------------------------------------------------------------------
# TestHealth
# ---------------------------------------------------------------------------


class TestHealth:
    """Tests para el endpoint /health (WT-27)"""

    @pytest.fixture
    def app_health(self):
        """App con MockApiClient configurado para devolver datos de health."""
        app = create_app('testing')
        app.termostato_service._api_client = MockApiClient(DATOS_HEALTH_BACKEND)
        return app

    @pytest.fixture
    def client_health(self, app_health):
        """Cliente para tests de health."""
        with app_health.test_client() as test_client:
            yield test_client

    def test_health_con_backend_ok(self, client_health):
        """Health retorna ok cuando backend responde correctamente."""
        response = client_health.get('/health')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert 'timestamp' in data
        assert data['frontend']['status'] == 'ok'
        assert data['frontend']['version'] == '2.0.0'
        assert data['backend']['status'] == 'ok'
        assert data['backend']['version'] == '1.1.0'
        assert data['backend']['uptime_seconds'] == 3600

    def test_health_con_backend_caido(self, app_health, client_health):
        """Health retorna 503 cuando backend lanza ApiConnectionError."""
        app_health.termostato_service._api_client = MockApiClient(
            {}, raise_error=ApiConnectionError
        )

        response = client_health.get('/health')

        assert response.status_code == 503
        data = response.get_json()
        assert data['status'] == 'degraded'
        assert data['frontend']['status'] == 'ok'
        assert data['backend']['status'] == 'unavailable'
        assert 'error' in data['backend']

    def test_health_con_backend_timeout(self, app_health, client_health):
        """Health retorna 503 cuando backend lanza ApiTimeoutError."""
        app_health.termostato_service._api_client = MockApiClient(
            {}, raise_error=ApiTimeoutError
        )

        response = client_health.get('/health')

        assert response.status_code == 503
        data = response.get_json()
        assert data['status'] == 'degraded'
        assert data['backend']['status'] == 'unavailable'
