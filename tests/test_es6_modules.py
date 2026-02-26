"""
Tests unitarios para US-003: Migración JavaScript a Módulos ES6.

Validan dos contratos:
1. Template Flask — el dashboard usa un único entry point type="module"
2. Estructura de archivos JS — cada módulo exporta sus símbolos públicos
   e importa sus dependencias explícitamente.
"""
import os
import pytest

from webapp import create_app

# ---------------------------------------------------------------------------
# Rutas de archivos JS
# ---------------------------------------------------------------------------

_BASE_JS = os.path.join(
    os.path.dirname(__file__), '..', 'webapp', 'static', 'js'
)

MODULOS_RAIZ = [
    'config.js',
    'dom-utils.js',
    'diferencia.js',
    'validacion.js',
    'bateria.js',
    'tendencia.js',
    'historial.js',
    'conexion.js',
    'api.js',
    'app.js',
]

MODULOS_GRAFICAS = [
    'graficas/config.js',
    'graficas/temperatura.js',
    'graficas/climatizador.js',
]

TODOS_LOS_MODULOS = MODULOS_RAIZ + MODULOS_GRAFICAS


def _leer(relpath):
    """Devuelve el contenido de un archivo JS."""
    with open(os.path.join(_BASE_JS, relpath), encoding='utf-8') as f:
        return f.read()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    """App Flask para testing con MockApiClient."""
    return create_app('testing')


@pytest.fixture
def client(app):
    """Cliente HTTP de pruebas."""
    with app.test_client() as c:
        yield c


@pytest.fixture
def dashboard_html(client):
    """HTML renderizado del dashboard."""
    response = client.get('/')
    return response.data.decode('utf-8')


# ---------------------------------------------------------------------------
# TestTemplateES6 — contratos del template index.html
# ---------------------------------------------------------------------------

class TestTemplateES6:
    """Verifica que el template usa módulos ES6 correctamente."""

    def test_existe_script_type_module(self, dashboard_html):
        """El dashboard incluye exactamente un <script type="module">."""
        assert 'type="module"' in dashboard_html

    def test_entry_point_es_app_js(self, dashboard_html):
        """El único entry point apunta a app.js."""
        assert 'js/app.js' in dashboard_html

    def test_existe_fallback_nomodule(self, dashboard_html):
        """El template incluye <script nomodule> para navegadores sin soporte."""
        assert 'nomodule' in dashboard_html

    def test_no_carga_modulos_individualmente(self, dashboard_html):
        """No hay tags <script src> para módulos internos (config, conexion, etc.)."""
        modulos_internos = [
            'js/config.js',
            'js/conexion.js',
            'js/api.js',
            'js/validacion.js',
            'js/dom-utils.js',
            'js/bateria.js',
            'js/tendencia.js',
            'js/diferencia.js',
            'js/historial.js',
            'js/graficas/config.js',
            'js/graficas/temperatura.js',
            'js/graficas/climatizador.js',
        ]
        for modulo in modulos_internos:
            # Acepta que aparezca en type="module" de app.js, pero no como script src separado
            assert f'src="{modulo}"' not in dashboard_html
            assert f"src='{modulo}'" not in dashboard_html

    def test_dashboard_responde_200(self, client):
        """El dashboard sigue respondiendo con status 200."""
        response = client.get('/')
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# TestJSModulosEstructura — contratos de los archivos JS
# ---------------------------------------------------------------------------

class TestJSModulosEstructura:
    """Verifica que los archivos JS usan sintaxis de módulos ES6."""

    @pytest.mark.parametrize("modulo", TODOS_LOS_MODULOS)
    def test_no_tiene_comentario_exported(self, modulo):
        """Ningún módulo tiene comentarios /* exported */ (sintaxis de globals)."""
        contenido = _leer(modulo)
        assert '/* exported' not in contenido, (
            f"{modulo} todavía tiene comentario '/* exported */'"
        )

    @pytest.mark.parametrize("modulo", TODOS_LOS_MODULOS)
    def test_no_tiene_comentario_global(self, modulo):
        """Ningún módulo tiene comentarios /* global */ para variables propias."""
        contenido = _leer(modulo)
        assert '/* global' not in contenido, (
            f"{modulo} todavía tiene comentario '/* global */'"
        )

    @pytest.mark.parametrize("modulo", TODOS_LOS_MODULOS)
    def test_tiene_export(self, modulo):
        """Cada módulo exporta al menos un símbolo público con 'export'."""
        contenido = _leer(modulo)
        assert 'export ' in contenido, (
            f"{modulo} no tiene ninguna declaración 'export'"
        )

    @pytest.mark.parametrize("modulo", [
        'validacion.js',
        'bateria.js',
        'tendencia.js',
        'historial.js',
        'conexion.js',
        'api.js',
        'app.js',
        'graficas/config.js',
        'graficas/temperatura.js',
        'graficas/climatizador.js',
    ])
    def test_tiene_import(self, modulo):
        """Los módulos que tienen dependencias usan 'import' explícito."""
        contenido = _leer(modulo)
        assert 'import ' in contenido, (
            f"{modulo} debería tener declaraciones 'import' para sus dependencias"
        )

    def test_config_exporta_constantes_clave(self):
        """config.js exporta las constantes principales."""
        contenido = _leer('config.js')
        constantes = [
            'INTERVALO_MS',
            'CONFIG_REINTENTOS',
            'ESTADOS_CONEXION',
            'REGLAS_VALIDACION',
            'TOOLTIPS_BATERIA',
            'RANGOS_TIEMPO',
        ]
        for const in constantes:
            assert f'export const {const}' in contenido, (
                f"config.js no exporta '{const}'"
            )

    def test_app_js_importa_todos_los_modulos_clave(self):
        """app.js importa los módulos principales que necesita."""
        contenido = _leer('app.js')
        imports_esperados = [
            './config.js',
            './api.js',
            './validacion.js',
            './dom-utils.js',
            './conexion.js',
            './bateria.js',
            './tendencia.js',
            './diferencia.js',
            './graficas/temperatura.js',
            './graficas/climatizador.js',
            './historial.js',
        ]
        for modulo in imports_esperados:
            assert modulo in contenido, (
                f"app.js no importa '{modulo}'"
            )

    def test_api_js_importa_conexion(self):
        """api.js importa mostrarReintentando desde conexion.js."""
        contenido = _leer('api.js')
        assert './conexion.js' in contenido

    def test_conexion_js_importa_config_y_dom_utils(self):
        """conexion.js importa sus dependencias de config.js y dom-utils.js."""
        contenido = _leer('conexion.js')
        assert './config.js' in contenido
        assert './dom-utils.js' in contenido

    def test_graficas_temperatura_importa_historial(self):
        """graficas/temperatura.js importa obtenerHistorialAPI de historial.js."""
        contenido = _leer('graficas/temperatura.js')
        assert '../historial.js' in contenido

    def test_graficas_usan_config_relativo(self):
        """Los módulos de graficas importan config principal con ruta relativa ../."""
        for modulo in ['graficas/config.js', 'graficas/temperatura.js', 'graficas/climatizador.js']:
            contenido = _leer(modulo)
            assert '../config.js' in contenido, (
                f"{modulo} debería importar '../config.js'"
            )
