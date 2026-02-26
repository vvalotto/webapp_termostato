"""
Tests de integración para US-003: Migración JavaScript a Módulos ES6.

Validan el flujo HTTP completo que sustenta las funcionalidades del dashboard:
  - Dashboard → HTML con entry point ES6 + endpoints de la API que el JS consume
  - Flujos de datos: estado, historial, reconexión, caché
  - Compatibilidad de formato de respuesta con lo que espera el JS migrado

Los tests siguen el patrón del proyecto: MockApiClient inyectado, sin @patch.
"""
import json

import pytest

from webapp import create_app
from webapp.services.api_client import ApiConnectionError, MockApiClient

# ---------------------------------------------------------------------------
# Datos de mock
# ---------------------------------------------------------------------------

ESTADO_NORMAL = {
    'temperatura_ambiente': 22.5,
    'temperatura_deseada': 24.0,
    'estado_climatizador': 'encendido',
    'carga_bateria': 4.1,
    'indicador': 'NORMAL',
}

HISTORIAL_VALIDO = {
    'historial': [
        {'timestamp': '2026-01-01T10:00:00', 'temperatura': 21.0},
        {'timestamp': '2026-01-01T10:01:00', 'temperatura': 21.5},
        {'timestamp': '2026-01-01T10:02:00', 'temperatura': 22.0},
    ],
    'total': 3,
}

HEALTH_BACKEND = {
    'status': 'ok',
    'version': '1.0.0',
    'uptime_seconds': 7200,
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    """App Flask de testing con MockApiClient (datos de estado) y caché limpio."""
    aplicacion = create_app('testing')
    aplicacion.termostato_service._api_client = MockApiClient(ESTADO_NORMAL)
    yield aplicacion
    aplicacion.termostato_service._cache.clear()


@pytest.fixture
def cliente(app):
    """Cliente HTTP de pruebas."""
    return app.test_client()


@pytest.fixture
def app_api_caida():
    """App con backend caído (ApiConnectionError en todas las llamadas)."""
    aplicacion = create_app('testing')
    aplicacion.termostato_service._api_client = MockApiClient(
        {}, raise_error=ApiConnectionError
    )
    yield aplicacion
    aplicacion.termostato_service._cache.clear()


@pytest.fixture
def cliente_api_caida(app_api_caida):
    """Cliente HTTP con backend caído."""
    return app_api_caida.test_client()


# ---------------------------------------------------------------------------
# TestDashboardConModulosES6
# Escenario BDD: "El dashboard se carga y muestra datos actualizados"
# ---------------------------------------------------------------------------

class TestDashboardConModulosES6:
    """Integración: template ES6 + endpoint /api/estado funcionando juntos."""

    def test_dashboard_carga_html_con_entry_point_module(self, cliente):
        """GET / sirve HTML con <script type="module"> apuntando a app.js."""
        resp = cliente.get('/')
        html = resp.data.decode('utf-8')

        assert resp.status_code == 200
        assert 'type="module"' in html
        assert 'js/app.js' in html

    def test_dashboard_incluye_fallback_nomodule(self, cliente):
        """El HTML del dashboard incluye <script nomodule> para navegadores sin soporte."""
        resp = cliente.get('/')
        html = resp.data.decode('utf-8')

        assert 'nomodule' in html

    def test_dashboard_y_api_estado_retornan_datos_coherentes(self, cliente):
        """
        Dashboard sirve HTML (200) y /api/estado retorna los datos
        que el JS mostraría en el DOM.
        """
        resp_dashboard = cliente.get('/')
        resp_api = cliente.get('/api/estado')

        assert resp_dashboard.status_code == 200
        assert resp_api.status_code == 200

        datos = json.loads(resp_api.data)
        assert datos['success'] is True
        assert datos['data']['temperatura_ambiente'] == 22.5
        assert datos['data']['estado_climatizador'] == 'encendido'

    def test_api_estado_envelope_compatible_con_js(self, cliente):
        """
        /api/estado devuelve el envelope {success, data, from_cache, timestamp}
        que app.js espera para procesar la respuesta.
        """
        resp = cliente.get('/api/estado')
        datos = json.loads(resp.data)

        assert resp.status_code == 200
        # El JS chequea resultado.success
        assert 'success' in datos
        # El JS accede a resultado.data para obtener temperatura, etc.
        assert 'data' in datos
        # El JS usa from_cache para decidir el estado de conexión
        assert 'from_cache' in datos
        # El JS usa timestamp para mostrar "Actualizado hace X"
        assert 'timestamp' in datos


# ---------------------------------------------------------------------------
# TestActualizacionAutomatica
# Escenario BDD: "Los datos se actualizan automáticamente cada 10 segundos"
# ---------------------------------------------------------------------------

class TestActualizacionAutomatica:
    """Integración: múltiples llamadas a /api/estado simulan el polling del JS."""

    def test_multiples_llamadas_retornan_datos_frescos(self, cliente):
        """Llamadas sucesivas a /api/estado retornan datos válidos (simula polling)."""
        for _ in range(3):
            resp = cliente.get('/api/estado')
            datos = json.loads(resp.data)
            assert resp.status_code == 200
            assert datos['success'] is True

    def test_api_estado_no_usa_cache_en_llamadas_normales(self, app, cliente):
        """En condiciones normales, from_cache es False (datos frescos)."""
        app.termostato_service._cache.clear()

        resp = cliente.get('/api/estado')
        datos = json.loads(resp.data)

        assert datos['from_cache'] is False


# ---------------------------------------------------------------------------
# TestReintentosCuandoAPIFalla
# Escenario BDD: "Se muestran reintentos cuando la API falla temporalmente"
# ---------------------------------------------------------------------------

class TestFalloDeConexion:
    """Integración: /api/estado responde 503 cuando el backend falla."""

    def test_api_estado_retorna_503_si_backend_caido(self, cliente_api_caida):
        """/api/estado retorna 503 cuando el backend no responde (sin caché)."""
        resp = cliente_api_caida.get('/api/estado')
        assert resp.status_code == 503

    def test_api_estado_retorna_503_con_success_false(self, cliente_api_caida):
        """El envelope de error tiene success=False para que el JS lo detecte."""
        resp = cliente_api_caida.get('/api/estado')
        datos = json.loads(resp.data)

        assert datos['success'] is False

    def test_api_estado_usa_cache_cuando_backend_cae(self, app):
        """
        Si el backend falla pero hay datos en caché, /api/estado
        retorna 200 con from_cache=True (el JS muestra banner pero tiene datos).
        """
        # Primero poblar el caché con datos válidos
        app.termostato_service._api_client = MockApiClient(ESTADO_NORMAL)
        with app.test_client() as c:
            c.get('/api/estado')

        # Ahora simular backend caído
        app.termostato_service._api_client = MockApiClient(
            {}, raise_error=ApiConnectionError
        )
        with app.test_client() as c:
            resp = c.get('/api/estado')
            datos = json.loads(resp.data)

        assert resp.status_code == 200
        assert datos['success'] is True
        assert datos['from_cache'] is True


# ---------------------------------------------------------------------------
# TestGraficasYHistorial
# Escenario BDD: "Las gráficas de temperatura y climatizador se renderizan"
# Escenario BDD: "El selector de rango de tiempo actualiza las gráficas"
# ---------------------------------------------------------------------------

class TestGraficasYHistorial:
    """Integración: /api/historial provee datos para las gráficas del JS."""

    @pytest.fixture
    def app_historial(self):
        """App con MockApiClient que devuelve datos de historial."""
        aplicacion = create_app('testing')
        aplicacion.termostato_service._api_client = MockApiClient(HISTORIAL_VALIDO)
        yield aplicacion
        aplicacion.termostato_service._cache.clear()

    def test_historial_retorna_formato_esperado_por_js(self, app_historial):
        """
        /api/historial devuelve {success, historial, total} que
        historial.js y graficas/temperatura.js esperan.
        """
        with app_historial.test_client() as c:
            resp = c.get('/api/historial')
            datos = json.loads(resp.data)

        assert resp.status_code == 200
        assert datos['success'] is True
        assert 'historial' in datos
        assert isinstance(datos['historial'], list)

    def test_historial_respeta_parametro_limite(self, app_historial):
        """
        GET /api/historial?limite=60 acepta el parámetro que historial.js
        envía cuando el usuario selecciona un rango de tiempo.
        """
        with app_historial.test_client() as c:
            resp = c.get('/api/historial?limite=60')

        assert resp.status_code == 200

    def test_historial_con_backend_caido_retorna_503(self, cliente_api_caida):
        """/api/historial retorna 503 si el backend no responde."""
        resp = cliente_api_caida.get('/api/historial')
        assert resp.status_code == 503


# ---------------------------------------------------------------------------
# TestHealthEndpoint
# Integración: /health funciona con la nueva estructura de módulos
# ---------------------------------------------------------------------------

class TestHealthEndpoint:
    """Integración: /health sirve estado del sistema (backend + frontend)."""

    def test_health_retorna_estado_completo(self, app):
        """GET /health responde con estado de frontend y backend."""
        with app.test_client() as c:
            resp = c.get('/health')
            datos = json.loads(resp.data)

        assert resp.status_code == 200
        assert 'status' in datos
        assert 'frontend' in datos
        assert datos['frontend']['status'] == 'ok'
