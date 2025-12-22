#!/usr/bin/env python3
"""
Calculador de metricas de calidad para activos web (HTML, CSS, JavaScript).
Sigue el patron de calculate_metrics.py para integracion con el sistema existente.

Metricas medidas:
- HTML: Validacion con HTMLHint (errores, warnings)
- CSS: Linting con Stylelint (errores, warnings)
- JavaScript: Linting con ESLint (errores, warnings, complejidad)

Autor: Ambiente Agentico - webapp_termostato
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class CalculadorMetricasWeb:
    """Calcula metricas de calidad para activos web."""

    def __init__(self, ruta_objetivo="."):
        self.ruta_objetivo = Path(ruta_objetivo)
        self.metricas = {
            "timestamp": datetime.now().isoformat(),
            "objetivo": str(self.ruta_objetivo),
            "html": {},
            "css": {},
            "javascript": {},
            "resumen_web": {}
        }
        self.settings = self._cargar_settings()

    def _cargar_settings(self):
        """Carga configuracion de .claude/settings.json"""
        settings_path = self.ruta_objetivo / ".claude" / "settings.json"

        # Valores por defecto para quality gates web
        defaults = {
            "quality_gates_web": {
                "html": {
                    "max_errors": 0,
                    "max_warnings": 5
                },
                "css": {
                    "max_errors": 0,
                    "max_warnings": 10
                },
                "javascript": {
                    "max_errors": 0,
                    "max_warnings": 10,
                    "max_complexity": 10
                }
            }
        }

        if settings_path.exists():
            try:
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    # Merge con defaults
                    if "quality_gates_web" in settings:
                        defaults["quality_gates_web"].update(settings["quality_gates_web"])
                    return defaults
            except (json.JSONDecodeError, IOError):
                pass

        return defaults

    def verificar_dependencias(self):
        """Verifica que npm y los linters esten instalados."""
        print("Verificando dependencias npm...")

        # Verificar que npm existe
        try:
            subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                check=True,
                cwd=str(self.ruta_objetivo)
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[ERROR] npm no esta instalado")
            return False

        # Verificar que node_modules existe
        node_modules = self.ruta_objetivo / "node_modules"
        if not node_modules.exists():
            print("[WARN] node_modules no existe. Ejecutando npm install...")
            try:
                subprocess.run(
                    ["npm", "install"],
                    capture_output=True,
                    check=True,
                    cwd=str(self.ruta_objetivo)
                )
                print("[OK] Dependencias instaladas")
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Fallo npm install: {e}")
                return False

        # Verificar linters
        linters = ["htmlhint", "stylelint", "eslint"]
        for linter in linters:
            linter_path = node_modules / ".bin" / linter
            if not linter_path.exists():
                print(f"[ERROR] {linter} no esta instalado")
                return False

        print("[OK] Todas las dependencias disponibles\n")
        return True

    def calcular_metricas_html(self):
        """Ejecuta htmlhint y procesa resultados."""
        print("Analizando archivos HTML con HTMLHint...", end=" ")

        templates_dir = self.ruta_objetivo / "templates"
        if not templates_dir.exists():
            print("[SKIP] No existe directorio templates/")
            self.metricas["html"] = {
                "archivos_analizados": 0,
                "errores": 0,
                "warnings": 0,
                "detalle": []
            }
            return True

        try:
            # Buscar archivos HTML
            html_files = list(templates_dir.glob("**/*.html"))
            if not html_files:
                print("[SKIP] No hay archivos HTML")
                self.metricas["html"] = {
                    "archivos_analizados": 0,
                    "errores": 0,
                    "warnings": 0,
                    "detalle": []
                }
                return True

            # Ejecutar htmlhint
            resultado = subprocess.run(
                ["npx", "htmlhint", str(templates_dir / "**/*.html"), "--format", "json"],
                capture_output=True,
                text=True,
                cwd=str(self.ruta_objetivo)
            )

            # HTMLHint retorna salida JSON en stdout
            errores = 0
            warnings = 0
            detalle = []

            if resultado.stdout.strip():
                try:
                    datos = json.loads(resultado.stdout)
                    for archivo_info in datos:
                        for mensaje in archivo_info.get("messages", []):
                            if mensaje.get("type") == "error":
                                errores += 1
                            else:
                                warnings += 1

                            detalle.append({
                                "archivo": archivo_info.get("file", ""),
                                "linea": mensaje.get("line", 0),
                                "columna": mensaje.get("col", 0),
                                "tipo": mensaje.get("type", "warning"),
                                "regla": mensaje.get("rule", {}).get("id", ""),
                                "mensaje": mensaje.get("message", "")
                            })
                except json.JSONDecodeError:
                    # Si no hay errores, htmlhint puede no retornar JSON valido
                    pass

            self.metricas["html"] = {
                "archivos_analizados": len(html_files),
                "errores": errores,
                "warnings": warnings,
                "detalle": detalle
            }

            print(f"[OK] {len(html_files)} archivos, {errores} errores, {warnings} warnings")
            return True

        except subprocess.CalledProcessError as e:
            print(f"[ERROR] {e}")
            return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

    def calcular_metricas_css(self):
        """Ejecuta stylelint y procesa resultados."""
        print("Analizando archivos CSS con Stylelint...", end=" ")

        static_dir = self.ruta_objetivo / "static"
        if not static_dir.exists():
            print("[SKIP] No existe directorio static/")
            self.metricas["css"] = {
                "archivos_analizados": 0,
                "errores": 0,
                "warnings": 0,
                "detalle": []
            }
            return True

        try:
            # Buscar archivos CSS
            css_files = list(static_dir.glob("**/*.css"))
            if not css_files:
                print("[SKIP] No hay archivos CSS")
                self.metricas["css"] = {
                    "archivos_analizados": 0,
                    "errores": 0,
                    "warnings": 0,
                    "detalle": []
                }
                return True

            # Ejecutar stylelint
            resultado = subprocess.run(
                ["npx", "stylelint", "static/**/*.css", "--formatter", "json"],
                capture_output=True,
                text=True,
                cwd=str(self.ruta_objetivo)
            )

            errores = 0
            warnings = 0
            detalle = []

            if resultado.stdout.strip():
                try:
                    datos = json.loads(resultado.stdout)
                    for archivo_info in datos:
                        for warning in archivo_info.get("warnings", []):
                            severity = warning.get("severity", "warning")
                            if severity == "error":
                                errores += 1
                            else:
                                warnings += 1

                            detalle.append({
                                "archivo": archivo_info.get("source", ""),
                                "linea": warning.get("line", 0),
                                "columna": warning.get("column", 0),
                                "tipo": severity,
                                "regla": warning.get("rule", ""),
                                "mensaje": warning.get("text", "")
                            })
                except json.JSONDecodeError:
                    pass

            self.metricas["css"] = {
                "archivos_analizados": len(css_files),
                "errores": errores,
                "warnings": warnings,
                "detalle": detalle
            }

            print(f"[OK] {len(css_files)} archivos, {errores} errores, {warnings} warnings")
            return True

        except subprocess.CalledProcessError as e:
            print(f"[ERROR] {e}")
            return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

    def calcular_metricas_javascript(self):
        """Ejecuta eslint y procesa resultados."""
        print("Analizando archivos JavaScript con ESLint...", end=" ")

        static_dir = self.ruta_objetivo / "static"
        if not static_dir.exists():
            print("[SKIP] No existe directorio static/")
            self.metricas["javascript"] = {
                "archivos_analizados": 0,
                "errores": 0,
                "warnings": 0,
                "complejidad_maxima": 0,
                "detalle": []
            }
            return True

        try:
            # Buscar archivos JS
            js_files = list(static_dir.glob("**/*.js"))
            if not js_files:
                print("[SKIP] No hay archivos JavaScript")
                self.metricas["javascript"] = {
                    "archivos_analizados": 0,
                    "errores": 0,
                    "warnings": 0,
                    "complejidad_maxima": 0,
                    "detalle": []
                }
                return True

            # Ejecutar eslint
            resultado = subprocess.run(
                ["npx", "eslint", "static/**/*.js", "--format", "json"],
                capture_output=True,
                text=True,
                cwd=str(self.ruta_objetivo)
            )

            errores = 0
            warnings = 0
            complejidad_maxima = 0
            detalle = []

            if resultado.stdout.strip():
                try:
                    datos = json.loads(resultado.stdout)
                    for archivo_info in datos:
                        errores += archivo_info.get("errorCount", 0)
                        warnings += archivo_info.get("warningCount", 0)

                        for mensaje in archivo_info.get("messages", []):
                            # Detectar regla de complejidad
                            if mensaje.get("ruleId") == "complexity":
                                # Extraer valor de complejidad del mensaje
                                msg_text = mensaje.get("message", "")
                                import re
                                match = re.search(r'complexity of (\d+)', msg_text)
                                if match:
                                    cc = int(match.group(1))
                                    if cc > complejidad_maxima:
                                        complejidad_maxima = cc

                            detalle.append({
                                "archivo": archivo_info.get("filePath", ""),
                                "linea": mensaje.get("line", 0),
                                "columna": mensaje.get("column", 0),
                                "tipo": "error" if mensaje.get("severity") == 2 else "warning",
                                "regla": mensaje.get("ruleId", ""),
                                "mensaje": mensaje.get("message", "")
                            })
                except json.JSONDecodeError:
                    pass

            self.metricas["javascript"] = {
                "archivos_analizados": len(js_files),
                "errores": errores,
                "warnings": warnings,
                "complejidad_maxima": complejidad_maxima,
                "detalle": detalle
            }

            print(f"[OK] {len(js_files)} archivos, {errores} errores, {warnings} warnings, CC max: {complejidad_maxima}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"[ERROR] {e}")
            return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

    def generar_resumen_web(self):
        """Genera resumen con estado PASS/FAIL para cada gate."""
        gates = self.settings["quality_gates_web"]

        # Evaluar HTML
        html_errores_ok = self.metricas["html"]["errores"] <= gates["html"]["max_errors"]
        html_warnings_ok = self.metricas["html"]["warnings"] <= gates["html"]["max_warnings"]
        html_pass = html_errores_ok  # Solo errores bloquean

        # Evaluar CSS
        css_errores_ok = self.metricas["css"]["errores"] <= gates["css"]["max_errors"]
        css_warnings_ok = self.metricas["css"]["warnings"] <= gates["css"]["max_warnings"]
        css_pass = css_errores_ok  # Solo errores bloquean

        # Evaluar JavaScript
        js_errores_ok = self.metricas["javascript"]["errores"] <= gates["javascript"]["max_errors"]
        js_complejidad_ok = self.metricas["javascript"]["complejidad_maxima"] <= gates["javascript"]["max_complexity"]
        js_pass = js_errores_ok and js_complejidad_ok  # Errores y complejidad bloquean

        gates_pasados = sum([html_pass, css_pass, js_pass])
        gates_totales = 3

        # Calcular grado
        if gates_pasados == 3:
            grado = "A"
        elif gates_pasados == 2:
            grado = "B"
        elif gates_pasados == 1:
            grado = "C"
        else:
            grado = "F"

        self.metricas["resumen_web"] = {
            "grado": grado,
            "gates_pasados": gates_pasados,
            "gates_totales": gates_totales,
            "quality_gates": {
                "html": {
                    "estado": "PASS" if html_pass else "FAIL",
                    "errores": self.metricas["html"]["errores"],
                    "warnings": self.metricas["html"]["warnings"],
                    "umbral_errores": gates["html"]["max_errors"],
                    "umbral_warnings": gates["html"]["max_warnings"]
                },
                "css": {
                    "estado": "PASS" if css_pass else "FAIL",
                    "errores": self.metricas["css"]["errores"],
                    "warnings": self.metricas["css"]["warnings"],
                    "umbral_errores": gates["css"]["max_errors"],
                    "umbral_warnings": gates["css"]["max_warnings"]
                },
                "javascript": {
                    "estado": "PASS" if js_pass else "FAIL",
                    "errores": self.metricas["javascript"]["errores"],
                    "warnings": self.metricas["javascript"]["warnings"],
                    "complejidad_maxima": self.metricas["javascript"]["complejidad_maxima"],
                    "umbral_errores": gates["javascript"]["max_errors"],
                    "umbral_complejidad": gates["javascript"]["max_complexity"]
                }
            }
        }

    def ejecutar_todo(self):
        """Ejecuta todos los analisis."""
        exito = True

        print("="*60)
        print("ANALISIS DE CALIDAD WEB")
        print("="*60)
        print(f"Objetivo: {self.ruta_objetivo}\n")

        # HTML
        if not self.calcular_metricas_html():
            exito = False

        # CSS
        if not self.calcular_metricas_css():
            exito = False

        # JavaScript
        if not self.calcular_metricas_javascript():
            exito = False

        if exito:
            self.generar_resumen_web()
            print("\n[OK] Analisis web completado exitosamente!")
        else:
            print("\n[WARN] Algunos analisis fallaron")

        return exito

    def guardar_json(self):
        """Guarda metricas en quality/reports/quality_web_TIMESTAMP.json"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_salida = self.ruta_objetivo / "quality" / "reports" / f"quality_web_{timestamp}.json"

        # Crear directorio si no existe
        ruta_salida.parent.mkdir(parents=True, exist_ok=True)

        with open(ruta_salida, 'w') as f:
            json.dump(self.metricas, f, indent=2, ensure_ascii=False)

        print(f"\nMetricas guardadas en: {ruta_salida}")
        return str(ruta_salida)

    def imprimir_resumen(self):
        """Imprime resumen en consola."""
        resumen = self.metricas["resumen_web"]

        print("\n" + "="*60)
        print("RESUMEN DE CALIDAD WEB")
        print("="*60)

        print(f"\nGrado Web: {resumen['grado']}")
        print(f"Quality Gates: {resumen['gates_pasados']}/{resumen['gates_totales']} pasaron")

        # HTML
        html = self.metricas["html"]
        html_gate = resumen["quality_gates"]["html"]
        estado_html = "[PASS]" if html_gate["estado"] == "PASS" else "[FAIL]"
        print(f"\nHTML ({html['archivos_analizados']} archivos):")
        print(f"  {estado_html} Errores: {html['errores']} (umbral: {html_gate['umbral_errores']})")
        print(f"  Warnings: {html['warnings']} (umbral: {html_gate['umbral_warnings']})")

        # CSS
        css = self.metricas["css"]
        css_gate = resumen["quality_gates"]["css"]
        estado_css = "[PASS]" if css_gate["estado"] == "PASS" else "[FAIL]"
        print(f"\nCSS ({css['archivos_analizados']} archivos):")
        print(f"  {estado_css} Errores: {css['errores']} (umbral: {css_gate['umbral_errores']})")
        print(f"  Warnings: {css['warnings']} (umbral: {css_gate['umbral_warnings']})")

        # JavaScript
        js = self.metricas["javascript"]
        js_gate = resumen["quality_gates"]["javascript"]
        estado_js = "[PASS]" if js_gate["estado"] == "PASS" else "[FAIL]"
        print(f"\nJavaScript ({js['archivos_analizados']} archivos):")
        print(f"  {estado_js} Errores: {js['errores']} (umbral: {js_gate['umbral_errores']})")
        print(f"  Warnings: {js['warnings']}")
        print(f"  Complejidad max: {js['complejidad_maxima']} (umbral: {js_gate['umbral_complejidad']})")

        print("\n" + "="*60)


if __name__ == "__main__":
    ruta = sys.argv[1] if len(sys.argv) > 1 else "."
    calculador = CalculadorMetricasWeb(ruta)

    if not calculador.verificar_dependencias():
        print("\n[ERROR] Dependencias npm no instaladas. Ejecutar: npm install")
        sys.exit(2)

    exito = calculador.ejecutar_todo()
    calculador.guardar_json()
    calculador.imprimir_resumen()

    # Salir con codigo apropiado
    if exito:
        bloqueantes = 3 - calculador.metricas["resumen_web"]["gates_pasados"]
        sys.exit(0 if bloqueantes == 0 else 1)
    else:
        sys.exit(2)
