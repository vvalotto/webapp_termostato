"""
Step definitions BDD para US-001: Refactorizar Backend en Arquitectura por Capas.
Valida el comportamiento del sistema desde la perspectiva del usuario y del desarrollador.
"""
import json

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

from webapp import create_app
from webapp.cache.memory_cache import MemoryCache
from webapp.services.api_client import ApiConnectionError, MockApiClient
from webapp.services.termostato_service import TermostatoService

# ---------------------------------------------------------------------------
# Cargar escenarios del feature file
# ---------------------------------------------------------------------------
scenarios('../features/US-001-refactor-backend-capas.feature')

# ---------------------------------------------------------------------------
# Datos de prueba compartidos
# ---------------------------------------------------------------------------
DATOS_ESTADO = {
    'temperatura_ambiente': 22.5,
    'temperatura_deseada': 24.0,
    'estado_climatizador': 'encendido',
    'carga_bateria': 3.9,
    'indicador': 'NORMAL',
}

DATOS_HISTORIAL = {
    'historial': [
        {'timestamp': '2026-01-01T10:00:00', 'temperatura': 21.0},
    ],
    'total': 1,
}

DATOS_HEALTH = {
    'status': 'ok',
    'version': '1.1.0',
    'uptime_seconds': 3600,
}


# ---------------------------------------------------------------------------
# Helper: inyectar MockApiClient en el servicio del contexto
# ---------------------------------------------------------------------------

def _inyectar_mock(ctx, mock_data, raise_error=None):
    """Reemplaza el api_client del servicio con un MockApiClient."""
    ctx['app'].termostato_service._api_client = MockApiClient(
        mock_data, raise_error=raise_error
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def ctx():
    """Contexto mutable compartido entre todos los steps de un escenario."""
    return {
        'app': None,
        'client': None,
        'response': None,
        'mock_api_client': None,
        'mock_cache': None,
        'servicio': None,
        'blueprints': [],
    }


@pytest.fixture(autouse=True)
def limpiar_cache(ctx):
    """Limpia el caché del servicio al finalizar cada test."""
    yield
    if ctx.get('app'):
        ctx['app'].termostato_service._cache.clear()


# ---------------------------------------------------------------------------
# Background steps
# ---------------------------------------------------------------------------

@given("la aplicación web está iniciada con la nueva arquitectura por capas")
def app_iniciada(ctx):
    """La aplicación se crea con create_app (Application Factory)."""
    ctx['app'] = create_app('testing')
    ctx['client'] = ctx['app'].test_client()


@given("el servicio de termostato está disponible")
def servicio_disponible(ctx):
    """El servicio está accesible a través del app context."""
    assert hasattr(ctx['app'], 'termostato_service')
    assert ctx['app'].termostato_service is not None


# ---------------------------------------------------------------------------
# Given: estados del backend
# ---------------------------------------------------------------------------

@given("la API backend responde con datos válidos del termostato")
def api_responde_datos_validos(ctx):
    """Mock que devuelve DATOS_ESTADO para /termostato/."""
    _inyectar_mock(ctx, DATOS_ESTADO)


@given("la API backend responde con historial de temperaturas")
def api_responde_historial(ctx):
    """Mock que devuelve DATOS_HISTORIAL para /termostato/historial/."""
    _inyectar_mock(ctx, DATOS_HISTORIAL)


@given("la API backend está disponible y responde al health check")
def api_responde_health(ctx):
    """Mock que devuelve DATOS_HEALTH para /comprueba/."""
    _inyectar_mock(ctx, DATOS_HEALTH)


@given("la API backend respondió exitosamente en la última petición")
def api_respondio_exitosamente(ctx):
    """Hace una petición exitosa para poblar el caché."""
    _inyectar_mock(ctx, DATOS_ESTADO)
    ctx['client'].get('/api/estado')  # Pobla el caché


@given("la API backend ya no está disponible")
def api_ya_no_disponible(ctx):
    """Configura el mock para fallar con ConnectionError."""
    _inyectar_mock(ctx, {}, raise_error=ApiConnectionError)


@given("la API backend no está disponible y no hay datos en caché")
def api_no_disponible_sin_cache(ctx):
    """La API falla y el caché está explícitamente vacío."""
    ctx['app'].termostato_service._cache.clear()
    _inyectar_mock(ctx, {}, raise_error=ApiConnectionError)


@given("existe una implementación mock del cliente API")
def mock_api_client_existe(ctx):
    """Crea un ApiClient stub que registra las rutas llamadas."""
    class MockApiClientDIP:
        """Mock que captura llamadas sin hacer HTTP real."""
        def __init__(self):
            self.rutas_llamadas = []

        def get(self, path, **kwargs):
            self.rutas_llamadas.append(path)
            return DATOS_ESTADO

    ctx['mock_api_client'] = MockApiClientDIP()


@given("existe una implementación en memoria del caché")
def cache_en_memoria_existe(ctx):
    """Instancia real de MemoryCache inyectable."""
    ctx['mock_cache'] = MemoryCache()


@given('la aplicación está creada con la factory "create_app"')
def app_con_factory(ctx):
    """Verifica que la app fue creada mediante Application Factory."""
    assert ctx['app'] is not None


# ---------------------------------------------------------------------------
# When steps
# ---------------------------------------------------------------------------

@when('el usuario accede a la ruta principal "/"')
def acceder_index(ctx):
    """GET /"""
    ctx['response'] = ctx['client'].get('/')


@when(parsers.parse('se hace una petición GET a "{ruta}"'))
def hacer_get(ctx, ruta):
    """GET a la ruta especificada."""
    ctx['response'] = ctx['client'].get(ruta)


@when("se inyecta el mock en el servicio de termostato")
def inyectar_mock_api_client(ctx):
    """Instancia TermostatoService con el mock de ApiClient."""
    ctx['servicio'] = TermostatoService(
        api_client=ctx['mock_api_client'],
        cache=MemoryCache()
    )


@when("se inyecta el caché en el servicio de termostato")
def inyectar_mock_cache(ctx):
    """Instancia TermostatoService con el MemoryCache inyectado."""
    class ApiClientSimple:
        """Cliente API minimal para tests de caché."""
        def get(self, path, **kwargs):
            return DATOS_ESTADO

    ctx['servicio'] = TermostatoService(
        api_client=ApiClientSimple(),
        cache=ctx['mock_cache']
    )


@when("se inspeccionan los blueprints registrados")
def inspeccionar_blueprints(ctx):
    """Obtiene la lista de nombres de blueprints del app Flask."""
    ctx['blueprints'] = list(ctx['app'].blueprints.keys())


# ---------------------------------------------------------------------------
# Then steps
# ---------------------------------------------------------------------------

@then(parsers.parse("la respuesta tiene código HTTP {codigo:d}"))
def verificar_codigo_http(ctx, codigo):
    """Valida el código de estado HTTP."""
    assert ctx['response'].status_code == codigo


@then("el dashboard muestra la temperatura ambiente")
def dashboard_muestra_temp_ambiente(ctx):
    """La página renderizada contiene el valor de temperatura ambiente."""
    contenido = ctx['response'].data.decode('utf-8')
    assert '22' in contenido


@then("el dashboard muestra la temperatura deseada")
def dashboard_muestra_temp_deseada(ctx):
    """La página renderizada contiene el valor de temperatura deseada."""
    contenido = ctx['response'].data.decode('utf-8')
    assert '24' in contenido


@then("el dashboard muestra el estado del climatizador")
def dashboard_muestra_estado_climatizador(ctx):
    """La página renderizada contiene el estado del climatizador."""
    contenido = ctx['response'].data.decode('utf-8')
    assert 'encendido' in contenido.lower()


@then('la respuesta JSON contiene "success" igual a true')
def json_success_true(ctx):
    """El JSON de respuesta tiene success=true."""
    datos = json.loads(ctx['response'].data)
    assert datos.get('success') is True


@then('la respuesta JSON contiene "success" igual a false')
def json_success_false(ctx):
    """El JSON de respuesta tiene success=false."""
    datos = json.loads(ctx['response'].data)
    assert datos.get('success') is False


@then("la respuesta JSON contiene los datos del termostato")
def json_contiene_datos_termostato(ctx):
    """El JSON tiene clave 'data' con los campos del termostato."""
    datos = json.loads(ctx['response'].data)
    assert 'data' in datos
    assert 'temperatura_ambiente' in datos['data']


@then('el campo "from_cache" es false')
def from_cache_es_false(ctx):
    """El campo from_cache debe ser False para datos frescos."""
    datos = json.loads(ctx['response'].data)
    assert datos.get('from_cache') is False


@then('la respuesta JSON contiene la lista "historial"')
def json_contiene_historial(ctx):
    """El JSON tiene clave 'historial' con una lista."""
    datos = json.loads(ctx['response'].data)
    assert 'historial' in datos
    assert isinstance(datos['historial'], list)


@then('la petición al backend incluye el parámetro "limite=10"')
def peticion_incluye_limite(ctx):
    """Verifica que la URL llamada al backend incluye el parámetro limite."""
    last_path = ctx['app'].termostato_service._api_client.last_path
    assert last_path is not None and 'limite=10' in last_path


@then('la respuesta JSON contiene "status" igual a "ok"')
def json_status_ok(ctx):
    """El JSON tiene status='ok'."""
    datos = json.loads(ctx['response'].data)
    assert datos.get('status') == 'ok'


@then("la respuesta incluye información del frontend y del backend")
def json_incluye_frontend_backend(ctx):
    """El health check JSON incluye secciones frontend y backend."""
    datos = json.loads(ctx['response'].data)
    assert 'frontend' in datos
    assert 'backend' in datos


@then("el dashboard muestra los últimos datos cacheados")
def dashboard_muestra_datos_cacheados(ctx):
    """Con API caída y caché poblado, el dashboard NO muestra 'Error API'."""
    assert ctx['response'].status_code == 200
    contenido = ctx['response'].data.decode('utf-8')
    assert 'Error API' not in contenido


@then('el dashboard muestra "Error API" en los campos de temperatura')
def dashboard_muestra_error_api(ctx):
    """Sin API ni caché, el dashboard muestra 'Error API'."""
    contenido = ctx['response'].data.decode('utf-8')
    assert 'Error API' in contenido


@then("el servicio obtiene datos usando el cliente inyectado")
def servicio_usa_cliente_inyectado(ctx):
    """El servicio obtiene datos reales mediante el cliente mock inyectado."""
    datos, _, _ = ctx['servicio'].obtener_estado()
    assert datos is not None
    assert datos['temperatura_ambiente'] == DATOS_ESTADO['temperatura_ambiente']


@then("no se realizan peticiones HTTP reales")
def sin_peticiones_http_reales(ctx):
    """El mock capturó las llamadas — no hubo HTTP real."""
    assert len(ctx['mock_api_client'].rutas_llamadas) > 0


@then("el servicio almacena y recupera datos usando el caché inyectado")
def servicio_usa_cache_inyectado(ctx):
    """Tras obtener_estado(), el caché inyectado tiene los datos."""
    ctx['servicio'].obtener_estado()
    assert ctx['mock_cache'].get('estado') is not None


@then("el caché puede ser reemplazado sin modificar el servicio")
def cache_reemplazable(ctx):
    """El servicio funciona con cualquier implementación de Cache."""
    nuevo_cache = MemoryCache()
    servicio_nuevo = TermostatoService(
        api_client=ctx['servicio']._api_client,
        cache=nuevo_cache
    )
    datos, _, _ = servicio_nuevo.obtener_estado()
    assert datos is not None


@then("existe un blueprint para las rutas de interfaz de usuario")
def blueprint_ui_existe(ctx):
    """Existe el blueprint 'main' para las rutas de la interfaz web."""
    assert 'main' in ctx['blueprints']


@then("existe un blueprint para las rutas de API JSON")
def blueprint_api_existe(ctx):
    """Existe el blueprint 'api' para los endpoints JSON."""
    assert 'api' in ctx['blueprints']
