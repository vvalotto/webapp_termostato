"""
Implementación en memoria del caché, thread-safe.
Migra las variables globales `ultima_respuesta_valida` y `ultimo_timestamp`
de webapp/__init__.py a una abstracción con locking.
"""
import threading
from typing import Any, Optional

from .cache_interface import Cache


class MemoryCache(Cache):
    """Caché en memoria thread-safe basado en diccionario.

    Usa threading.Lock para garantizar consistencia en entornos
    multi-worker (Gunicorn con múltiples threads).

    Attributes:
        _data: Diccionario interno de almacenamiento.
        _lock: Lock para acceso thread-safe.
    """

    def __init__(self) -> None:
        """Inicializar caché vacío con lock."""
        self._data: dict = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Obtener valor del caché de forma thread-safe.

        Args:
            key: Clave del valor a recuperar.

        Returns:
            El valor almacenado, o None si la clave no existe.
        """
        with self._lock:
            return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        """Almacenar valor en el caché de forma thread-safe.

        Args:
            key: Clave bajo la que almacenar el valor.
            value: Valor a almacenar (cualquier tipo serializable).
        """
        with self._lock:
            self._data[key] = value

    def clear(self) -> None:
        """Limpiar todos los valores del caché de forma thread-safe."""
        with self._lock:
            self._data.clear()
