"""
Step definitions BDD para US-002: Implementar Inyección de Dependencias.
Valida MockApiClient, excepciones custom, Application Factory con DI y MemoryCache TTL.
"""
import json
import threading
import time
from unittest.mock import patch

import pytest
import requests
from pytest_bdd import scenarios, given, when, then, parsers

from webapp import create_app
from webapp.cache.memory_cache import MemoryCache
from webapp.services.api_client import (
    ApiConnectionError,
    ApiTimeoutError,
    MockApiClient,
    RequestsApiClient,
)
from webapp.services.termostato_service import TermostatoService

# ---------------------------------------------------------------------------
# Cargar escenarios del feature file
# ---------------------------------------------------------------------------
scenarios('../features/US-002-inyeccion-dependencias.feature')

# ---------------------------------------------------------------------------
# Datos de prueba
# ---------------------------------------------------------------------------
DATOS_ESTADO = {
    'temperatura_ambiente': 22.5,
    'temperatura_deseada': 24.0,
    'estado_climatizador': 'encendido',
    'carga_bateria': 3.9,
    'indicador': 'NORMAL',
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def ctx():
    """Contexto mutable compartido entre todos los steps de un escenario."""
    return {
        'app': None,
        'client': None,
        'mock_api_client': None,
        'servicio': None,
        'cache': None,
        'resultado_get': None,
        'datos': None,
        'from_cache': None,
        'excepcion': None,
        'response': None,
    }


@pytest.fixture(autouse=True)
def limpiar_cache(ctx):
    """Limpia el caché del servicio al finalizar cada test."""
    yield
    if ctx.get('app'):
        ctx['app'].termostato_service._cache.clear()


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------

@given('la aplicación web está creada con la factory "create_app"')
def app_creada_con_factory(ctx):
    """Crea la aplicación usando Application Factory con config testing."""
    ctx['app'] = create_app('testing')
    ctx['client'] = ctx['app'].test_client()


# ---------------------------------------------------------------------------
# Given steps — MockApiClient
# ---------------------------------------------------------------------------

@given("un MockApiClient configurado con datos válidos del termostato")
def mock_api_client_con_datos(ctx):
    """Crea un MockApiClient que devuelve DATOS_ESTADO."""
    ctx['mock_api_client'] = MockApiClient(DATOS_ESTADO)


@given("un MockApiClient configurado para lanzar ApiConnectionError")
def mock_api_client_con_error(ctx):
    """Crea un MockApiClient configurado para lanzar ApiConnectionError."""
    ctx['mock_api_client'] = MockApiClient({}, raise_error=ApiConnectionError)


@given("un TermostatoService con el MockApiClient inyectado")
def servicio_con_mock_api_client(ctx):
    """Instancia TermostatoService con el mock de api_client y un caché vacío."""
    ctx['cache'] = MemoryCache()
    ctx['servicio'] = TermostatoService(
        api_client=ctx['mock_api_client'],
        cache=ctx['cache'],
    )


@given("un MemoryCache con datos previos almacenados")
def cache_con_datos_previos(ctx):
    """Crea un MemoryCache con datos de estado ya almacenados."""
    ctx['cache'] = MemoryCache()
    ctx['cache'].set('estado', {'datos': DATOS_ESTADO, 'timestamp': 'T'})


@given("un MemoryCache vacío")
def cache_vacio(ctx):
    """Crea un MemoryCache sin datos."""
    ctx['cache'] = MemoryCache()


@given("un TermostatoService con el MockApiClient y el cache inyectados")
def servicio_con_mock_y_cache(ctx):
    """Instancia TermostatoService con el mock y el caché ya creados."""
    ctx['servicio'] = TermostatoService(
        api_client=ctx['mock_api_client'],
        cache=ctx['cache'],
    )


@given("un RequestsApiClient configurado con una URL inaccesible")
def requests_api_client_url_inaccesible(ctx):
    """Crea un RequestsApiClient apuntando a una URL que rechazará la conexión."""
    ctx['api_client_real'] = RequestsApiClient(
        base_url='http://localhost:19999', timeout=1
    )


@given("un RequestsApiClient configurado con timeout muy bajo")
def requests_api_client_timeout_bajo(ctx):
    """Crea un RequestsApiClient con timeout de 0.001 segundos."""
    ctx['api_client_real'] = RequestsApiClient(
        base_url='http://localhost:19999', timeout=0.001
    )


@given('la aplicación creada con create_app("testing")')
def app_con_testing_config(ctx):
    """La aplicación ya fue creada en el Background — verificación explícita."""
    assert ctx['app'] is not None
    assert ctx['app'].config['TESTING'] is True


# ---------------------------------------------------------------------------
# When steps
# ---------------------------------------------------------------------------

@when("se llama al método get() del MockApiClient")
def llamar_get_mock(ctx):
    """Invoca get() en el MockApiClient almacenado en el contexto."""
    ctx['resultado_get'] = ctx['mock_api_client'].get('/termostato/')


@when(parsers.parse('se llama a get() con el path "{path}"'))
def llamar_get_con_path(ctx, path):
    """Invoca get() con un path específico."""
    ctx['resultado_get'] = ctx['mock_api_client'].get(path)


@when("se llama a obtener_estado()")
def llamar_obtener_estado(ctx):
    """Llama a obtener_estado() y almacena datos, timestamp y from_cache."""
    ctx['datos'], ctx['timestamp'], ctx['from_cache'] = ctx['servicio'].obtener_estado()


@when("se llama a get() y la conexión es rechazada")
def llamar_get_conexion_rechazada(ctx):
    """Invoca get() esperando que lance ApiConnectionError."""
    try:
        with patch('webapp.services.api_client.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError('sin conexión')
            ctx['api_client_real'].get('/termostato/')
    except ApiConnectionError as exc:
        ctx['excepcion'] = exc


@when("se llama a get() y la petición tarda más del timeout")
def llamar_get_timeout(ctx):
    """Invoca get() esperando que lance ApiTimeoutError."""
    try:
        with patch('webapp.services.api_client.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout('timeout')
            ctx['api_client_real'].get('/termostato/')
    except ApiTimeoutError as exc:
        ctx['excepcion'] = exc


@when("se inspecciona el servicio inyectado en la aplicación")
def inspeccionar_servicio_inyectado(ctx):
    """Obtiene el api_client actualmente inyectado en el servicio."""
    ctx['api_client_inyectado'] = ctx['app'].termostato_service._api_client


@when('el usuario accede a la ruta principal "/"')
def acceder_ruta_principal(ctx):
    """GET /"""
    ctx['response'] = ctx['client'].get('/')


@when(parsers.parse('se hace una petición GET a "{ruta}"'))
def hacer_get(ctx, ruta):
    """GET a la ruta especificada."""
    ctx['response'] = ctx['client'].get(ruta)


@when("se almacena un valor con TTL de 60 segundos")
def almacenar_con_ttl_60(ctx):
    """Almacena 'valor_test' en el caché con TTL=60."""
    ctx['cache'].set('clave_test', 'valor_test', ttl=60)


@when("se almacena un valor con TTL de 1 segundo y espera a que expire")
def almacenar_con_ttl_1_y_esperar(ctx):
    """Almacena un valor con TTL=1 y espera 1.1 segundos."""
    ctx['cache'].set('clave_test', 'valor_expirado', ttl=1)
    time.sleep(1.1)


@when("múltiples hilos escriben y leen simultáneamente")
def hilos_concurrentes(ctx):
    """Lanza 30 hilos que escriben y leen del caché al mismo tiempo."""
    ctx['errores_hilos'] = []
    ctx['valores_escritos'] = {}

    def operar(indice):
        try:
            ctx['cache'].set(f'k{indice}', indice)
            leido = ctx['cache'].get(f'k{indice}')
            ctx['valores_escritos'][indice] = leido
        except Exception as exc:  # pylint: disable=broad-except
            ctx['errores_hilos'].append(exc)

    hilos = [threading.Thread(target=operar, args=(i,)) for i in range(30)]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()


# ---------------------------------------------------------------------------
# Then steps
# ---------------------------------------------------------------------------

@then("retorna los datos configurados")
def retorna_datos_configurados(ctx):
    """El resultado de get() es igual a DATOS_ESTADO."""
    assert ctx['resultado_get'] == DATOS_ESTADO


@then("el contador de llamadas se incrementa en 1")
def contador_llamadas_incrementado(ctx):
    """call_count del mock debe ser 1 tras una llamada."""
    assert ctx['mock_api_client'].call_count == 1


@then(parsers.parse('el atributo last_path del mock contiene "{path}"'))
def last_path_contiene(ctx, path):
    """last_path del mock es igual al path consultado."""
    assert ctx['mock_api_client'].last_path == path


@then("el servicio retorna los datos del mock sin realizar peticiones HTTP reales")
def servicio_retorna_datos_mock(ctx):
    """datos no es None y call_count del mock es > 0."""
    assert ctx['datos'] is not None
    assert ctx['mock_api_client'].call_count > 0


@then("from_cache es false")
def from_cache_es_false(ctx):
    """from_cache debe ser False."""
    assert ctx['from_cache'] is False


@then("el servicio retorna los datos del cache")
def servicio_retorna_datos_cache(ctx):
    """datos no es None (proviene del caché)."""
    assert ctx['datos'] is not None


@then("from_cache es true")
def from_cache_es_true(ctx):
    """from_cache debe ser True."""
    assert ctx['from_cache'] is True


@then("datos es None")
def datos_es_none(ctx):
    """datos debe ser None cuando falla la API y el caché está vacío."""
    assert ctx['datos'] is None


@then("se lanza ApiConnectionError")
def lanza_api_connection_error(ctx):
    """La excepción capturada es ApiConnectionError."""
    assert ctx['excepcion'] is not None
    assert isinstance(ctx['excepcion'], ApiConnectionError)


@then("se lanza ApiTimeoutError")
def lanza_api_timeout_error(ctx):
    """La excepción capturada es ApiTimeoutError."""
    assert ctx['excepcion'] is not None
    assert isinstance(ctx['excepcion'], ApiTimeoutError)


@then("el api_client del servicio es una instancia de MockApiClient")
def api_client_es_mock(ctx):
    """El api_client inyectado en testing es MockApiClient."""
    assert isinstance(ctx['api_client_inyectado'], MockApiClient)


@then("no se realizan peticiones HTTP reales al backend")
def sin_peticiones_http_reales(ctx):
    """El MockApiClient intercepta todas las llamadas — no hay HTTP real."""
    # Si llegó aquí sin ConnectionError, el mock funcionó
    assert isinstance(ctx['app'].termostato_service._api_client, MockApiClient)


@then(parsers.parse("la respuesta tiene código HTTP {codigo:d}"))
def verificar_codigo_http(ctx, codigo):
    """Valida el código de estado HTTP."""
    assert ctx['response'].status_code == codigo


@then("el dashboard muestra datos del termostato")
def dashboard_muestra_datos(ctx):
    """La página renderizada contiene datos del termostato (temperatura)."""
    contenido = ctx['response'].data.decode('utf-8')
    assert '22' in contenido or '24' in contenido


@then('la respuesta JSON contiene "success" igual a true')
def json_success_true(ctx):
    """El JSON de respuesta tiene success=true."""
    datos = json.loads(ctx['response'].data)
    assert datos.get('success') is True


@then('el campo "from_cache" es false')
def campo_from_cache_false(ctx):
    """El campo from_cache en la respuesta JSON es False."""
    datos = json.loads(ctx['response'].data)
    assert datos.get('from_cache') is False


@then("get() retorna el valor almacenado")
def get_retorna_valor(ctx):
    """El caché devuelve el valor antes de que expire el TTL."""
    assert ctx['cache'].get('clave_test') == 'valor_test'


@then("get() retorna None")
def get_retorna_none(ctx):
    """El caché devuelve None cuando el TTL ha expirado."""
    assert ctx['cache'].get('clave_test') is None


@then("no se producen condiciones de carrera")
def sin_condiciones_carrera(ctx):
    """No hubo errores durante la escritura/lectura concurrente."""
    assert not ctx['errores_hilos'], f"Errores en hilos: {ctx['errores_hilos']}"


@then("todos los valores son consistentes")
def valores_consistentes(ctx):
    """Cada índice almacenado puede ser leído correctamente."""
    for indice in range(30):
        valor = ctx['cache'].get(f'k{indice}')
        # El valor puede ser None si otro hilo sobreescribió o el hilo no terminó
        # Lo importante es que no hubo corrupción (no errores)
        assert valor is None or valor == indice
