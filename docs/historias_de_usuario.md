# Historias de Usuario - Mejoras WebApp Termostato

## Resumen del Proyecto

**Estado actual**: Dashboard de monitorización de termostato con visualización de temperatura, estado del climatizador y batería.

**Propósito**: Frontend de **solo visualización** que comunica el funcionamiento del termostato IoT remoto. No hay interacción ni control del dispositivo a través de esta interfaz.

**Tecnologías**: Flask, Bootstrap 3, Chart.js, JavaScript vanilla.

**Métricas de Calidad Actuales**:
- Python: Grado B (Pylint 7.62/10)
- Web: Grado A (0 errores)
- Issues: Funciones JS largas en `graficas.js` (79 y 105 líneas)

**API Backend** (v1.1.0): https://app-termostato-1090421346746.us-central1.run.app/docs/

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/termostato/` | GET | Estado completo (todos los datos) |
| `/termostato/historial/` | GET | Historial de temperaturas |
| `/comprueba/` | GET | Health check del backend |

**Proyecto Jira**: WT (webapp_termostato)

---

## Épica 1: Comunicación Efectiva del Estado (WT-1)

> Foco principal: que el usuario entienda claramente qué está pasando con el termostato

### WT-8: Leyenda explicativa del funcionamiento
**Como** usuario nuevo
**Quiero** entender qué significa cada dato mostrado en el dashboard
**Para** interpretar correctamente el estado del termostato

**Estados del sistema (según API v1.1.0):**

| Estado Climatizador | Significado |
|---------------------|-------------|
| apagado | Sistema en espera, temperatura en rango |
| encendido | Sistema activo (genérico) |
| enfriando | Aire acondicionado activo |
| calentando | Calefacción activa |

| Indicador Batería | Significado |
|-------------------|-------------|
| NORMAL | Carga suficiente (>3.5V) |
| BAJO | Carga baja, considerar recarga (2.5-3.5V) |
| CRITICO | Carga crítica, riesgo de apagado (<2.5V) |

**Criterios de aceptación:**
- [ ] Tooltip en cada card explicando el dato
- [ ] Sección "¿Cómo funciona?" colapsable
- [ ] Explicación de los 4 estados del climatizador
- [ ] Explicación de los 3 niveles de batería (NORMAL/BAJO/CRITICO)
- [ ] Iconos visuales para cada estado

**Prioridad:** Alta

---

### WT-9: Indicadores visuales de tendencia
**Como** usuario
**Quiero** ver si la temperatura está subiendo o bajando
**Para** anticipar el comportamiento del climatizador

**Lógica de tendencia:**
- Comparar temperatura actual con las últimas 3 lecturas
- Correlacionar con estado del climatizador (enfriando→↓, calentando→↑)

**Criterios de aceptación:**
- [ ] Flecha ↑↓ junto a temperatura actual
- [ ] Color verde si se acerca a deseada, rojo si se aleja
- [ ] Animación suave en cambios de valor
- [ ] Texto: "Subiendo hacia 22°C" o "Enfriando hacia 22°C"
- [ ] Icono coherente con estado_climatizador (❄️ enfriando, 🔥 calentando)

**Prioridad:** Alta

---

### WT-10: Estado de conexión visible
**Como** usuario
**Quiero** saber si los datos mostrados están actualizados
**Para** confiar en la información que veo

**Criterios de aceptación:**
- [ ] Indicador "En línea" / "Sin conexión" visible
- [ ] Timestamp de última actualización exitosa
- [ ] Cambio visual cuando datos tienen más de 30s
- [ ] Icono pulsante cuando está actualizando

**Prioridad:** Alta

---

### WT-11: Diferencia entre temperatura actual y deseada
**Como** usuario
**Quiero** ver claramente la diferencia entre temperatura actual y deseada
**Para** entender cuánto falta para alcanzar el confort

**Criterios de aceptación:**
- [ ] Mostrar diferencia: "+2.5°C para alcanzar objetivo"
- [ ] Barra de progreso visual temperatura actual → deseada
- [ ] Colores: azul (frío), verde (OK), rojo (calor)
- [ ] Estimación opcional: "~15 min para alcanzar"

**Prioridad:** Media

---

## Épica 2: Experiencia Visual Fluida (WT-2)

> Eliminar parpadeos y mejorar la percepción de tiempo real

### WT-12: Actualización sin recarga de página
**Como** usuario
**Quiero** que los datos se actualicen sin que la página parpadee
**Para** tener una experiencia visual fluida

**Contexto técnico**: Actualmente usa `<meta http-equiv="refresh" content="10">` que recarga toda la página.

**Criterios de aceptación:**
- [ ] Reemplazar meta refresh por AJAX/Fetch
- [ ] Actualizar solo valores que cambian
- [ ] Mantener gráficas sin reinicializar
- [ ] Indicador visual de "actualizando..."

**Prioridad:** Crítica

---

### WT-13: Usar endpoint unificado de la API
**Como** desarrollador
**Quiero** consumir el endpoint `/termostato/` que ya devuelve todos los datos
**Para** hacer una sola llamada en lugar de 5

**Contexto técnico**:
- Actualmente `lanzador.py` hace 5 llamadas separadas
- La API YA tiene `/termostato/` que devuelve todo en una sola llamada

**Respuesta de `/termostato/` (GET):**
```json
{
  "temperatura_ambiente": 22,      // 0-50°C
  "temperatura_deseada": 24,       // 15-30°C
  "estado_climatizador": "encendido", // apagado|encendido|enfriando|calentando
  "carga_bateria": 3.8,            // 0.0-5.0V
  "indicador": "NORMAL"            // NORMAL|BAJO|CRITICO
}
```

**Criterios de aceptación:**
- [ ] Reemplazar 5 llamadas por una sola a `/termostato/`
- [ ] Crear endpoint local `/api/estado` que proxee a la API
- [ ] Cachear última respuesta válida (para datos stale)
- [ ] Agregar timestamp local de última actualización

**Prioridad:** Alta

---

### WT-14: Transiciones animadas en cambios
**Como** usuario
**Quiero** animaciones suaves cuando cambian los valores
**Para** notar los cambios sin perder contexto

**Criterios de aceptación:**
- [ ] Fade-in/out en cambio de valores numéricos
- [ ] Transición de color en cambio de estados
- [ ] Highlight temporal en valor recién actualizado
- [ ] Duración de animación < 300ms

**Prioridad:** Baja

---

## Épica 3: Gráficas Informativas (WT-3)

> Mejorar la comprensión de tendencias y patrones

### WT-15: Ventana de tiempo configurable con historial
**Como** usuario
**Quiero** cambiar el rango de tiempo en las gráficas
**Para** ver tendencias de diferentes periodos

**Contexto técnico**:
- Actualmente fijo a 5 minutos en `graficas.js` (solo localStorage)
- La API tiene `/termostato/historial/?limite=N` que retorna historial del servidor

**Respuesta de `/termostato/historial/` (GET):**
```json
{
  "historial": [
    {"timestamp": "2025-12-22T10:30:00", "temperatura": 22},
    {"timestamp": "2025-12-22T10:31:00", "temperatura": 22.5}
  ],
  "total": 50
}
```

**Criterios de aceptación:**
- [ ] Selector: 5min (localStorage), 1h, 6h, 24h (API historial)
- [ ] Usar `/termostato/historial/?limite=N` para rangos largos
- [ ] Combinar datos locales recientes con historial del servidor
- [ ] Persistir preferencia en localStorage

**Prioridad:** Media

---

### WT-16: Zona de confort en gráfica
**Como** usuario
**Quiero** ver la temperatura deseada como referencia en la gráfica
**Para** entender si el sistema está logrando el objetivo

**Criterios de aceptación:**
- [ ] Línea horizontal en temperatura deseada
- [ ] Zona sombreada de confort (±1°C de la deseada)
- [ ] Leyenda explicativa
- [ ] Actualizar si cambia temperatura deseada

**Prioridad:** Media

---

### WT-17: Correlación temperatura-climatizador
**Como** usuario
**Quiero** ver la relación entre temperatura y estados del climatizador
**Para** entender cómo responde el sistema

**Criterios de aceptación:**
- [ ] Overlay de estados en gráfica de temperatura
- [ ] Colores: rojo=calentando, azul=enfriando, gris=apagado
- [ ] Tooltip mostrando ambos valores al hover
- [ ] Opción de mostrar/ocultar overlay

**Prioridad:** Baja

---

## Épica 4: Alertas Visuales (WT-4)

> Comunicar situaciones importantes sin requerir acción del usuario

### WT-18: Alerta visual de batería baja
**Como** usuario
**Quiero** que la card de batería destaque cuando está baja
**Para** saber que puede haber problemas pronto

**Niveles de alerta según API:**
| Indicador | Color | Acción Visual |
|-----------|-------|---------------|
| NORMAL | Verde | Sin alerta |
| BAJO | Naranja | Advertencia, pulso sutil |
| CRITICO | Rojo | Alerta urgente, pulso intenso |

**Criterios de aceptación:**
- [ ] Card verde para NORMAL, naranja para BAJO, rojo para CRITICO
- [ ] Icono de advertencia visible en BAJO y CRITICO
- [ ] Animación de pulso (sutil en BAJO, intenso en CRITICO)
- [ ] Tooltip con recomendación según nivel

**Prioridad:** Alta

---

### WT-19: Alerta visual de pérdida de conexión
**Como** usuario
**Quiero** ver claramente cuando se pierde conexión con el backend
**Para** saber que los datos pueden estar desactualizados

**Criterios de aceptación:**
- [ ] Banner de advertencia en la parte superior
- [ ] Mostrar "Último dato: hace X minutos"
- [ ] Atenuar cards con datos potencialmente obsoletos
- [ ] Notificación cuando se recupera conexión

**Prioridad:** Alta

---

### WT-20: Alerta visual de temperatura extrema
**Como** usuario
**Quiero** ver si la temperatura está muy lejos de la deseada
**Para** entender que el sistema está trabajando fuertemente

**Criterios de aceptación:**
- [ ] Indicador si diferencia > 5°C
- [ ] Card de ambiente cambia a color de alerta
- [ ] Texto explicativo: "Temperatura muy alejada del objetivo"
- [ ] Sin sonido (solo visual)

**Prioridad:** Media

---

## Épica 5: Estabilidad y Rendimiento (WT-5)

> Mejorar robustez basado en métricas de calidad

### WT-21: Validación de datos de la API
**Como** usuario
**Quiero** que los datos mostrados sean validados
**Para** no ver información incorrecta

**Rangos válidos según API v1.1.0:**
| Campo | Rango | Tipo |
|-------|-------|------|
| temperatura_ambiente | 0-50°C | integer |
| temperatura_deseada | 15-30°C | integer |
| carga_bateria | 0.0-5.0V | number |
| indicador | NORMAL, BAJO, CRITICO | string |
| estado_climatizador | apagado, encendido, enfriando, calentando | string |

**Criterios de aceptación:**
- [ ] Validar cada campo según su rango/valores permitidos
- [ ] Mostrar "N/A" si dato está fuera de rango
- [ ] Mostrar "Error" si dato tiene tipo incorrecto
- [ ] Log en consola de datos inválidos recibidos

**Prioridad:** Alta

---

### WT-22: Reintentos automáticos en API
**Como** usuario
**Quiero** que la aplicación reintente si la API falla
**Para** no ver errores por fallos momentáneos

**Criterios de aceptación:**
- [ ] 3 reintentos con backoff exponencial
- [ ] Timeout progresivo (2s, 4s, 8s)
- [ ] Mostrar datos anteriores durante reintentos
- [ ] Indicador de "reintentando..."

**Prioridad:** Alta

---

### WT-23: Refactorizar funciones JavaScript largas
**Como** desarrollador
**Quiero** dividir las funciones largas en `graficas.js`
**Para** mejorar mantenibilidad y testabilidad

**Contexto técnico**:
- `actualizarGraficaTemperatura` tiene 79 líneas (max: 50)
- `actualizarGraficaClimatizador` tiene 105 líneas (max: 50)

**Criterios de aceptación:**
- [ ] Ninguna función > 50 líneas
- [ ] Funciones con responsabilidad única
- [ ] Nombres descriptivos
- [ ] 0 warnings en ESLint

**Prioridad:** Media

---

## Épica 6: Accesibilidad y Responsive (WT-6)

### WT-24: Dashboard responsive mejorado
**Como** usuario móvil
**Quiero** ver el dashboard correctamente en mi teléfono
**Para** monitorear desde cualquier dispositivo

**Criterios de aceptación:**
- [ ] Cards apiladas verticalmente en móvil
- [ ] Gráficas con scroll horizontal si necesario
- [ ] Botones de tamaño táctil (mínimo 44px)
- [ ] Fuentes legibles sin zoom

**Prioridad:** Media

---

### WT-25: Modo oscuro
**Como** usuario
**Quiero** un tema oscuro
**Para** reducir fatiga visual de noche

**Criterios de aceptación:**
- [ ] Toggle claro/oscuro
- [ ] Respetar preferencia del sistema
- [ ] Persistir en localStorage
- [ ] Colores accesibles en ambos temas

**Prioridad:** Baja

---

## Épica 7: DevOps y Calidad (WT-7)

### WT-26: Tests unitarios básicos
**Como** desarrollador
**Quiero** tests para las funciones principales
**Para** detectar regresiones

**Criterios de aceptación:**
- [ ] Test de ruta `/` con API funcionando
- [ ] Test de ruta `/` con API caída
- [ ] Test de `/api/estado` (cuando exista)
- [ ] Cobertura mínima 70%

**Prioridad:** Media

---

### WT-27: Health check endpoint
**Como** sistema de monitoreo
**Quiero** un endpoint `/health`
**Para** detectar cuando el servicio falla

**Contexto técnico**:
La API backend YA tiene `/comprueba/` que retorna:
```json
{
  "status": "ok",
  "timestamp": "2025-12-22T10:30:00",
  "uptime_seconds": 3600,
  "version": "1.1.0"
}
```

**Criterios de aceptación:**
- [ ] Crear GET `/health` en el frontend Flask
- [ ] Verificar conexión con `/comprueba/` del backend
- [ ] Retornar 200 si backend responde, 503 si no
- [ ] Incluir versión del frontend y estado del backend
- [ ] Respuesta en menos de 2s (incluye llamada al backend)

**Prioridad:** Media

---

## Matriz de Priorización Revisada

| Prioridad | Historias | Justificación |
|-----------|-----------|---------------|
| **Crítica** | WT-12 | Meta refresh causa mala UX, bloquea otras mejoras |
| **Alta** | WT-8, WT-9, WT-10, WT-13, WT-18, WT-19, WT-21, WT-22 | Comunicación efectiva y estabilidad |
| **Media** | WT-11, WT-15, WT-16, WT-20, WT-23, WT-24, WT-26, WT-27 | Mejoras de experiencia |
| **Baja** | WT-14, WT-17, WT-25 | Nice-to-have |

---

## Roadmap Sugerido

### Sprint 1: Fundación Técnica
**Objetivo**: Eliminar el meta refresh y unificar la API

- WT-12: Actualización sin recarga de página (Crítica)
- WT-13: Endpoint API unificado (Alta)
- WT-10: Estado de conexión visible (Alta)

**Resultado**: Dashboard que actualiza fluidamente sin parpadeos

### Sprint 2: Comunicación Clara
**Objetivo**: Que el usuario entienda el estado del termostato

- WT-8: Leyenda explicativa del funcionamiento
- WT-9: Indicadores visuales de tendencia
- WT-18: Alerta visual de batería baja
- WT-19: Alerta visual de pérdida de conexión

**Resultado**: Usuario comprende qué está pasando sin ser experto

### Sprint 3: Robustez
**Objetivo**: Manejar errores gracefully

- WT-21: Validación de datos de la API
- WT-22: Reintentos automáticos en API
- WT-23: Refactorizar funciones JavaScript largas

**Resultado**: Código más mantenible, experiencia más estable

### Sprint 4: Mejoras de Visualización
**Objetivo**: Mejorar comprensión de tendencias

- WT-11: Diferencia temperatura actual/deseada
- WT-15: Ventana de tiempo configurable
- WT-16: Zona de confort en gráfica

**Resultado**: Gráficas más informativas

### Sprint 5: Polish
**Objetivo**: Pulir experiencia

- WT-24: Dashboard responsive mejorado
- WT-26: Tests unitarios básicos
- WT-27: Health check endpoint

---

## Dependencias Técnicas

```
WT-12 (AJAX) ──┬──> WT-9 (Tendencias)
               ├──> WT-10 (Estado conexión)
               ├──> WT-14 (Animaciones)
               └──> WT-19 (Alerta conexión)

WT-13 (API unificada) ──> WT-12 (AJAX)

WT-23 (Refactor JS) ──> WT-15 (Ventana tiempo)
                    ──> WT-16 (Zona confort)
```

---

## Mapeo de Códigos

| Código Original | Código Jira | Título |
|-----------------|-------------|--------|
| Épica 1 | WT-1 | Comunicación Efectiva del Estado |
| Épica 2 | WT-2 | Experiencia Visual Fluida |
| Épica 3 | WT-3 | Gráficas Informativas |
| Épica 4 | WT-4 | Alertas Visuales |
| Épica 5 | WT-5 | Estabilidad y Rendimiento |
| Épica 6 | WT-6 | Accesibilidad y Responsive |
| Épica 7 | WT-7 | DevOps y Calidad |
| HU-001 | WT-8 | Leyenda explicativa del funcionamiento |
| HU-002 | WT-9 | Indicadores visuales de tendencia |
| HU-003 | WT-10 | Estado de conexión visible |
| HU-004 | WT-11 | Diferencia entre temperatura actual y deseada |
| HU-005 | WT-12 | Actualización sin recarga de página |
| HU-006 | WT-13 | Usar endpoint unificado de la API |
| HU-007 | WT-14 | Transiciones animadas en cambios |
| HU-008 | WT-15 | Ventana de tiempo configurable con historial |
| HU-009 | WT-16 | Zona de confort en gráfica |
| HU-010 | WT-17 | Correlación temperatura-climatizador |
| HU-011 | WT-18 | Alerta visual de batería baja |
| HU-012 | WT-19 | Alerta visual de pérdida de conexión |
| HU-013 | WT-20 | Alerta visual de temperatura extrema |
| HU-014 | WT-21 | Validación de datos de la API |
| HU-015 | WT-22 | Reintentos automáticos en API |
| HU-016 | WT-23 | Refactorizar funciones JavaScript largas |
| HU-017 | WT-24 | Dashboard responsive mejorado |
| HU-018 | WT-25 | Modo oscuro |
| HU-019 | WT-26 | Tests unitarios básicos |
| HU-020 | WT-27 | Health check endpoint |

---

*Documento actualizado el 2025-12-24*
*Códigos sincronizados con proyecto Jira WT (webapp_termostato)*
