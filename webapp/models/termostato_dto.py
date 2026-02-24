"""
DTOs (Data Transfer Objects) para el termostato.
Tipado explícito de los datos recibidos desde la API backend.
"""
from typing import Optional, TypedDict


class TermostatoEstadoDTO(TypedDict, total=False):
    """DTO con el estado completo del termostato.

    Refleja la estructura de respuesta del endpoint /termostato/ del backend.

    Attributes:
        temperatura_ambiente: Temperatura actual del ambiente en grados.
        temperatura_deseada: Temperatura objetivo configurada en grados.
        carga_bateria: Nivel de carga de la batería en voltios.
        indicador: Indicador de batería ('NORMAL', 'BAJO', 'CRITICO').
        estado_climatizador: Estado del climatizador ('apagado', 'encendido',
            'enfriando', 'calentando').
    """

    temperatura_ambiente: Optional[float]
    temperatura_deseada: Optional[float]
    carga_bateria: Optional[float]
    indicador: Optional[str]
    estado_climatizador: Optional[str]
