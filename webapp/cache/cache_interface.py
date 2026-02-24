"""
Interfaz abstracta del sistema de caché.
Permite intercambiar implementaciones sin modificar el código consumidor.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional


class Cache(ABC):
    """Interfaz abstracta para sistemas de caché.

    Permite sustituir la implementación en memoria por Redis u otro
    backend sin modificar los servicios que la consumen (DIP).
    """

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Obtener un valor del caché.

        Args:
            key: Clave del valor a recuperar.

        Returns:
            El valor almacenado, o None si no existe.
        """

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Almacenar un valor en el caché.

        Args:
            key: Clave bajo la que almacenar el valor.
            value: Valor a almacenar.
        """

    @abstractmethod
    def clear(self) -> None:
        """Limpiar todos los valores del caché.

        Usado principalmente en tests para garantizar estado limpio.
        """
