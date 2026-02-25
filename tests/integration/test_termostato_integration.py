"""
Tests de integración para webapp_termostato.
Validan el flujo HTTP completo: TestClient → Blueprint → TermostatoService → MemoryCache.

US-002: Reemplazados @patch por inyección directa de MockApiClient.
El servicio inyectado en create_app('testing') es MockApiClient por defecto.
Para escenarios de error se swapea el api_client directamente.
"""
import json

import pytest

from webapp import create_app
from webapp.services.api_client import ApiConnectionError, ApiTimeoutError, MockApiClient

# ---------------------------------------------------------------------------
# Datos de mock para distintos escenarios
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


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    """Aplicación Flask de testing con MockApiClient (datos de estado) y caché limpio."""
    aplicacion = create_app('testing')
    # Inyectar mock con datos de estado (comportamiento por defecto de testing)
    aplicacion.termostato_service._api_client = MockApiClient(RESPUESTA_ESTADO)
    yield aplicacion
    aplicacion.termostato_service._cache.clear()


@pytest.fixture
def cliente(app):
    """Cliente HTTP de testing."""
    return app.test_client()


@pytest.fixture
def app_historial():
    """App con MockApiClient configurado para retornar datos de historial."""
    aplicacion = create_app('testing')
    aplicacion.termostato_service._api_client = MockApiClient(RESPUESTA_HISTORIAL)
    yield aplicacion
    aplicacion.termostato_service._cache.clear()


@pytest.fixture
def app_health():
    """App con MockApiClient configurado para retornar datos de health."""
    aplicacion = create_app('testing')
    aplicacion.termostato_service._api_client = MockApiClient(RESPUESTA_HEALTH)
    yield aplicacion
    aplicacion.termostato_service._cache.clear()


# ---------------------------------------------------------------------------
# Tests de integración: flujo completo HTTP
# ---------------------------------------------------------------------------

class TestIntegracionRutaPrincipal:
    """Flujo: GET / → main_bp → TermostatoService → render template."""

    def test_index_renderiza_con_datos_reales(self, cliente):
        """La ruta principal renderiza datos del servicio real."""
        respuesta = cliente.get('/')
        assert respuesta.status_code == 200

    def test_index_responde_200_aunque_api_caiga(self, app, cliente):
        """La ruta / responde 200 aunque la API esté caída (muestra estado de error)."""
        app.termostato_service._api_client = MockApiClient(
            {}, raise_error=ApiConnectionError
        )
        respuesta = cliente.get('/')
        assert respuesta.status_code == 200

    def test_index_llama_api_en_cada_peticion(self, app, cliente):
        """Cada petición a / llama al backend (caché es solo fallback ante fallos)."""
        cliente.get('/')
        cliente.get('/')

        assert app.termostato_service._api_client.call_count == 2


class TestIntegracionApiEstado:
    """Flujo: GET /api/estado → api_bp → TermostatoService → JSON."""

    def test_api_estado_retorna_json_valido(self, cliente):
        """GET /api/estado retorna JSON con todos los campos del termostato."""
        respuesta = cliente.get('/api/estado')

        assert respuesta.status_code == 200
        envelope = json.loads(respuesta.data)
        assert envelope['success'] is True
        datos = envelope['data']
        assert datos['temperatura_ambiente'] == 21.5
        assert datos['indicador'] == 'NORMAL'

    def test_api_estado_from_cache_es_false_en_respuesta_fresca(self, cliente):
        """Datos frescos: from_cache debe ser False."""
        respuesta = cliente.get('/api/estado')
        datos = json.loads(respuesta.data)
        assert datos.get('from_cache') is False

    def test_api_estado_retorna_503_sin_cache(self, app, cliente):
        """Si la API falla y no hay caché, /api/estado retorna 503."""
        app.termostato_service._api_client = MockApiClient(
            {}, raise_error=ApiConnectionError
        )
        respuesta = cliente.get('/api/estado')
        assert respuesta.status_code == 503

    def test_api_estado_sirve_cache_cuando_api_cae(self, app, cliente):
        """Si la API falla pero hay caché, retorna datos con from_cache=True."""
        # Primera petición: poblar caché
        cliente.get('/api/estado')

        # Swap: API caída
        app.termostato_service._api_client = MockApiClient(
            {}, raise_error=ApiConnectionError
        )
        respuesta = cliente.get('/api/estado')

        assert respuesta.status_code == 200
        datos = json.loads(respuesta.data)
        assert datos.get('from_cache') is True


class TestIntegracionApiHistorial:
    """Flujo: GET /api/historial → api_bp → TermostatoService → JSON."""

    def test_historial_retorna_lista(self, app_historial):
        """GET /api/historial retorna JSON con campo historial."""
        with app_historial.test_client() as c:
            respuesta = c.get('/api/historial')

        assert respuesta.status_code == 200
        datos = json.loads(respuesta.data)
        assert 'historial' in datos
        assert len(datos['historial']) == 2

    def test_historial_acepta_parametro_limite(self, app_historial):
        """GET /api/historial?limite=10 pasa el parámetro al backend."""
        with app_historial.test_client() as c:
            c.get('/api/historial?limite=10')

        assert 'limite=10' in app_historial.termostato_service._api_client.last_path

    def test_historial_retorna_503_cuando_api_cae(self, app_historial):
        """GET /api/historial retorna 503 si el backend no responde."""
        app_historial.termostato_service._api_client = MockApiClient(
            {}, raise_error=ApiConnectionError
        )
        with app_historial.test_client() as c:
            respuesta = c.get('/api/historial')

        assert respuesta.status_code == 503


class TestIntegracionHealth:
    """Flujo: GET /health → health_bp → TermostatoService.health_check() → JSON."""

    def test_health_retorna_status_ok(self, app_health):
        """GET /health retorna status ok del backend."""
        with app_health.test_client() as c:
            respuesta = c.get('/health')

        assert respuesta.status_code == 200
        datos = json.loads(respuesta.data)
        assert datos['status'] == 'ok'

    def test_health_retorna_503_cuando_backend_cae(self, app_health):
        """GET /health retorna 503 si el backend no está disponible."""
        app_health.termostato_service._api_client = MockApiClient(
            {}, raise_error=ApiConnectionError
        )
        with app_health.test_client() as c:
            respuesta = c.get('/health')

        assert respuesta.status_code == 503

    def test_health_retorna_503_en_timeout(self, app_health):
        """GET /health retorna 503 si el backend no responde a tiempo."""
        app_health.termostato_service._api_client = MockApiClient(
            {}, raise_error=ApiTimeoutError
        )
        with app_health.test_client() as c:
            respuesta = c.get('/health')

        assert respuesta.status_code == 503


class TestIntegracionCacheServiceInteraccion:
    """Tests que validan la interacción real entre TermostatoService y MemoryCache."""

    def test_cache_se_popula_tras_peticion_exitosa(self, app, cliente):
        """Después de GET /api/estado, el caché del servicio tiene datos."""
        cliente.get('/api/estado')

        cache = app.termostato_service._cache
        assert cache.get('estado') is not None

    def test_cache_vacio_al_inicio(self, app):
        """El caché está vacío al iniciar la aplicación."""
        cache = app.termostato_service._cache
        assert cache.get('estado') is None

    def test_clear_cache_fuerza_nueva_peticion(self, app, cliente):
        """Limpiar el caché fuerza una nueva petición al backend."""
        cliente.get('/api/estado')
        app.termostato_service._cache.clear()
        cliente.get('/api/estado')

        assert app.termostato_service._api_client.call_count == 2
