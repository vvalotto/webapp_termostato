#!/usr/bin/env python3
"""
Genera un reporte consolidado de calidad de código (Backend + Frontend)
y muestra la evolución histórica de las métricas.

Autor: Ambiente Agentico - webapp_termostato
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

def cargar_historial(directorio_reportes):
    """Carga y ordena todos los reportes JSON disponibles."""
    path = Path(directorio_reportes)
    if not path.exists():
        return [], []

    reportes_backend = []
    reportes_frontend = []

    # Buscar archivos JSON
    for archivo in path.glob("*.json"):
        try:
            with open(archivo, 'r') as f:
                datos = json.load(f)
                
                # Identificar tipo de reporte
                if "resumen_web" in datos:
                    reportes_frontend.append(datos)
                elif "resumen" in datos:
                    reportes_backend.append(datos)
        except (json.JSONDecodeError, IOError):
            continue

    # Ordenar por timestamp
    reportes_backend.sort(key=lambda x: x.get("timestamp", ""))
    reportes_frontend.sort(key=lambda x: x.get("timestamp", ""))

    return reportes_backend, reportes_frontend

def generar_tabla_evolucion_backend(historial):
    """Genera una tabla Markdown con la evolución del backend."""
    if not historial:
        return "_No hay historial de backend disponible._"

    tabla = "| Fecha | Grado | Pylint | CC Prom | MI Prom | LOC |\n"
    tabla += "|-------|-------|--------|---------|---------|-----|\n"

    for reporte in historial:
        fecha = datetime.fromisoformat(reporte["timestamp"]).strftime("%Y-%m-%d %H:%M")
        grado = reporte["resumen"]["grado"]
        pylint = reporte["pylint"]["score"]
        cc = reporte["complejidad"]["promedio"]
        mi = reporte["mantenibilidad"]["promedio"]
        loc = reporte["tamanio"]["loc"]

        tabla += f"| {fecha} | {grado} | {pylint} | {cc} | {mi} | {loc} |\n"

    return tabla

def generar_tabla_evolucion_frontend(historial):
    """Genera una tabla Markdown con la evolución del frontend."""
    if not historial:
        return "_No hay historial de frontend disponible._"

    tabla = "| Fecha | Grado | HTML Err | CSS Err | JS Err | JS CC Max |\n"
    tabla += "|-------|-------|----------|---------|--------|-----------|\n"

    for reporte in historial:
        fecha = datetime.fromisoformat(reporte["timestamp"]).strftime("%Y-%m-%d %H:%M")
        grado = reporte["resumen_web"]["grado"]
        html_err = reporte["html"]["errores"]
        css_err = reporte["css"]["errores"]
        js_err = reporte["javascript"]["errores"]
        js_cc = reporte["javascript"]["complejidad_maxima"]

        tabla += f"| {fecha} | {grado} | {html_err} | {css_err} | {js_err} | {js_cc} |\n"

    return tabla

def generar_seccion_actual_backend(ultimo_reporte):
    """Genera resumen del estado actual del backend."""
    if not ultimo_reporte:
        return "_No hay datos recientes de backend._"

    resumen = ultimo_reporte["resumen"]
    gates = resumen["quality_gates"]
    
    md = f"### Backend (Python)\n\n"
    md += f"- **Grado General:** {resumen['grado']}\n"
    md += f"- **Quality Gates:** {resumen['gates_pasados']}/{resumen['gates_totales']}\n\n"
    
    md += "| Métrica | Estado | Valor | Umbral |\n"
    md += "|---------|--------|-------|--------|\n"
    
    for gate, datos in gates.items():
        icono = "✅" if datos["estado"] == "PASS" else "❌"
        md += f"| {gate.title()} | {icono} | {datos['valor']} | {datos['umbral']} |\n"
        
    return md

def generar_seccion_actual_frontend(ultimo_reporte):
    """Genera resumen del estado actual del frontend."""
    if not ultimo_reporte:
        return "_No hay datos recientes de frontend._"

    resumen = ultimo_reporte["resumen_web"]
    gates = resumen["quality_gates"]
    
    md = f"### Frontend (Web)\n\n"
    md += f"- **Grado General:** {resumen['grado']}\n"
    md += f"- **Quality Gates:** {resumen['gates_pasados']}/{resumen['gates_totales']}\n\n"
    
    md += "| Métrica | Estado | Errores | Warnings |\n"
    md += "|---------|--------|---------|----------|\n"
    
    for gate, datos in gates.items():
        icono = "✅" if datos["estado"] == "PASS" else "❌"
        errores = datos.get("errores", 0)
        warnings = datos.get("warnings", 0)
        md += f"| {gate.upper()} | {icono} | {errores} | {warnings} |\n"
        
    return md

def generar_reporte_consolidado(dir_reportes):
    """Orquesta la generación del reporte completo."""
    backend_hist, frontend_hist = cargar_historial(dir_reportes)
    
    ultimo_backend = backend_hist[-1] if backend_hist else None
    ultimo_frontend = frontend_hist[-1] if frontend_hist else None
    
    fecha_reporte = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    md = f"# Reporte Consolidado de Calidad\n\n"
    md += f"**Fecha de Generación:** {fecha_reporte}\n\n"
    
    md += "## 1. Estado Actual del Proyecto\n\n"
    md += generar_seccion_actual_backend(ultimo_backend)
    md += "\n"
    md += generar_seccion_actual_frontend(ultimo_frontend)
    
    md += "\n## 2. Evolución Histórica\n\n"
    md += "### Evolución Backend\n"
    md += generar_tabla_evolucion_backend(backend_hist)
    md += "\n### Evolución Frontend\n"
    md += generar_tabla_evolucion_frontend(frontend_hist)
    
    md += "\n## 3. Conclusiones y Recomendaciones\n\n"
    
    # Análisis simple de tendencias
    if len(backend_hist) >= 2:
        prev = backend_hist[-2]["pylint"]["score"]
        curr = backend_hist[-1]["pylint"]["score"]
        diff = curr - prev
        if diff > 0:
            md += f"- 📈 La calidad del backend ha mejorado (+{diff:.2f} puntos Pylint).\n"
        elif diff < 0:
            md += f"- 📉 La calidad del backend ha disminuido ({diff:.2f} puntos Pylint).\n"
        else:
            md += "- ➡️ La calidad del backend se mantiene estable.\n"
            
    if len(frontend_hist) >= 2:
        prev_err = frontend_hist[-2]["javascript"]["errores"]
        curr_err = frontend_hist[-1]["javascript"]["errores"]
        if curr_err < prev_err:
            md += f"- 📈 Se han corregido errores de JavaScript ({prev_err} -> {curr_err}).\n"
        elif curr_err > prev_err:
            md += f"- 📉 Han aparecido nuevos errores de JavaScript ({prev_err} -> {curr_err}).\n"

    md += "\n---\n*Generado automáticamente por Quality Agent*"
    
    return md

if __name__ == "__main__":
    directorio = "quality/reports"
    if len(sys.argv) > 1:
        directorio = sys.argv[1]
        
    reporte_md = generar_reporte_consolidado(directorio)
    
    # Guardar reporte
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_salida = f"{directorio}/consolidated_report_{timestamp}.md"
    
    # Asegurar que existe el directorio
    Path(archivo_salida).parent.mkdir(parents=True, exist_ok=True)
    
    with open(archivo_salida, 'w') as f:
        f.write(reporte_md)
        
    print(f"Reporte consolidado generado: {archivo_salida}")
    print("\n" + "="*60 + "\n")
    print(reporte_md)
