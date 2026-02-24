"""
Configuración de la aplicación webapp_termostato.
Jerarquía de objetos de configuración para diferentes entornos.
"""
import os


class Config:
    """Configuración base compartida por todos los entornos."""

    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'clave-desarrollo-local')
    URL_APP_API: str = os.environ.get('API_URL', os.environ.get('URL_APP_API', 'http://localhost:5050'))
    API_TIMEOUT: int = 5
    API_TIMEOUT_HEALTH: int = 2


class DevelopmentConfig(Config):
    """Configuración para entorno de desarrollo."""

    DEBUG: bool = True


class TestingConfig(Config):
    """Configuración para entorno de testing."""

    TESTING: bool = True
    WTF_CSRF_ENABLED: bool = False
    URL_APP_API: str = 'http://localhost:5050'


class ProductionConfig(Config):
    """Configuración para entorno de producción."""

    DEBUG: bool = False


config: dict = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
