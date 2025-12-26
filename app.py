"""
Punto de entrada de la aplicacion webapp_termostato.

Uso:
- Desarrollo: python app.py
- Produccion: gunicorn app:app
"""
from webapp import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
