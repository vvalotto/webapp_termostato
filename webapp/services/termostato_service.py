"""
Servicio de dominio del termostato.
Encapsula la lógica de negocio: obtención de estado, historial y health check.
Migra la función obtener_estado_termostato() de webapp/__init__.py.
"""
from datetime import datetime
from typing import Optional, Tuple

from webapp.cache.cache_interface import Cache
from webapp.services.api_client import ApiClient, ApiError

# Clave usada para almacenar el estado en el caché
_CACHE_KEY_ESTADO = 'estado'


class TermostatoService:
    """Servicio que gestiona los datos del termostato.

    Encapsula:
    - Comunicación con la API backend via ApiClient inyectado.
    - Estrategia de caché fallback via Cache inyectado.
    - Lógica de negocio para estado, historial y health.

    Attributes:
        _api_client: Cliente HTTP inyectado.
        _cache: Sistema de caché inyectado.
    """

    def __init__(self, api_client: ApiClient, cache: Cache) -> None:
        """Inicializar servicio con dependencias inyectadas.

        Args:
            api_client: Implementación de ApiClient a usar.
            cache: Implementación de Cache a usar.
        """
        self._api_client = api_client
        self._cache = cache

    def obtener_estado(self) -> Tuple[Optional[dict], Optional[str], bool]:
        """Obtener estado completo del termostato con fallback a caché.

        Intenta obtener datos frescos del backend. Si falla, devuelve
        la última respuesta válida almacenada en caché.

        Returns:
            Tupla (datos, timestamp, from_cache) donde:
            - datos: Dict con el estado del termostato, o None si no hay datos.
            - timestamp: ISO timestamp de la última actualización exitosa.
            - from_cache: True si los datos provienen del caché.
        """
        try:
            datos = self._api_client.get('/termostato/')
            timestamp = datetime.utcnow().isoformat()
            self._cache.set(_CACHE_KEY_ESTADO, (datos, timestamp))
            return datos, timestamp, False
        except ApiError:
            cached = self._cache.get(_CACHE_KEY_ESTADO)
            if cached:
                datos_cache, timestamp_cache = cached
                return datos_cache, timestamp_cache, True
            return None, None, False

    def obtener_historial(self, limite: int = 60) -> dict:
        """Obtener historial de temperaturas desde el backend.

        Args:
            limite: Número máximo de registros a obtener (default: 60).

        Returns:
            Dict con 'historial' (lista) y 'total' (int).

        Raises:
            requests.exceptions.RequestException: Si el backend no responde.
        """
        return self._api_client.get(
            f'/termostato/historial/?limite={limite}',
            timeout=10
        )

    def health_check(self) -> dict:
        """Verificar estado del backend via endpoint /comprueba/.

        Returns:
            Dict con datos del backend: status, version, uptime_seconds.

        Raises:
            requests.exceptions.RequestException: Si el backend no responde.
        """
        return self._api_client.get('/comprueba/', timeout=2)
