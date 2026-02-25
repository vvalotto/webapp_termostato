"""
Implementación en memoria del caché, thread-safe.
Migra las variables globales `ultima_respuesta_valida` y `ultimo_timestamp`
de webapp/__init__.py a una abstracción con locking.
"""
import threading
from datetime import datetime, timedelta
from typing import Any, Optional

from .cache_interface import Cache


class MemoryCache(Cache):
    """Caché en memoria thread-safe basado en diccionario.

    Usa threading.Lock para garantizar consistencia en entornos
    multi-worker (Gunicorn con múltiples threads).

    Cada entrada almacena el valor y una marca de expiración opcional.
    Si el TTL expiró, get() devuelve None y elimina la entrada.

    Attributes:
        _data: Diccionario interno con entradas {'value': ..., 'expires': datetime|None}.
        _lock: Lock para acceso thread-safe.
    """

    def __init__(self) -> None:
        """Inicializar caché vacío con lock."""
        self._data: dict = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Obtener valor del caché de forma thread-safe.

        Si la entrada tiene TTL y expiró, se elimina y se devuelve None.

        Args:
            key: Clave del valor a recuperar.

        Returns:
            El valor almacenado, o None si no existe o expiró.
        """
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                return None
            expires = entry['expires']
            if expires is not None and datetime.utcnow() >= expires:
                del self._data[key]
                return None
            return entry['value']

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Almacenar valor en el caché de forma thread-safe.

        Args:
            key: Clave bajo la que almacenar el valor.
            value: Valor a almacenar (cualquier tipo serializable).
            ttl: Time-to-live en segundos. None = sin expiración.
        """
        expires = datetime.utcnow() + timedelta(seconds=ttl) if ttl is not None else None
        with self._lock:
            self._data[key] = {'value': value, 'expires': expires}

    def delete(self, key: str) -> None:
        """Eliminar una clave del caché de forma thread-safe.

        No lanza error si la clave no existe.

        Args:
            key: Clave a eliminar.
        """
        with self._lock:
            self._data.pop(key, None)

    def clear(self) -> None:
        """Limpiar todos los valores del caché de forma thread-safe."""
        with self._lock:
            self._data.clear()
