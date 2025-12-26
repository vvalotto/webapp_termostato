"""
Tests unitarios para la aplicacion webapp_termostato.
WT-26: Tests unitarios basicos

pylint: disable=redefined-outer-name
"""
import os
import sys
from unittest.mock import patch, Mock

import pytest
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lanzador import app  # noqa: E402  pylint: disable=wrong-import-position


# Datos de ejemplo que devuelve la API
DATOS_API_VALIDOS = {
    'temperatura_ambiente': 22,
    'temperatura_deseada': 24,
    'estado_climatizador': 'encendido',
    'carga_bateria': 3.8,
    'indicador': 'NORMAL'
}

DATOS_HISTORIAL_VALIDOS = {
    'historial': [
        {'timestamp': '2025-12-26T10:30:00', 'temperatura': 22},
        {'timestamp': '2025-12-26T10:31:00', 'temperatura': 22.5}
    ],
    'total': 2
}


@pytest.fixture
def client():
    """Fixture que proporciona un cliente de pruebas Flask."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def reset_cache():
    """Fixture para limpiar el cache entre tests."""
    import lanzador  # pylint: disable=import-outside-toplevel
    lanzador.ultima_respuesta_valida = None
    lanzador.ultimo_timestamp = None
    yield
    lanzador.ultima_respuesta_valida = None
    lanzador.ultimo_timestamp = None


@pytest.mark.usefixtures('reset_cache')
class TestRutaIndex:
    """Tests para la ruta principal /"""

    @patch('lanzador.requests.get')
    def test_index_con_api_funcionando(self, mock_get, client):
        """Test de ruta / con API funcionando correctamente."""
        # Configurar mock para simular respuesta exitosa de la API
        mock_response = Mock()
        mock_response.json.return_value = DATOS_API_VALIDOS
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Hacer peticion a la ruta principal
        response = client.get('/')

        # Verificar respuesta exitosa
        assert response.status_code == 200
        assert b'Dashboard Termostato' in response.data
        assert b'22' in response.data  # temperatura_ambiente
        assert b'24' in response.data  # temperatura_deseada
        assert b'ENCENDIDO' in response.data  # estado_climatizador

    @patch('lanzador.requests.get')
    def test_index_con_api_caida(self, mock_get, client):
        """Test de ruta / con API caida (sin conexion)."""
        # Configurar mock para simular error de conexion
        mock_get.side_effect = requests.exceptions.ConnectionError('No connection')

        # Hacer peticion a la ruta principal
        response = client.get('/')

        # Verificar que la pagina carga pero muestra error
        assert response.status_code == 200
        assert b'Dashboard Termostato' in response.data
        assert b'Error API' in response.data

    @patch('lanzador.requests.get')
    def test_index_con_api_timeout(self, mock_get, client):
        """Test de ruta / con API timeout."""
        # Configurar mock para simular timeout
        mock_get.side_effect = requests.exceptions.Timeout('Timeout')

        # Hacer peticion a la ruta principal
        response = client.get('/')

        # Verificar que la pagina carga pero muestra error
        assert response.status_code == 200
        assert b'Error API' in response.data

    @patch('lanzador.requests.get')
    def test_index_usa_cache_cuando_api_cae(self, mock_get, client):
        """Test que verifica el uso de cache cuando la API falla."""
        # Primera llamada: API funciona
        mock_response = Mock()
        mock_response.json.return_value = DATOS_API_VALIDOS
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        response1 = client.get('/')
        assert response1.status_code == 200
        assert b'22' in response1.data

        # Segunda llamada: API falla, debe usar cache
        mock_get.side_effect = requests.exceptions.ConnectionError('No connection')

        response2 = client.get('/')
        assert response2.status_code == 200
        assert b'22' in response2.data  # Datos del cache


@pytest.mark.usefixtures('reset_cache')
class TestApiEstado:
    """Tests para el endpoint /api/estado"""

    @patch('lanzador.requests.get')
    def test_api_estado_funcionando(self, mock_get, client):
        """Test de /api/estado con API funcionando."""
        mock_response = Mock()
        mock_response.json.return_value = DATOS_API_VALIDOS
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        response = client.get('/api/estado')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['temperatura_ambiente'] == 22
        assert data['from_cache'] is False

    @patch('lanzador.requests.get')
    def test_api_estado_con_api_caida(self, mock_get, client):
        """Test de /api/estado con API caida y sin cache."""
        mock_get.side_effect = requests.exceptions.ConnectionError('No connection')

        response = client.get('/api/estado')

        assert response.status_code == 503
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data

    @patch('lanzador.requests.get')
    def test_api_estado_usa_cache(self, mock_get, client):
        """Test de /api/estado retorna datos cacheados cuando API falla."""
        # Primera llamada exitosa
        mock_response = Mock()
        mock_response.json.return_value = DATOS_API_VALIDOS
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client.get('/api/estado')

        # Segunda llamada con API caida
        mock_get.side_effect = requests.exceptions.ConnectionError('No connection')

        response = client.get('/api/estado')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['from_cache'] is True


class TestApiHistorial:
    """Tests para el endpoint /api/historial"""

    @patch('lanzador.requests.get')
    def test_api_historial_funcionando(self, mock_get, client):
        """Test de /api/historial con API funcionando."""
        mock_response = Mock()
        mock_response.json.return_value = DATOS_HISTORIAL_VALIDOS
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        response = client.get('/api/historial')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['historial']) == 2
        assert data['total'] == 2

    @patch('lanzador.requests.get')
    def test_api_historial_con_limite(self, mock_get, client):
        """Test de /api/historial con parametro limite."""
        mock_response = Mock()
        mock_response.json.return_value = DATOS_HISTORIAL_VALIDOS
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        response = client.get('/api/historial?limite=100')

        assert response.status_code == 200
        # Verificar que se llamo con el limite correcto
        mock_get.assert_called_once()
        call_url = mock_get.call_args[0][0]
        assert 'limite=100' in call_url

    @patch('lanzador.requests.get')
    def test_api_historial_con_api_caida(self, mock_get, client):
        """Test de /api/historial con API caida."""
        mock_get.side_effect = requests.exceptions.ConnectionError('No connection')

        response = client.get('/api/historial')

        assert response.status_code == 503
        data = response.get_json()
        assert data['success'] is False
        assert data['historial'] == []
