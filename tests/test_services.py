"""
Tests unitarios para TermostatoService.
Usa mocks inyectados directamente (sin @patch) para validar la lógica
de negocio de forma aislada de la infraestructura.
"""
import pytest

from webapp.cache.memory_cache import MemoryCache
from webapp.services.api_client import ApiConnectionError, ApiTimeoutError
from webapp.services.termostato_service import TermostatoService

# Datos de ejemplo reutilizados en los tests
DATOS_ESTADO = {
    'temperatura_ambiente': 22,
    'temperatura_deseada': 24,
    'estado_climatizador': 'encendido',
    'carga_bateria': 3.8,
    'indicador': 'NORMAL'
}

DATOS_HISTORIAL = {
    'historial': [
        {'timestamp': '2026-01-01T10:00:00', 'temperatura': 21},
        {'timestamp': '2026-01-01T10:01:00', 'temperatura': 21.5},
    ],
    'total': 2
}

DATOS_HEALTH = {
    'status': 'ok',
    'version': '1.1.0',
    'uptime_seconds': 3600
}


class MockApiClientExitoso:
    """Mock de ApiClient que siempre responde con éxito."""

    def get(self, path, **kwargs):
        if '/termostato/historial/' in path:
            return DATOS_HISTORIAL
        if '/comprueba/' in path:
            return DATOS_HEALTH
        return DATOS_ESTADO


class MockApiClientFallido:
    """Mock de ApiClient que siempre lanza ApiConnectionError."""

    def get(self, path, **kwargs):
        raise ApiConnectionError('Sin conexión')


class MockApiClientTimeout:
    """Mock de ApiClient que siempre lanza ApiTimeoutError."""

    def get(self, path, **kwargs):
        raise ApiTimeoutError('Timeout')


@pytest.fixture
def cache():
    """Fixture de caché limpio para cada test."""
    return MemoryCache()


@pytest.fixture
def servicio_ok(cache):
    """Servicio con API que responde exitosamente."""
    return TermostatoService(api_client=MockApiClientExitoso(), cache=cache)


@pytest.fixture
def servicio_caido(cache):
    """Servicio con API caída y caché vacío."""
    return TermostatoService(api_client=MockApiClientFallido(), cache=cache)


class TestObtenerEstado:
    """Tests de obtener_estado()."""

    def test_retorna_datos_cuando_api_responde(self, servicio_ok):
        """Devuelve datos frescos cuando la API está disponible."""
        datos, timestamp, from_cache = servicio_ok.obtener_estado()

        assert datos is not None
        assert datos['temperatura_ambiente'] == 22
        assert datos['temperatura_deseada'] == 24
        assert timestamp is not None
        assert from_cache is False

    def test_almacena_respuesta_en_cache(self, servicio_ok, cache):
        """Después de una petición exitosa, el estado queda en caché."""
        servicio_ok.obtener_estado()

        assert cache.get('estado') is not None

    def test_retorna_cache_cuando_api_falla(self, cache):
        """Devuelve datos cacheados si la API falla."""
        # Primero una llamada exitosa para poblar el caché
        servicio_ok = TermostatoService(MockApiClientExitoso(), cache)
        servicio_ok.obtener_estado()

        # Ahora la API falla — debe usar el caché
        servicio_caido = TermostatoService(MockApiClientFallido(), cache)
        datos, timestamp, from_cache = servicio_caido.obtener_estado()

        assert datos is not None
        assert datos['temperatura_ambiente'] == 22
        assert from_cache is True

    def test_retorna_none_sin_datos_ni_cache(self, servicio_caido):
        """Retorna (None, None, False) si API falla y no hay caché."""
        datos, timestamp, from_cache = servicio_caido.obtener_estado()

        assert datos is None
        assert timestamp is None
        assert from_cache is False

    def test_from_cache_false_en_respuesta_fresca(self, servicio_ok):
        """from_cache es False cuando los datos son frescos del backend."""
        _, _, from_cache = servicio_ok.obtener_estado()
        assert from_cache is False

    def test_from_cache_true_cuando_api_cae_tras_exito(self, cache):
        """from_cache es True cuando se sirve desde caché."""
        servicio_ok = TermostatoService(MockApiClientExitoso(), cache)
        servicio_ok.obtener_estado()

        servicio_caido = TermostatoService(MockApiClientFallido(), cache)
        _, _, from_cache = servicio_caido.obtener_estado()

        assert from_cache is True

    def test_timeout_usa_cache_si_disponible(self, cache):
        """Un timeout también activa el fallback al caché."""
        TermostatoService(MockApiClientExitoso(), cache).obtener_estado()

        servicio_timeout = TermostatoService(MockApiClientTimeout(), cache)
        datos, _, from_cache = servicio_timeout.obtener_estado()

        assert datos is not None
        assert from_cache is True


class TestObtenerHistorial:
    """Tests de obtener_historial()."""

    def test_retorna_historial_cuando_api_responde(self, servicio_ok):
        """Retorna el historial del backend correctamente."""
        resultado = servicio_ok.obtener_historial()

        assert 'historial' in resultado
        assert resultado['total'] == 2
        assert len(resultado['historial']) == 2

    def test_pasa_limite_al_api_client(self):
        """El parámetro limite se incluye en la URL de la petición."""
        rutas_llamadas = []

        class MockApiCapturaPaths:
            def get(self, path, **kwargs):
                rutas_llamadas.append(path)
                return DATOS_HISTORIAL

        servicio = TermostatoService(MockApiCapturaPaths(), MemoryCache())
        servicio.obtener_historial(limite=100)

        assert any('limite=100' in ruta for ruta in rutas_llamadas)

    def test_lanza_excepcion_cuando_api_falla(self, servicio_caido):
        """Lanza ApiConnectionError si el backend no responde."""
        with pytest.raises(ApiConnectionError):
            servicio_caido.obtener_historial()


class TestHealthCheck:
    """Tests de health_check()."""

    def test_retorna_datos_del_backend(self, servicio_ok):
        """Retorna el estado del backend correctamente."""
        resultado = servicio_ok.health_check()

        assert resultado['status'] == 'ok'
        assert resultado['version'] == '1.1.0'
        assert resultado['uptime_seconds'] == 3600

    def test_lanza_excepcion_cuando_backend_no_responde(self, servicio_caido):
        """Lanza ApiConnectionError si el backend no está disponible."""
        with pytest.raises(ApiConnectionError):
            servicio_caido.health_check()

    def test_lanza_excepcion_en_timeout(self, cache):
        """Lanza ApiTimeoutError si el backend no responde a tiempo."""
        servicio = TermostatoService(MockApiClientTimeout(), cache)

        with pytest.raises(ApiTimeoutError):
            servicio.health_check()
