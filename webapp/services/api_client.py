"""
Cliente HTTP para comunicación con la API backend del termostato.
Abstracción que permite sustituir el cliente real por un mock en tests (DIP).
"""
from abc import ABC, abstractmethod
from typing import Any, Optional

import requests


class ApiError(Exception):
    """Error base para fallos de comunicación con la API backend."""


class ApiConnectionError(ApiError):
    """Error de red: conexión rechazada o host inalcanzable."""


class ApiTimeoutError(ApiError):
    """La petición superó el timeout configurado."""


class ApiClient(ABC):
    """Interfaz abstracta para cliente HTTP.

    Permite inyectar implementaciones alternativas (mock, stub)
    sin modificar los servicios que la consumen.
    """

    @abstractmethod
    def get(self, path: str, **kwargs: Any) -> dict:
        """Realizar petición GET a la API backend.

        Args:
            path: Ruta relativa del endpoint (ej: '/termostato/').
            **kwargs: Argumentos adicionales para la petición.

        Returns:
            Dict con la respuesta JSON del backend.

        Raises:
            ApiConnectionError: Si hay error de red o conexión rechazada.
            ApiTimeoutError: Si la petición supera el timeout.
            ApiError: Para cualquier otro error HTTP.
        """


class RequestsApiClient(ApiClient):
    """Implementación real del cliente HTTP usando la librería requests.

    Attributes:
        _base_url: URL base de la API backend.
        _timeout: Timeout en segundos para las peticiones.
    """

    def __init__(self, base_url: str, timeout: int = 5) -> None:
        """Inicializar cliente con URL base y timeout.

        Args:
            base_url: URL base del backend (ej: 'http://localhost:5050').
            timeout: Timeout en segundos (default: 5).
        """
        self._base_url = base_url.rstrip('/')
        self._timeout = timeout

    def get(self, path: str, **kwargs: Any) -> dict:
        """Realizar petición GET al backend.

        Args:
            path: Ruta relativa del endpoint (ej: '/termostato/').
            **kwargs: Argumentos adicionales pasados a requests.get().

        Returns:
            Dict con el JSON de la respuesta.

        Raises:
            ApiConnectionError: Si hay error de red o conexión rechazada.
            ApiTimeoutError: Si la petición supera el timeout.
            ApiError: Para cualquier otro error HTTP o de requests.
        """
        url = self._base_url + path
        timeout = kwargs.pop('timeout', self._timeout)
        try:
            respuesta = requests.get(url, timeout=timeout, **kwargs)
            respuesta.raise_for_status()
            return respuesta.json()
        except requests.exceptions.Timeout as exc:
            raise ApiTimeoutError(f"Timeout accediendo a {url}") from exc
        except requests.exceptions.ConnectionError as exc:
            raise ApiConnectionError(f"Error de conexión a {url}") from exc
        except requests.exceptions.RequestException as exc:
            raise ApiError(f"Error de API: {exc}") from exc


class MockApiClient(ApiClient):
    """Mock de ApiClient para testing. No realiza peticiones HTTP reales.

    Permite inyectar datos predefinidos o simular errores sin depender
    de un backend real ni de @patch.

    Attributes:
        mock_data: Datos a devolver en cada llamada a get().
        raise_error: Si se especifica, get() lanza este tipo de excepción.
        call_count: Número de veces que se llamó a get().
        last_path: Último path consultado via get().
    """

    def __init__(
        self,
        mock_data: dict,
        raise_error: Optional[type] = None
    ) -> None:
        """Inicializar mock con datos y comportamiento opcionales.

        Args:
            mock_data: Dict a devolver en cada llamada a get().
            raise_error: Tipo de excepción a lanzar (ej: ApiConnectionError).
                Si es None, get() devuelve mock_data normalmente.
        """
        self.mock_data = mock_data
        self.raise_error = raise_error
        self.call_count: int = 0
        self.last_path: Optional[str] = None

    def get(self, path: str, **kwargs: Any) -> dict:
        """Devolver datos del mock o lanzar error simulado.

        Args:
            path: Ruta consultada (se registra en last_path).
            **kwargs: Ignorados (compatibilidad con la interfaz).

        Returns:
            mock_data configurado en el constructor.

        Raises:
            ApiError (o subclase): Si raise_error fue configurado.
        """
        self.call_count += 1
        self.last_path = path
        if self.raise_error is not None:
            raise self.raise_error(f"Mock error para {path}")
        return self.mock_data
