#!/usr/bin/env python3
"""
Valida quality gates basado en metricas calculadas.
Retorna codigo de salida 0 si todos los gates pasan, 1 si alguno falla.

Autor: Ambiente Agentico - webapp_termostato
"""

import json
import sys
from pathlib import Path


def cargar_metricas(archivo_metricas):
    """Carga metricas desde archivo JSON."""
    with open(archivo_metricas, 'r') as f:
        return json.load(f)


def validar_gates(metricas):
    """Valida todos los quality gates."""

    resumen = metricas.get("resumen", {})
    gates = resumen.get("quality_gates", {})

    print("Validando Quality Gates...")
    print("="*60)

    todos_pasaron = True

    for nombre_gate, datos_gate in gates.items():
        estado = datos_gate["estado"]
        valor = datos_gate["valor"]
        umbral = datos_gate["umbral"]

        if estado == "PASS":
            print(f"[PASS] {nombre_gate.upper()}")
            print(f"       Valor: {valor}, Umbral: {umbral}")
        else:
            print(f"[FAIL] {nombre_gate.upper()}")
            print(f"       Valor: {valor}, Umbral: {umbral}")
            todos_pasaron = False

        print()

    print("="*60)

    if todos_pasaron:
        print("[OK] TODOS LOS QUALITY GATES PASARON!")
        return 0
    else:
        print("[FAIL] ALGUNOS QUALITY GATES FALLARON!")
        print("\nPor favor corrija los issues antes de hacer commit.")
        return 1


def mostrar_recomendaciones(metricas):
    """Muestra recomendaciones basadas en gates fallidos."""

    resumen = metricas.get("resumen", {})
    gates = resumen.get("quality_gates", {})

    gates_fallidos = [nombre for nombre, datos in gates.items() if datos["estado"] == "FAIL"]

    if not gates_fallidos:
        return

    print("\nRecomendaciones:")
    print("-"*60)

    for gate in gates_fallidos:
        datos = gates[gate]

        if gate == "complejidad":
            print(f"\n[COMPLEJIDAD] CC promedio ({datos['valor']}) excede umbral ({datos['umbral']})")
            print("  Acciones sugeridas:")
            print(f"  1. Revisar funcion con mayor CC: {metricas['complejidad']['ubicacion_maximo']}")
            print("  2. Extraer condiciones complejas en funciones separadas")
            print("  3. Considerar aplicar patron Strategy para logica de branching")

        elif gate == "mantenibilidad":
            print(f"\n[MANTENIBILIDAD] MI promedio ({datos['valor']}) bajo umbral ({datos['umbral']})")
            print("  Acciones sugeridas:")
            print(f"  1. Revisar modulo: {metricas['mantenibilidad']['archivo_minimo']}")
            print("  2. Dividir modulos grandes en unidades mas pequenias")
            print("  3. Reducir dependencias entre modulos")
            print("  4. Mejorar documentacion y comentarios")

        elif gate == "pylint":
            print(f"\n[PYLINT] Score ({datos['valor']}) bajo umbral ({datos['umbral']})")
            print("  Acciones sugeridas:")
            print(f"  1. Corregir {metricas['pylint']['errores']} error(es)")
            print(f"  2. Atender {metricas['pylint']['warnings']} warning(s)")
            print("  3. Ejecutar: pylint --list-msgs para entender violaciones")
            print("  4. Ejecutar: autopep8 --in-place <archivo> para auto-corregir estilo")

    print("\n" + "-"*60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python validate_gates.py <archivo_metricas.json>")
        print("\nEjemplo:")
        print("  python validate_gates.py quality/reports/quality_20251219_143022.json")
        sys.exit(2)

    archivo_metricas = sys.argv[1]

    if not Path(archivo_metricas).exists():
        print(f"Error: Archivo de metricas no encontrado: {archivo_metricas}")
        sys.exit(2)

    metricas = cargar_metricas(archivo_metricas)
    codigo_salida = validar_gates(metricas)

    if codigo_salida != 0:
        mostrar_recomendaciones(metricas)

    sys.exit(codigo_salida)
