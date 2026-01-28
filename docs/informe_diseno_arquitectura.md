# Informe de Calidad de Diseño y Arquitectura
**Proyecto:** WebApp Termostato
**Fecha:** 28 de Enero de 2026
**Enfoque:** Principios de Diseño y Métricas de Arquitectura Limpia (Robert C. Martin)

---

## 1. Calidad de Diseño

### 1.1 Cohesión y Acoplamiento

El análisis se centra en el módulo principal `webapp`.

*   **Cohesión (Nivel: Bajo/Medio):**
    *   ⚠️ **Problema Detectado:** El archivo `webapp/__init__.py` actúa como un "God Object" a pequeña escala. Agrupa responsabilidades dispares: configuración de la app, definición de rutas HTTP, lógica de obtención de datos (API calls) y gestión de caché en memoria.
    *   ✅ **Punto Positivo:** El módulo `forms.py` tiene alta cohesión; se encarga exclusivamente de la definición de esquemas de formularios.
    *   ✅ **Punto Positivo:** El Frontend (JS) ha sido refactorizado recientemente (WT-23) logrando una alta cohesión funcional (módulos separados para `api`, `graficas`, `ui`).

*   **Acoplamiento (Nivel: Alto):**
    *   ⚠️ **Acoplamiento Lógico:** Las vistas (`routes`) están fuertemente acopladas a la implementación de la API externa. Si la API cambia su firma, hay que modificar directamente la capa de presentación.
    *   **Acoplamiento de Librerías:** Existe una dependencia directa y estática de `requests` dentro de los controladores.

### 1.2 Principios SOLID

Evaluación del cumplimiento de los principios en el código Python (Backend).

1.  **SRP (Single Responsibility Principle):** ❌ **Violación**
    *   *Evidencia:* La función `obtener_estado_termostato()` en `__init__.py` mezcla la lógica de red (HTTP request), la lógica de negocio (validación de respuesta) y la lógica de estado (caché global).
    *   *Impacto:* Dificultad para testear la lógica de caché sin realizar peticiones HTTP reales.

2.  **OCP (Open/Closed Principle):** ⚠️ **Riesgo**
    *   *Evidencia:* Para agregar una nueva fuente de datos (ej. un segundo termostato o un sensor mock para tests), sería necesario modificar el código existente en lugar de extenderlo.

3.  **LSP (Liskov Substitution Principle):** N/A
    *   No hay jerarquías de herencia complejas en el backend actual.

4.  **ISP (Interface Segregation Principle):** N/A
    *   Python es dinámico, pero conceptualmente los clientes (vistas) consumen todo el objeto de datos devuelto por la API, lo cual es aceptable en este alcance.

5.  **DIP (Dependency Inversion Principle):** ❌ **Violación**
    *   *Evidencia:* Los módulos de alto nivel (Vistas de Flask) dependen de módulos de bajo nivel (Librería `requests` y endpoints específicos). No dependen de abstracciones (Interfaces/Protocolos).

---

## 2. Métricas de Arquitectura (Robert C. Martin)

Se analiza el paquete `webapp` como el componente central del sistema.

### 2.1 Definiciones
*   **Ca (Afferent Coupling):** Quién depende de mí.
*   **Ce (Efferent Coupling):** De quién dependo yo.
*   **I (Instability):** $I = Ce / (Ca + Ce)$. Rango [0, 1]. 0=Estable, 1=Inestable.
*   **A (Abstractness):** $A = Na / Nc$. Rango [0, 1]. 0=Concreto, 1=Abstracto.

### 2.2 Cálculo de Métricas

**Componente: `webapp`**

*   **Ce (Salientes):** Depende de `Flask`, `requests`, `flask_bootstrap`, `flask_moment`, `wtforms`, `os`, `datetime`. (Estimado: ~7 dependencias externas).
*   **Ca (Entrantes):** Solo `app.py` (entrypoint) importa `webapp`. (1 dependencia entrante).
*   **Na (Clases Abstractas):** 0.
*   **Nc (Clases Totales):** ~2 (TermostatoForm, y la instancia de Flask implícita).

**Resultados:**

1.  **Inestabilidad ($I$):**
    $$I = 7 / (1 + 7) = 0.875$$
    *   **Interpretación:** El componente es **Altamente Inestable**. Esto es normal para una capa de presentación/aplicación final. Significa que el componente es propenso a cambiar si sus dependencias (frameworks, librerías) cambian.

2.  **Abstracción ($A$):**
    $$A = 0 / 2 = 0$$
    *   **Interpretación:** El componente es **Totalmente Concreto**. No define contratos para otros, solo implementación.

3.  **Distancia de la Secuencia Principal ($D$):**
    $$D = |A + I - 1|$$
    $$D = |0 + 0.875 - 1| = |-0.125| = 0.125$$

### 2.3 Gráfica de la Secuencia Principal

```
     A=1 (Abstracto)
      |
      |   Zona de Inutilidad
      |       (Abstracto pero Inestable)
      |
      |\
      | \  <-- Secuencia Principal (Balance Ideal)
      |  \
      |   \
      |    \
      |     \
      |      \
      |_______X__________________ I=1 (Inestable)
    A=0      (Tu componente está aquí: Zona de Implementación)
```

### 2.4 Análisis de los Resultados

El componente `webapp` se encuentra en la **Zona de Implementación** (Baja Abstracción, Alta Inestabilidad).

*   **¿Es esto malo?** No necesariamente. En Clean Architecture, la capa de "Main" o "Frameworks & Drivers" *debe* ser concreta y sucia.
*   **El Problema Real:** El problema no es que `webapp` sea concreto, sino que **contiene Lógica de Negocio**.
    *   Según Martin, la lógica de negocio debería estar en componentes con $I$ bajo (Estables) y $A$ alto (Abstractos) o al menos separados del framework.
    *   Al tener la lógica dentro de un componente con $I=0.875$, la lógica de negocio se vuelve frágil y difícil de mantener.

---

## 3. Recomendaciones de Refactorización

Para mejorar la calidad de diseño y arquitectura, se propone la siguiente evolución hacia una **Arquitectura Hexagonal (Ports & Adapters)** simplificada:

### Paso 1: Extraer Capa de Servicio (Mejora de Cohesión)
Crear `webapp/services.py`. Mover `obtener_estado_termostato` y la lógica de caché allí.
*   *Beneficio:* `__init__.py` solo se encarga de rutas. `services.py` solo se encarga de datos.

### Paso 2: Aplicar DIP (Mejora de Arquitectura)
Definir una clase abstracta o protocolo para el servicio de datos.
```python
class TermostatoService(Protocol):
    def obtener_estado(self) -> dict: ...
```
Hacer que las rutas dependan de esta abstracción, no de `requests` directamente.

### Paso 3: Inyección de Dependencias
Instanciar el servicio concreto en el arranque (`app.py` o configuración) e inyectarlo en las vistas.
*   *Beneficio:* Permite testear las vistas usando un `MockTermostatoService` sin necesidad de conexión a internet ni backend real.

---
*Informe generado por el Asistente de Arquitectura.*
