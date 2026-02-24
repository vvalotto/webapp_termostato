"""
Cliente HTTP para comunicación con la API backend del termostato.
Abstracción que permite sustituir el cliente real por un mock en tests (DIP).
"""
from abc import ABC, abstractmethod
from typing import Any

import requests


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
            requests.exceptions.RequestException: Si hay error de red o HTTP.
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
            requests.exceptions.RequestException: Si hay error de red,
                timeout o respuesta HTTP de error.
        """
        url = self._base_url + path
        timeout = kwargs.pop('timeout', self._timeout)
        respuesta = requests.get(url, timeout=timeout, **kwargs)
        respuesta.raise_for_status()
        return respuesta.json()
