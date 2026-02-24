"""
Tests unitarios para la capa de caché.
Valida MemoryCache de forma aislada, sin dependencias externas.
"""
import threading

import pytest

from webapp.cache.memory_cache import MemoryCache


@pytest.fixture
def cache():
    """Fixture que retorna un caché limpio para cada test."""
    return MemoryCache()


class TestMemoryCacheSetGet:
    """Tests de almacenamiento y recuperación."""

    def test_set_y_get_retorna_valor(self, cache):
        """get() retorna el valor almacenado con set()."""
        cache.set('clave', 'valor')
        assert cache.get('clave') == 'valor'

    def test_get_clave_inexistente_retorna_none(self, cache):
        """get() retorna None si la clave no existe."""
        assert cache.get('no_existe') is None

    def test_set_sobreescribe_valor_existente(self, cache):
        """set() sobreescribe el valor anterior de la misma clave."""
        cache.set('clave', 'primero')
        cache.set('clave', 'segundo')
        assert cache.get('clave') == 'segundo'

    def test_almacena_distintos_tipos(self, cache):
        """Almacena y recupera correctamente distintos tipos de valor."""
        cache.set('entero', 42)
        cache.set('diccionario', {'a': 1, 'b': 2})
        cache.set('tupla', (10, 'x'))
        cache.set('none', None)

        assert cache.get('entero') == 42
        assert cache.get('diccionario') == {'a': 1, 'b': 2}
        assert cache.get('tupla') == (10, 'x')
        assert cache.get('none') is None

    def test_multiples_claves_independientes(self, cache):
        """Claves distintas almacenan valores independientes."""
        cache.set('k1', 'v1')
        cache.set('k2', 'v2')

        assert cache.get('k1') == 'v1'
        assert cache.get('k2') == 'v2'


class TestMemoryCacheClear:
    """Tests del método clear()."""

    def test_clear_elimina_todos_los_valores(self, cache):
        """clear() deja el caché vacío."""
        cache.set('k1', 'v1')
        cache.set('k2', 'v2')
        cache.clear()

        assert cache.get('k1') is None
        assert cache.get('k2') is None

    def test_clear_en_cache_vacio_no_falla(self, cache):
        """clear() no lanza excepción si el caché ya está vacío."""
        cache.clear()  # No debe fallar
        assert cache.get('cualquier') is None

    def test_set_tras_clear_funciona(self, cache):
        """Después de clear() se puede volver a almacenar valores."""
        cache.set('k', 'antes')
        cache.clear()
        cache.set('k', 'despues')

        assert cache.get('k') == 'despues'


class TestMemoryCacheThreadSafety:
    """Tests de seguridad en entornos multi-hilo."""

    def test_escrituras_concurrentes_no_corrompen_datos(self, cache):
        """Escrituras simultáneas desde múltiples hilos son seguras."""
        errores = []

        def escribir(indice):
            try:
                cache.set(f'clave_{indice}', indice)
            except Exception as e:  # pylint: disable=broad-except
                errores.append(e)

        hilos = [threading.Thread(target=escribir, args=(i,)) for i in range(50)]
        for hilo in hilos:
            hilo.start()
        for hilo in hilos:
            hilo.join()

        assert not errores, f"Errores en hilos: {errores}"
        # Verificar que todos los valores fueron escritos
        for i in range(50):
            assert cache.get(f'clave_{i}') == i
