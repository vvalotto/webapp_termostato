"""
Tests unitarios para RequestsApiClient.
Valida el cliente HTTP de forma aislada usando mocks de requests.
"""
from unittest.mock import patch, Mock

import pytest
import requests

from webapp.services.api_client import RequestsApiClient


@pytest.fixture
def cliente():
    """Fixture que retorna un cliente apuntando a URL de test."""
    return RequestsApiClient(base_url='http://localhost:5050', timeout=5)


class TestRequestsApiClientGet:
    """Tests del método get()."""

    @patch('webapp.services.api_client.requests.get')
    def test_get_exitoso_retorna_json(self, mock_get, cliente):
        """get() retorna el JSON de la respuesta cuando el backend responde."""
        mock_response = Mock()
        mock_response.json.return_value = {'clave': 'valor'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        resultado = cliente.get('/termostato/')

        assert resultado == {'clave': 'valor'}

    @patch('webapp.services.api_client.requests.get')
    def test_get_construye_url_correctamente(self, mock_get, cliente):
        """get() concatena base_url y path correctamente."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        cliente.get('/termostato/')

        url_llamada = mock_get.call_args[0][0]
        assert url_llamada == 'http://localhost:5050/termostato/'

    @patch('webapp.services.api_client.requests.get')
    def test_get_usa_timeout_configurado(self, mock_get, cliente):
        """get() pasa el timeout configurado a requests.get()."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        cliente.get('/termostato/')

        kwargs = mock_get.call_args[1]
        assert kwargs['timeout'] == 5

    @patch('webapp.services.api_client.requests.get')
    def test_get_permite_override_de_timeout(self, mock_get, cliente):
        """get() acepta timeout personalizado por llamada."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        cliente.get('/comprueba/', timeout=2)

        kwargs = mock_get.call_args[1]
        assert kwargs['timeout'] == 2

    @patch('webapp.services.api_client.requests.get')
    def test_get_lanza_excepcion_en_timeout(self, mock_get, cliente):
        """get() lanza Timeout si el backend no responde a tiempo."""
        mock_get.side_effect = requests.exceptions.Timeout('Timeout')

        with pytest.raises(requests.exceptions.Timeout):
            cliente.get('/termostato/')

    @patch('webapp.services.api_client.requests.get')
    def test_get_lanza_excepcion_en_error_de_conexion(self, mock_get, cliente):
        """get() lanza ConnectionError si el backend no está disponible."""
        mock_get.side_effect = requests.exceptions.ConnectionError('Sin conexión')

        with pytest.raises(requests.exceptions.ConnectionError):
            cliente.get('/termostato/')

    @patch('webapp.services.api_client.requests.get')
    def test_get_lanza_excepcion_en_error_http(self, mock_get, cliente):
        """get() lanza HTTPError si la respuesta tiene código de error."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError('404')
        mock_get.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError):
            cliente.get('/ruta-inexistente/')

    @patch('webapp.services.api_client.requests.get')
    def test_get_elimina_slash_duplicado_en_base_url(self, mock_get):
        """Base URL con slash final no genera URL con doble slash."""
        cliente_slash = RequestsApiClient(base_url='http://localhost:5050/')
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        cliente_slash.get('/termostato/')

        url_llamada = mock_get.call_args[0][0]
        assert '//' not in url_llamada.replace('http://', '')
