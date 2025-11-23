"""
Formularios de la aplicación web del termostato.
Define los formularios utilizados para mostrar datos en la interfaz.
"""
from flask_wtf import FlaskForm
from wtforms import StringField


class TermostatoForm(FlaskForm):
    """
    Formulario para mostrar el estado del termostato.

    Attributes:
        temperatura_ambiente: Temperatura actual del ambiente
        temperatura_deseada: Temperatura objetivo configurada
        carga_bateria: Nivel de carga de la batería
        estado_climatizador: Estado actual (encendido/apagado)
    """
    temperatura_ambiente = StringField('Temperatura Ambiente')
    temperatura_deseada = StringField('Temperatura Deseada')
    carga_bateria = StringField('Carga de Batería')
    estado_climatizador = StringField('Estado Climatizador')
