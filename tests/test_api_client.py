"""
Tests unitarios para RequestsApiClient y MockApiClient.
Valida el cliente HTTP de forma aislada usando mocks de requests.
"""
from unittest.mock import patch, Mock

import pytest
import requests

from webapp.services.api_client import (
    ApiConnectionError,
    ApiError,
    ApiTimeoutError,
    MockApiClient,
    RequestsApiClient,
)


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
    def test_get_lanza_api_timeout_error(self, mock_get, cliente):
        """get() relanza Timeout como ApiTimeoutError."""
        mock_get.side_effect = requests.exceptions.Timeout('Timeout')

        with pytest.raises(ApiTimeoutError):
            cliente.get('/termostato/')

    @patch('webapp.services.api_client.requests.get')
    def test_get_lanza_api_connection_error(self, mock_get, cliente):
        """get() relanza ConnectionError como ApiConnectionError."""
        mock_get.side_effect = requests.exceptions.ConnectionError('Sin conexión')

        with pytest.raises(ApiConnectionError):
            cliente.get('/termostato/')

    @patch('webapp.services.api_client.requests.get')
    def test_get_lanza_api_error_en_error_http(self, mock_get, cliente):
        """get() relanza HTTPError como ApiError."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError('404')
        mock_get.return_value = mock_response

        with pytest.raises(ApiError):
            cliente.get('/ruta-inexistente/')

    @patch('webapp.services.api_client.requests.get')
    def test_api_timeout_es_subclase_de_api_error(self, mock_get, cliente):
        """ApiTimeoutError es subclase de ApiError (catcheable con except ApiError)."""
        mock_get.side_effect = requests.exceptions.Timeout('Timeout')

        with pytest.raises(ApiError):
            cliente.get('/termostato/')

    @patch('webapp.services.api_client.requests.get')
    def test_api_connection_error_es_subclase_de_api_error(self, mock_get, cliente):
        """ApiConnectionError es subclase de ApiError (catcheable con except ApiError)."""
        mock_get.side_effect = requests.exceptions.ConnectionError('Sin conexión')

        with pytest.raises(ApiError):
            cliente.get('/termostato/')

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


class TestMockApiClient:
    """Tests unitarios para MockApiClient."""

    def test_retorna_datos_configurados(self):
        """get() devuelve los datos configurados en el constructor."""
        datos = {'temperatura': 22}
        mock = MockApiClient(datos)

        resultado = mock.get('/termostato/')

        assert resultado == datos

    def test_incrementa_call_count(self):
        """call_count se incrementa en 1 por cada llamada a get()."""
        mock = MockApiClient({})

        mock.get('/ruta-a/')
        mock.get('/ruta-b/')

        assert mock.call_count == 2

    def test_registra_last_path(self):
        """last_path contiene el último path consultado."""
        mock = MockApiClient({})

        mock.get('/termostato/')
        mock.get('/comprueba/')

        assert mock.last_path == '/comprueba/'

    def test_last_path_es_none_al_inicio(self):
        """last_path es None antes de cualquier llamada."""
        mock = MockApiClient({})
        assert mock.last_path is None

    def test_call_count_es_cero_al_inicio(self):
        """call_count es 0 antes de cualquier llamada."""
        mock = MockApiClient({})
        assert mock.call_count == 0

    def test_lanza_error_cuando_raise_error_configurado(self):
        """get() lanza la excepción configurada en raise_error."""
        mock = MockApiClient({}, raise_error=ApiConnectionError)

        with pytest.raises(ApiConnectionError):
            mock.get('/termostato/')

    def test_incrementa_call_count_incluso_al_lanzar_error(self):
        """call_count se incrementa aunque get() lance excepción."""
        mock = MockApiClient({}, raise_error=ApiConnectionError)

        with pytest.raises(ApiConnectionError):
            mock.get('/termostato/')

        assert mock.call_count == 1

    def test_acepta_api_timeout_error_como_raise_error(self):
        """raise_error puede ser ApiTimeoutError."""
        mock = MockApiClient({}, raise_error=ApiTimeoutError)

        with pytest.raises(ApiTimeoutError):
            mock.get('/termostato/')

    def test_sin_raise_error_no_lanza_excepcion(self):
        """Sin raise_error configurado, get() no lanza excepciones."""
        mock = MockApiClient({'key': 'value'})

        resultado = mock.get('/cualquier/ruta/')

        assert resultado == {'key': 'value'}
