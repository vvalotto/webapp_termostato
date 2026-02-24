"""Capa de presentación — blueprints de rutas Flask."""
from .main import main_bp
from .api import api_bp
from .health import health_bp

__all__ = ['main_bp', 'api_bp', 'health_bp']
