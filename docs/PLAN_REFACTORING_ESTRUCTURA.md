# Plan de Refactoring: Reorganizacion de Estructura del Proyecto

## Objetivo

Reorganizar el proyecto para tener una estructura mas clara y estandar:

```
webapp_termostato/
├── docs/                    # Documentacion
├── quality/                 # Calidad de codigo
├── tests/                   # Tests unitarios
├── webapp/                  # Aplicacion Flask
│   ├── __init__.py          # App Flask + rutas
│   ├── forms.py             # Formularios WTF
│   ├── templates/           # Templates Jinja2
│   └── static/              # CSS, JS, imagenes
├── app.py                   # Punto de entrada
├── pytest.ini               # Configuracion pytest
├── requirements.txt         # Dependencias produccion
└── requirements-dev.txt     # Dependencias desarrollo
```

## Pre-requisitos

- [ ] Commit de cambios pendientes (WT-24, WT-26)
- [ ] Crear rama nueva para el refactoring

---

## Paso 1: Crear estructura de carpeta webapp

**Acciones:**
1. Crear directorio `webapp/`
2. Crear `webapp/__init__.py` vacio inicialmente

**Comandos:**
```bash
mkdir webapp
touch webapp/__init__.py
```

---

## Paso 2: Mover archivos estaticos y templates

**Acciones:**
1. Mover `templates/` a `webapp/templates/`
2. Mover `static/` a `webapp/static/`

**Comandos:**
```bash
mv templates webapp/
mv static webapp/
```

---

## Paso 3: Mover forms.py

**Acciones:**
1. Mover `forms.py` a `webapp/forms.py`

**Comandos:**
```bash
mv forms.py webapp/
```

---

## Paso 4: Crear webapp/__init__.py con la aplicacion

**Acciones:**
1. Migrar contenido de `lanzador.py` a `webapp/__init__.py`
2. Ajustar imports (forms ahora es local)
3. Mantener la misma logica de rutas y funciones

**Contenido de `webapp/__init__.py`:**
```python
"""
Aplicacion web Flask para visualizacion de datos del termostato.
"""
import os
from datetime import datetime

from flask import Flask, render_template, jsonify, request
from flask_bootstrap import Bootstrap
from flask_moment import Moment
import requests

from .forms import TermostatoForm  # Import relativo

# Configuracion de la aplicacion
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave-desarrollo-local')

# ... resto del codigo de lanzador.py ...
```

---

## Paso 5: Crear app.py como punto de entrada

**Acciones:**
1. Crear `app.py` en la raiz
2. Importar app desde webapp
3. Configurar ejecucion para desarrollo

**Contenido de `app.py`:**
```python
"""
Punto de entrada de la aplicacion.
- Desarrollo: python app.py
- Produccion: gunicorn app:app
"""
from webapp import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
```

---

## Paso 6: Eliminar lanzador.py

**Acciones:**
1. Eliminar `lanzador.py` (ya migrado a webapp/__init__.py)

**Comandos:**
```bash
rm lanzador.py
```

---

## Paso 7: Actualizar tests

**Acciones:**
1. Actualizar imports en `tests/test_lanzador.py`
2. Renombrar a `tests/test_app.py` (opcional pero recomendado)
3. Cambiar `from lanzador import app` a `from webapp import app`
4. Actualizar mocks de `lanzador.requests.get` a `webapp.requests.get`

**Cambios en tests:**
```python
# Antes
from lanzador import app
@patch('lanzador.requests.get')

# Despues
from webapp import app
@patch('webapp.requests.get')
```

---

## Paso 8: Actualizar pytest.ini

**Acciones:**
1. Actualizar `--cov=lanzador` a `--cov=webapp`

**Contenido actualizado:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=webapp --cov-report=term-missing
filterwarnings =
    ignore::DeprecationWarning
```

---

## Paso 9: Actualizar CLAUDE.md

**Acciones:**
1. Actualizar comando de ejecucion: `python app.py`
2. Actualizar comando gunicorn: `gunicorn app:app`
3. Actualizar estructura de archivos en documentacion

---

## Paso 10: Actualizar scripts de quality

**Acciones:**
1. Verificar que los scripts de quality funcionen con la nueva estructura
2. Actualizar paths si es necesario

---

## Paso 11: Verificar funcionamiento

**Acciones:**
1. Ejecutar la aplicacion: `python app.py`
2. Ejecutar tests: `pytest`
3. Ejecutar quality check: `/quality-check`
4. Verificar que todo funciona correctamente

**Comandos de verificacion:**
```bash
python app.py &
curl http://localhost:5001/
pytest
python quality/scripts/calculate_metrics.py webapp/
python quality/scripts/calculate_web_metrics.py .
```

---

## Paso 12: Commit final

**Acciones:**
1. Agregar todos los cambios
2. Commit con mensaje descriptivo

**Mensaje de commit sugerido:**
```
Refactor: Reorganizar estructura del proyecto

- Crear carpeta webapp/ con la aplicacion Flask
- Renombrar lanzador.py a app.py (punto de entrada estandar)
- Mover templates/, static/, forms.py a webapp/
- Actualizar imports en tests
- Actualizar configuracion pytest y documentacion
```

---

## Rollback

Si algo falla, revertir con:
```bash
git checkout -- .
git clean -fd
```

---

## Checklist Final

- [ ] Paso 1: Crear estructura webapp/
- [ ] Paso 2: Mover templates y static
- [ ] Paso 3: Mover forms.py
- [ ] Paso 4: Crear webapp/__init__.py
- [ ] Paso 5: Crear app.py
- [ ] Paso 6: Eliminar lanzador.py
- [ ] Paso 7: Actualizar tests
- [ ] Paso 8: Actualizar pytest.ini
- [ ] Paso 9: Actualizar CLAUDE.md
- [ ] Paso 10: Verificar scripts quality
- [ ] Paso 11: Verificar funcionamiento
- [ ] Paso 12: Commit final

---

*Plan creado el 2025-12-26*
