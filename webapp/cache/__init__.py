"""Capa de infraestructura — sistema de caché."""
from .cache_interface import Cache
from .memory_cache import MemoryCache

__all__ = ['Cache', 'MemoryCache']
