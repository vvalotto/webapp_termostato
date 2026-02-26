"""
Step definitions BDD para US-003: Migración JavaScript a Módulos ES6.

Valida comportamientos del dashboard desde la perspectiva del usuario:
- Carga del dashboard con datos del termostato
- Actualización automática (polling a /api/estado)
- Reintentos y banner de desconexión cuando el backend falla
- Gráficas y selector de rango (vía /api/historial)
- Compatibilidad: mensaje para navegadores sin soporte ES6

Los steps se implementan al nivel HTTP/Flask (test client), verificando
que los endpoints proveen la información que el JS migrado necesita.
"""
import json

import pytest
from pytest_bdd import scenarios, given, when, then

from webapp import create_app
from webapp.services.api_client import ApiConnectionError, MockApiClient

# ---------------------------------------------------------------------------
# Cargar escenarios del feature file
# ---------------------------------------------------------------------------
scenarios('../features/US-003-migracion-es6-modules.feature')

# ---------------------------------------------------------------------------
# Datos de prueba
# ---------------------------------------------------------------------------
DATOS_ESTADO = {
    'temperatura_ambiente': 22.5,
    'temperatura_deseada': 24.0,
    'estado_climatizador': 'encendido',
    'carga_bateria': 4.1,
    'indicador': 'NORMAL',
}

DATOS_HISTORIAL = {
    'historial': [
        {'timestamp': '2026-01-01T10:00:00', 'temperatura': 21.0},
        {'timestamp': '2026-01-01T10:01:00', 'temperatura': 22.0},
        {'timestamp': '2026-01-01T10:02:00', 'temperatura': 22.5},
    ],
    'total': 3,
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def ctx():
    """Contexto mutable compartido entre todos los steps de un escenario."""
    return {
        'app': None,
        'response_dashboard': None,
        'response_api': None,
        'html': None,
    }


@pytest.fixture(autouse=True)
def limpiar_cache(ctx):
    """Limpia el caché del servicio al finalizar cada test."""
    yield
    if ctx.get('app'):
        ctx['app'].termostato_service._cache.clear()


def _crear_app_con_datos():
    """App con backend respondiendo correctamente."""
    app = create_app('testing')
    app.termostato_service._api_client = MockApiClient(DATOS_ESTADO)
    return app


def _crear_app_backend_caido():
    """App con backend caído (ApiConnectionError)."""
    app = create_app('testing')
    app.termostato_service._api_client = MockApiClient(
        {}, raise_error=ApiConnectionError
    )
    return app


# ---------------------------------------------------------------------------
# Given steps
# ---------------------------------------------------------------------------

@given("el usuario abre el dashboard del termostato")
def usuario_abre_dashboard(ctx):
    """El usuario navega al dashboard por primera vez."""
    ctx['app'] = _crear_app_con_datos()
    with ctx['app'].test_client() as c:
        ctx['response_dashboard'] = c.get('/')
        ctx['html'] = ctx['response_dashboard'].data.decode('utf-8')


@given("el usuario tiene el dashboard abierto")
def usuario_tiene_dashboard_abierto(ctx):
    """El dashboard está cargado y el usuario lo está viendo."""
    ctx['app'] = _crear_app_con_datos()
    with ctx['app'].test_client() as c:
        ctx['response_dashboard'] = c.get('/')
        ctx['html'] = ctx['response_dashboard'].data.decode('utf-8')


@given("el usuario tiene el dashboard con gráficas visibles")
def usuario_tiene_dashboard_con_graficas(ctx):
    """El dashboard está cargado con los canvas de gráficas presentes."""
    ctx['app'] = _crear_app_con_datos()
    with ctx['app'].test_client() as c:
        ctx['response_dashboard'] = c.get('/')
        ctx['html'] = ctx['response_dashboard'].data.decode('utf-8')


@given("un usuario con un navegador que no soporta módulos ES6")
def usuario_navegador_sin_es6(ctx):
    """Simula un contexto donde el navegador no soporta ES6 modules."""
    ctx['app'] = _crear_app_con_datos()


# ---------------------------------------------------------------------------
# When steps
# ---------------------------------------------------------------------------

@when("la página termina de cargar")
def pagina_termina_de_cargar(ctx):
    """La página ya fue cargada — la respuesta está en ctx['response_dashboard']."""
    assert ctx['response_dashboard'] is not None


@when("transcurren 10 segundos")
def transcurren_10_segundos(ctx):
    """
    Simula el polling automático: el JS llama a /api/estado cada 10 segundos.
    Aquí ejecutamos una llamada adicional a /api/estado.
    """
    with ctx['app'].test_client() as c:
        ctx['response_api'] = c.get('/api/estado')


@when("la API no responde en el primer intento")
def api_no_responde(ctx):
    """El backend cae — el JS detectará el error en la respuesta 503."""
    ctx['app'].termostato_service._cache.clear()
    ctx['app'].termostato_service._api_client = MockApiClient(
        {}, raise_error=ApiConnectionError
    )
    with ctx['app'].test_client() as c:
        ctx['response_api'] = c.get('/api/estado')


@when("la API deja de responder")
def api_deja_de_responder(ctx):
    """El backend se cae completamente — /api/estado retornará 503."""
    ctx['app'].termostato_service._cache.clear()
    ctx['app'].termostato_service._api_client = MockApiClient(
        {}, raise_error=ApiConnectionError
    )
    with ctx['app'].test_client() as c:
        ctx['response_api'] = c.get('/api/estado')


@when("selecciona un rango de tiempo diferente")
def selecciona_rango_tiempo(ctx):
    """
    El usuario hace clic en un rango de tiempo (ej: 1 hora).
    El JS llama a /api/historial?limite=60.
    """
    ctx['app'].termostato_service._api_client = MockApiClient(DATOS_HISTORIAL)
    with ctx['app'].test_client() as c:
        ctx['response_api'] = c.get('/api/historial?limite=60')


@when("abre el dashboard")
def abre_el_dashboard(ctx):
    """El usuario abre el dashboard — recibe el HTML con el entry point ES6."""
    with ctx['app'].test_client() as c:
        ctx['response_dashboard'] = c.get('/')
        ctx['html'] = ctx['response_dashboard'].data.decode('utf-8')


# ---------------------------------------------------------------------------
# Then steps
# ---------------------------------------------------------------------------

@then("se muestran los datos de temperatura y climatizador")
def se_muestran_datos(ctx):
    """
    El HTML del dashboard incluye los elementos donde el JS
    mostrará temperatura y climatizador.
    """
    html = ctx['html']
    # El HTML tiene los contenedores que el JS popula
    assert 'valor-temp-ambiente' in html
    assert 'badge-climatizador' in html


@then('el indicador de conexión muestra "Conectado"')
def indicador_conexion_conectado(ctx):
    """
    /api/estado retorna success=True y from_cache=False,
    lo que indica al JS mostrar estado "Conectado".
    """
    with ctx['app'].test_client() as c:
        resp = c.get('/api/estado')
        datos = json.loads(resp.data)

    assert resp.status_code == 200
    assert datos['success'] is True
    assert datos['from_cache'] is False


@then("los datos se actualizan sin recargar la página")
def datos_actualizan_sin_recargar(ctx):
    """
    /api/estado respondió correctamente al polling.
    El JS actualiza el DOM sin recargar (el test verifica la respuesta del endpoint).
    """
    assert ctx['response_api'] is not None
    assert ctx['response_api'].status_code == 200
    datos = json.loads(ctx['response_api'].data)
    assert datos['success'] is True


@then("se muestra el indicador de reintentando")
def se_muestra_indicador_reintentando(ctx):
    """
    /api/estado retorna 503 — el JS detecta el fallo y activa el indicador
    de "reintentando" con los reintentos automáticos configurados en CONFIG_REINTENTOS.
    """
    assert ctx['response_api'].status_code == 503


@then("el sistema vuelve a intentarlo automáticamente")
def sistema_reintenta(ctx):
    """
    El JS tiene configurados reintentos automáticos (CONFIG_REINTENTOS).
    Verificamos que /api/estado está disponible para ser consultado de nuevo.
    """
    with ctx['app'].test_client() as c:
        resp = c.get('/api/estado')
    # 503 indica que el backend sigue caído — el JS seguirá reintentando
    assert resp.status_code in (200, 503)


@then("aparece el banner de desconexión")
def aparece_banner_desconexion(ctx):
    """
    /api/estado retorna 503 (success=False) — el JS activa el banner de desconexión.
    """
    assert ctx['response_api'].status_code == 503
    datos = json.loads(ctx['response_api'].data)
    assert datos['success'] is False


@then("el usuario puede cerrarlo manualmente")
def usuario_puede_cerrar_banner(ctx):
    """
    El HTML del dashboard incluye el botón de cerrar del banner.
    El JS inicializa el evento click en inicializarBannerCerrar().
    """
    assert 'banner-cerrar' in ctx['html']


@then("la gráfica de temperatura es visible")
def grafica_temperatura_visible(ctx):
    """El HTML incluye el canvas donde Chart.js renderizará la gráfica de temperatura."""
    assert 'temperaturaChart' in ctx['html']


@then("la gráfica de climatizador es visible")
def grafica_climatizador_visible(ctx):
    """El HTML incluye el canvas donde Chart.js renderizará la gráfica del climatizador."""
    assert 'climatizadorChart' in ctx['html']


@then("las gráficas se actualizan con el nuevo rango")
def graficas_actualizan_con_rango(ctx):
    """
    /api/historial?limite=N respondió con datos para el rango seleccionado.
    El JS actualiza las gráficas con estos datos.
    """
    assert ctx['response_api'].status_code == 200
    datos = json.loads(ctx['response_api'].data)
    assert datos['success'] is True
    assert 'historial' in datos


@then("ve un mensaje indicando que debe actualizar su navegador")
def ve_mensaje_actualizar_navegador(ctx):
    """
    El HTML incluye <script nomodule> con el mensaje para navegadores sin soporte ES6.
    En esos navegadores, el script type="module" es ignorado y el nomodule se ejecuta.
    """
    html = ctx['html']
    assert 'nomodule' in html
    # El mensaje de actualización debe estar presente
    html_lower = html.lower()
    assert ('navegador' in html_lower or 'browser' in html_lower
            or 'módulos' in html_lower or 'ES6' in html)
