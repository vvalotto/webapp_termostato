#!/usr/bin/env python3
"""
Genera reporte Markdown legible a partir de metricas JSON.

Autor: Ambiente Agentico - webapp_termostato
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def generar_reporte_markdown(metricas):
    """Genera reporte detallado en Markdown."""

    resumen = metricas.get("resumen", {})
    gates = resumen.get("quality_gates", {})

    # Calcular porcentajes de distribucion de complejidad
    total_funciones = metricas["complejidad"]["total_funciones"]
    distribucion = metricas["complejidad"]["distribucion"]

    def porcentaje(valor):
        return round(valor / total_funciones * 100, 1) if total_funciones > 0 else 0

    reporte = f"""# Reporte de Calidad de Codigo

**Proyecto:** webapp_termostato
**Fecha:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Objetivo Analizado:** `{metricas['objetivo']}`
**Grado General:** {resumen['grado']}

---

## Resumen Ejecutivo

| Metrica | Valor |
|---------|-------|
| Quality Gates Pasados | {resumen['gates_pasados']}/{resumen['gates_totales']} |
| Issues Bloqueantes | {resumen['issues_bloqueantes']} |
| Grado General | {resumen['grado']} |

---

## Metricas de Tamanio

| Metrica | Valor |
|---------|-------|
| Total LOC | {metricas['tamanio']['loc']} |
| Source LOC | {metricas['tamanio']['sloc']} |
| Comentarios | {metricas['tamanio']['comentarios']} ({metricas['tamanio']['ratio_comentarios']}%) |
| Lineas en Blanco | {metricas['tamanio']['lineas_blanco']} |

---

## Analisis de Complejidad

| Metrica | Valor |
|---------|-------|
| CC Promedio | {metricas['complejidad']['promedio']} |
| CC Maximo | {metricas['complejidad']['maximo']} |
| Ubicacion Maximo | `{metricas['complejidad']['ubicacion_maximo']}` |
| Total Funciones | {total_funciones} |

### Distribucion por Grado

| Grado | Rango CC | Cantidad | Porcentaje |
|-------|----------|----------|------------|
| A | 1-5 | {distribucion['A']} | {porcentaje(distribucion['A'])}% |
| B | 6-10 | {distribucion['B']} | {porcentaje(distribucion['B'])}% |
| C | 11-20 | {distribucion['C']} | {porcentaje(distribucion['C'])}% |
| D | 21-30 | {distribucion['D']} | {porcentaje(distribucion['D'])}% |
| E | 31-40 | {distribucion['E']} | {porcentaje(distribucion['E'])}% |
| F | 41+ | {distribucion['F']} | {porcentaje(distribucion['F'])}% |

---

## Indice de Mantenibilidad

| Metrica | Valor |
|---------|-------|
| MI Promedio | {metricas['mantenibilidad']['promedio']} |
| MI Minimo | {metricas['mantenibilidad']['minimo']} |
| Archivo con MI Minimo | `{metricas['mantenibilidad']['archivo_minimo']}` |
| Modulos bajo umbral (< 20) | {metricas['mantenibilidad']['cantidad_bajo_umbral']} |

---

## Analisis Pylint

| Metrica | Valor |
|---------|-------|
| Score | {metricas['pylint']['score']}/10.0 |
| Errores | {metricas['pylint']['errores']} |
| Warnings | {metricas['pylint']['warnings']} |
| Sugerencias Refactor | {metricas['pylint']['refactor']} |
| Convenciones | {metricas['pylint']['convencion']} |
| Total Mensajes | {metricas['pylint']['total_mensajes']} |

---

## Estado de Quality Gates

| Gate | Estado | Valor | Umbral |
|------|--------|-------|--------|
"""

    for nombre_gate, datos_gate in gates.items():
        estado = datos_gate["estado"]
        valor = datos_gate["valor"]
        umbral = datos_gate["umbral"]
        icono = "[PASS]" if estado == "PASS" else "[FAIL]"
        reporte += f"| {nombre_gate.title()} | {icono} | {valor} | {umbral} |\n"

    reporte += """
---

## Recomendaciones

"""

    # Generar recomendaciones basadas en gates fallidos
    bloqueantes = resumen['issues_bloqueantes']

    if bloqueantes == 0:
        reporte += """[OK] **No hay issues bloqueantes.** El codigo cumple con todos los estandares de calidad.

**Sugerencias de mejora continua:**
- Mantener monitoreo de metricas en futuros commits
- Considerar aumentar cobertura de tests
- Documentar algoritmos complejos
"""
    else:
        reporte += f"""[ALERTA] **{bloqueantes} issue(s) bloqueante(s) detectado(s).**

Por favor corregir antes de hacer commit:

"""
        for nombre_gate, datos_gate in gates.items():
            if datos_gate["estado"] == "FAIL":
                if nombre_gate == "complejidad":
                    reporte += f"""### Complejidad Ciclomatica

**Problema:** CC promedio ({datos_gate['valor']}) excede umbral ({datos_gate['umbral']})

**Acciones:**
1. Refactorizar funcion: `{metricas['complejidad']['ubicacion_maximo']}`
2. Extraer condiciones complejas en funciones separadas
3. Aplicar patron Strategy para logica de branching

"""
                elif nombre_gate == "mantenibilidad":
                    reporte += f"""### Indice de Mantenibilidad

**Problema:** MI promedio ({datos_gate['valor']}) bajo umbral ({datos_gate['umbral']})

**Acciones:**
1. Revisar modulo: `{metricas['mantenibilidad']['archivo_minimo']}`
2. Dividir modulos grandes en unidades mas pequenias
3. Reducir dependencias entre modulos
4. Mejorar documentacion y comentarios

"""
                elif nombre_gate == "pylint":
                    reporte += f"""### Pylint Score

**Problema:** Score ({datos_gate['valor']}) bajo umbral ({datos_gate['umbral']})

**Acciones:**
1. Corregir {metricas['pylint']['errores']} error(es)
2. Atender {metricas['pylint']['warnings']} warning(s)
3. Ejecutar: `pylint <archivo> --list-msgs` para detalles
4. Ejecutar: `autopep8 --in-place <archivo>` para auto-corregir estilo

"""

    reporte += f"""---

## Metadata del Reporte

| Campo | Valor |
|-------|-------|
| Timestamp | {metricas['timestamp']} |
| Generado | {datetime.now().isoformat()} |
| Herramienta | quality-agent (webapp_termostato) |

---

*Reporte generado automaticamente por el ambiente agentico de calidad.*
"""

    return reporte


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python generate_report.py <metricas.json>")
        print("\nEjemplo:")
        print("  python generate_report.py quality/reports/quality_20251219_143022.json")
        sys.exit(1)

    archivo_metricas = sys.argv[1]

    if not Path(archivo_metricas).exists():
        print(f"Error: Archivo no encontrado: {archivo_metricas}")
        sys.exit(1)

    with open(archivo_metricas, 'r') as f:
        metricas = json.load(f)

    # Generar reporte
    reporte = generar_reporte_markdown(metricas)

    # Guardar a archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_reporte = f"quality/reports/quality_report_{timestamp}.md"

    # Crear directorio si no existe
    Path(archivo_reporte).parent.mkdir(parents=True, exist_ok=True)

    with open(archivo_reporte, 'w') as f:
        f.write(reporte)

    print(f"Reporte generado: {archivo_reporte}")
    print("\n" + "="*60)
    print(reporte)
