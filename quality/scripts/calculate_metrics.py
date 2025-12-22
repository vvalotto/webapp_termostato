#!/usr/bin/env python3
"""
Calcula metricas esenciales de calidad de codigo para proyectos Python.
Genera salida JSON con datos de metricas.

Metricas medidas:
- LOC/SLOC: Lineas de codigo
- CC: Complejidad Ciclomatica
- MI: Indice de Mantenibilidad
- Pylint Score: Calidad general

Autor: Ambiente Agentico - webapp_termostato
"""

import json
import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime


class CalculadorMetricas:
    """Calcula metricas de calidad de codigo usando radon y pylint."""

    def __init__(self, ruta_objetivo="."):
        self.ruta_objetivo = Path(ruta_objetivo)
        self.metricas = {
            "timestamp": datetime.now().isoformat(),
            "objetivo": str(self.ruta_objetivo),
            "tamanio": {},
            "complejidad": {},
            "mantenibilidad": {},
            "pylint": {},
            "resumen": {}
        }

    def calcular_metricas_tamanio(self):
        """Calcula LOC, SLOC usando radon raw."""
        try:
            resultado = subprocess.run(
                ["radon", "raw", str(self.ruta_objetivo), "-s", "-j"],
                capture_output=True,
                text=True,
                check=True
            )

            datos_raw = json.loads(resultado.stdout)

            # Agregar metricas
            total_loc = 0
            total_sloc = 0
            total_comentarios = 0
            total_blancos = 0

            for ruta_archivo, datos in datos_raw.items():
                total_loc += datos.get("loc", 0)
                total_sloc += datos.get("sloc", 0)
                total_comentarios += datos.get("comments", 0)
                total_blancos += datos.get("blank", 0)

            self.metricas["tamanio"] = {
                "loc": total_loc,
                "sloc": total_sloc,
                "comentarios": total_comentarios,
                "lineas_blanco": total_blancos,
                "ratio_comentarios": round(total_comentarios / total_loc * 100, 2) if total_loc > 0 else 0
            }

            return True

        except subprocess.CalledProcessError as e:
            print(f"Error calculando metricas de tamanio: {e}", file=sys.stderr)
            return False
        except json.JSONDecodeError as e:
            print(f"Error parseando salida de radon: {e}", file=sys.stderr)
            return False

    def calcular_metricas_complejidad(self):
        """Calcula Complejidad Ciclomatica usando radon cc."""
        try:
            resultado = subprocess.run(
                ["radon", "cc", str(self.ruta_objetivo), "-a", "-s", "-j"],
                capture_output=True,
                text=True,
                check=True
            )

            datos_cc = json.loads(resultado.stdout)

            # Agregar complejidad
            todas_complejidades = []
            max_cc = 0
            funcion_max_cc = None

            # Distribucion por grado
            distribucion = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0}

            for ruta_archivo, funciones in datos_cc.items():
                for func in funciones:
                    cc = func.get("complexity", 0)
                    todas_complejidades.append(cc)

                    if cc > max_cc:
                        max_cc = cc
                        funcion_max_cc = f"{ruta_archivo}:{func.get('lineno')} {func.get('name')}"

                    # Distribucion por grado
                    grado = func.get("rank", "F")
                    if grado in distribucion:
                        distribucion[grado] += 1

            promedio_cc = sum(todas_complejidades) / len(todas_complejidades) if todas_complejidades else 0

            self.metricas["complejidad"] = {
                "promedio": round(promedio_cc, 2),
                "maximo": max_cc,
                "ubicacion_maximo": funcion_max_cc,
                "total_funciones": len(todas_complejidades),
                "distribucion": distribucion
            }

            return True

        except subprocess.CalledProcessError as e:
            print(f"Error calculando complejidad: {e}", file=sys.stderr)
            return False
        except json.JSONDecodeError as e:
            print(f"Error parseando salida de radon cc: {e}", file=sys.stderr)
            return False

    def calcular_indice_mantenibilidad(self):
        """Calcula Indice de Mantenibilidad usando radon mi."""
        try:
            resultado = subprocess.run(
                ["radon", "mi", str(self.ruta_objetivo), "-s", "-j"],
                capture_output=True,
                text=True,
                check=True
            )

            datos_mi = json.loads(resultado.stdout)

            # Agregar MI
            todos_mi = []
            min_mi = 100
            archivo_min_mi = None

            for ruta_archivo, datos in datos_mi.items():
                mi = datos.get("mi", 0)
                todos_mi.append(mi)

                if mi < min_mi:
                    min_mi = mi
                    archivo_min_mi = ruta_archivo

            promedio_mi = sum(todos_mi) / len(todos_mi) if todos_mi else 0

            # Contar modulos bajo umbral
            bajo_umbral = sum(1 for mi in todos_mi if mi < 20)

            self.metricas["mantenibilidad"] = {
                "promedio": round(promedio_mi, 2),
                "minimo": round(min_mi, 2),
                "archivo_minimo": archivo_min_mi,
                "cantidad_bajo_umbral": bajo_umbral
            }

            return True

        except subprocess.CalledProcessError as e:
            print(f"Error calculando MI: {e}", file=sys.stderr)
            return False
        except json.JSONDecodeError as e:
            print(f"Error parseando salida de radon mi: {e}", file=sys.stderr)
            return False

    def calcular_pylint_score(self):
        """Calcula score de Pylint."""
        try:
            # Ejecutar pylint para obtener mensajes en JSON
            resultado_json = subprocess.run(
                ["pylint", str(self.ruta_objetivo), "--output-format=json"],
                capture_output=True,
                text=True
            )

            # Pylint retorna non-zero incluso con warnings, no usar check=True

            # Parsear salida JSON
            mensajes = json.loads(resultado_json.stdout) if resultado_json.stdout else []

            # Ejecutar pylint nuevamente para obtener el score (sin JSON format)
            resultado_score = subprocess.run(
                ["pylint", str(self.ruta_objetivo), "--score=yes"],
                capture_output=True,
                text=True
            )

            # Extraer score de stdout (el score aparece en la salida normal)
            score = 0.0
            for linea in resultado_score.stdout.split('\n'):
                if 'rated at' in linea.lower():
                    match = re.search(r'(\d+\.\d+)/10', linea)
                    if match:
                        score = float(match.group(1))
                    break

            # Contar tipos de mensajes
            errores = sum(1 for msg in mensajes if msg.get("type") == "error")
            warnings = sum(1 for msg in mensajes if msg.get("type") == "warning")
            refactor = sum(1 for msg in mensajes if msg.get("type") == "refactor")
            convencion = sum(1 for msg in mensajes if msg.get("type") == "convention")

            self.metricas["pylint"] = {
                "score": score,
                "errores": errores,
                "warnings": warnings,
                "refactor": refactor,
                "convencion": convencion,
                "total_mensajes": len(mensajes)
            }

            return True

        except subprocess.CalledProcessError as e:
            print(f"Error ejecutando pylint: {e}", file=sys.stderr)
            return False
        except json.JSONDecodeError as e:
            print(f"Error parseando salida de pylint: {e}", file=sys.stderr)
            return False

    def generar_resumen(self):
        """Genera resumen ejecutivo con estado pass/fail."""

        # Quality gates desde .claude/settings.json (valores por defecto)
        gates = {
            "max_complejidad": 10,
            "min_mantenibilidad": 20,
            "min_pylint_score": 8.0
        }

        # Cargar gates desde settings si existe
        settings_path = Path(".claude/settings.json")
        if settings_path.exists():
            try:
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    qg = settings.get("quality_gates", {})
                    gates["max_complejidad"] = qg.get("max_complexity", 10)
                    gates["min_mantenibilidad"] = qg.get("min_maintainability", 20)
                    gates["min_pylint_score"] = qg.get("min_pylint_score", 8.0)
            except (json.JSONDecodeError, IOError):
                pass  # Usar valores por defecto

        # Verificar cada gate
        complejidad_ok = self.metricas["complejidad"]["promedio"] <= gates["max_complejidad"]
        mi_ok = self.metricas["mantenibilidad"]["promedio"] > gates["min_mantenibilidad"]
        pylint_ok = self.metricas["pylint"]["score"] >= gates["min_pylint_score"]

        pasados = sum([complejidad_ok, mi_ok, pylint_ok])

        # Grado general
        if pasados == 3:
            grado = "A"
        elif pasados == 2:
            grado = "B"
        elif pasados == 1:
            grado = "C"
        else:
            grado = "F"

        self.metricas["resumen"] = {
            "grado": grado,
            "gates_pasados": pasados,
            "gates_totales": 3,
            "issues_bloqueantes": 3 - pasados,
            "quality_gates": {
                "complejidad": {
                    "estado": "PASS" if complejidad_ok else "FAIL",
                    "valor": self.metricas["complejidad"]["promedio"],
                    "umbral": gates["max_complejidad"]
                },
                "mantenibilidad": {
                    "estado": "PASS" if mi_ok else "FAIL",
                    "valor": self.metricas["mantenibilidad"]["promedio"],
                    "umbral": gates["min_mantenibilidad"]
                },
                "pylint": {
                    "estado": "PASS" if pylint_ok else "FAIL",
                    "valor": self.metricas["pylint"]["score"],
                    "umbral": gates["min_pylint_score"]
                }
            }
        }

    def ejecutar_todo(self):
        """Ejecuta todos los calculos de metricas."""
        exito = True

        print("Calculando metricas de calidad de codigo...")
        print(f"Objetivo: {self.ruta_objetivo}\n")

        print("1/4 Calculando metricas de tamanio...", end=" ")
        if self.calcular_metricas_tamanio():
            print("[OK]")
        else:
            print("[ERROR]")
            exito = False

        print("2/4 Calculando complejidad...", end=" ")
        if self.calcular_metricas_complejidad():
            print("[OK]")
        else:
            print("[ERROR]")
            exito = False

        print("3/4 Calculando indice de mantenibilidad...", end=" ")
        if self.calcular_indice_mantenibilidad():
            print("[OK]")
        else:
            print("[ERROR]")
            exito = False

        print("4/4 Ejecutando analisis pylint...", end=" ")
        if self.calcular_pylint_score():
            print("[OK]")
        else:
            print("[ERROR]")
            exito = False

        if exito:
            self.generar_resumen()
            print("\n[OK] Todas las metricas calculadas exitosamente!")
        else:
            print("\n[WARN] Algunas metricas fallaron al calcular")

        return exito

    def guardar_json(self, ruta_salida):
        """Guarda metricas como JSON."""
        # Crear directorio si no existe
        Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)

        with open(ruta_salida, 'w') as f:
            json.dump(self.metricas, f, indent=2, ensure_ascii=False)
        print(f"\nMetricas guardadas en: {ruta_salida}")

    def imprimir_resumen(self):
        """Imprime resumen ejecutivo en consola."""
        resumen = self.metricas["resumen"]

        print("\n" + "="*60)
        print("RESUMEN DE METRICAS DE CALIDAD")
        print("="*60)

        print(f"\nGrado General: {resumen['grado']}")
        print(f"Quality Gates: {resumen['gates_pasados']}/{resumen['gates_totales']} pasaron")
        print(f"Issues Bloqueantes: {resumen['issues_bloqueantes']}")

        print("\nMetricas de Tamanio:")
        print(f"  - Total LOC: {self.metricas['tamanio']['loc']}")
        print(f"  - Source LOC: {self.metricas['tamanio']['sloc']}")
        print(f"  - Comentarios: {self.metricas['tamanio']['ratio_comentarios']}%")

        print("\nComplejidad:")
        print(f"  - CC Promedio: {self.metricas['complejidad']['promedio']}")
        print(f"  - CC Maximo: {self.metricas['complejidad']['maximo']} ({self.metricas['complejidad']['ubicacion_maximo']})")

        print("\nMantenibilidad:")
        print(f"  - MI Promedio: {self.metricas['mantenibilidad']['promedio']}")
        print(f"  - Modulos bajo umbral: {self.metricas['mantenibilidad']['cantidad_bajo_umbral']}")

        print("\nPylint:")
        print(f"  - Score: {self.metricas['pylint']['score']}/10.0")
        print(f"  - Errores: {self.metricas['pylint']['errores']}")
        print(f"  - Warnings: {self.metricas['pylint']['warnings']}")

        print("\nEstado de Quality Gates:")
        for gate, datos in resumen["quality_gates"].items():
            estado_icono = "[PASS]" if datos["estado"] == "PASS" else "[FAIL]"
            print(f"  {estado_icono} {gate.title()}: {datos['valor']} (umbral: {datos['umbral']})")

        print("\n" + "="*60)


if __name__ == "__main__":
    objetivo = sys.argv[1] if len(sys.argv) > 1 else "."

    calculador = CalculadorMetricas(objetivo)

    if calculador.ejecutar_todo():
        # Guardar JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_salida = f"quality/reports/quality_{timestamp}.json"
        calculador.guardar_json(archivo_salida)

        # Imprimir resumen
        calculador.imprimir_resumen()

        # Salir con codigo apropiado
        bloqueantes = calculador.metricas["resumen"]["issues_bloqueantes"]
        sys.exit(0 if bloqueantes == 0 else 1)
    else:
        print("\n[ERROR] Fallo al calcular metricas")
        sys.exit(2)
