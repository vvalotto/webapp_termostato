# Plan de Despliegue en Google Cloud Platform

## Objetivo

Desplegar webapp_termostato (frontend) en Google Cloud Run con despliegue continuo desde GitHub.

**Frontend desplegado:** https://webapp-termostato-1090421346746.us-central1.run.app

**Backend existente:** https://app-termostato-1090421346746.us-central1.run.app

## Arquitectura

```
    GitHub                      Google Cloud Platform
  +---------+                 +------------------------+
  |  main   |  ---(push)--->  |     Cloud Build        |
  | branch  |                 | (build automatico)     |
  +---------+                 +-----------+------------+
                                          |
                                          v
                              +------------------------+
                              |      Cloud Run         |
                              |   webapp-termostato    |
                              |  (deploy automatico)   |
                              +-----------+------------+
                                          |
                                          v
                              +------------------------+
                              |      Cloud Run         |
                              |    app-termostato      |
                              |      (Backend)         |
                              +------------------------+
```

**Proyecto GCP:** `app-termostato-2025`
**Repositorio GitHub:** `vvalotto/webapp_termostato`

## Pre-requisitos

- [x] Cuenta de GCP con facturacion habilitada
- [x] gcloud CLI instalado y configurado
- [x] Proyecto de GCP configurado (`app-termostato-2025`)
- [x] Repositorio en GitHub

---

## Paso 1: Verificar configuracion de gcloud

**Estado:** Completado

```bash
gcloud config list
# account = vvalotto@gmail.com
# project = app-termostato-2025
```

---

## Paso 2: Habilitar APIs necesarias

**Estado:** Completado

```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

---

## Paso 3: Crear Procfile

**Acciones:**
1. Crear archivo `Procfile` en la raiz del proyecto

**Contenido de `Procfile`:**
```
web: gunicorn --bind :$PORT --workers 1 --threads 8 app:app
```

---

## Paso 4: Subir cambios a GitHub

**Acciones:**
1. Commit del Procfile
2. Push a la rama main/master

```bash
git add Procfile
git commit -m "Add Procfile for Cloud Run deployment"
git push origin master
```

---

## Paso 5: Configurar despliegue continuo desde GitHub

### Opcion A: Desde la Consola de GCP (Recomendado)

1. Ir a [Cloud Run Console](https://console.cloud.google.com/run)
2. Click en **"Create Service"**
3. Seleccionar **"Continuously deploy from a repository"**
4. Click en **"Set up with Cloud Build"**
5. Autenticar con GitHub y seleccionar el repositorio `vvalotto/webapp_termostato`
6. Configurar:
   - **Branch:** `master` (o `main`)
   - **Build Type:** `Python via Buildpacks`
7. Configurar el servicio:
   - **Service name:** `webapp-termostato`
   - **Region:** `us-central1`
   - **Authentication:** `Allow unauthenticated invocations`
8. Expandir **"Container, Networking, Security"**:
   - **Memory:** `256Mi`
   - **Min instances:** `0`
   - **Max instances:** `10`
9. En **"Variables & Secrets"**, agregar variable de entorno:
   - **Name:** `API_URL`
   - **Value:** `https://app-termostato-1090421346746.us-central1.run.app`
10. Click en **"Create"**

### Opcion B: Desde linea de comandos

```bash
# Paso 1: Hacer deploy inicial (esto crea el servicio)
gcloud run deploy webapp-termostato \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="API_URL=https://app-termostato-1090421346746.us-central1.run.app" \
  --memory=256Mi \
  --min-instances=0 \
  --max-instances=10

# Paso 2: Conectar con GitHub para despliegue continuo
# Ir a Cloud Console > Cloud Run > webapp-termostato > "Set up continuous deployment"
```

---

## Paso 6: Verificar despliegue

**Acciones:**
1. Esperar a que Cloud Build termine (1-3 minutos)
2. Obtener URL del servicio
3. Verificar funcionamiento

```bash
# Obtener URL del servicio
gcloud run services describe webapp-termostato \
  --region=us-central1 \
  --format='value(status.url)'

# Verificar health check
curl $(gcloud run services describe webapp-termostato --region=us-central1 --format='value(status.url)')/health

# Abrir en navegador
open $(gcloud run services describe webapp-termostato --region=us-central1 --format='value(status.url)')
```

---

## Paso 7: Probar despliegue continuo

Una vez configurado, cada push a `master` dispara un deploy automatico:

```bash
# Hacer un cambio
echo "# Test" >> README.md
git add README.md
git commit -m "Test continuous deployment"
git push origin master

# Verificar en Cloud Console que se inicia un nuevo build
# https://console.cloud.google.com/cloud-build/builds
```

---

## Costos Estimados

- **Cloud Run:** Con `min-instances=0`, solo pagas por uso real
- **Cloud Build:** 120 min/dia gratis, luego $0.003/min
- **Estimado mensual:** < $5/mes con uso bajo

---

## Checklist Final

- [x] Paso 1: Verificar gcloud CLI
- [x] Paso 2: Habilitar APIs
- [x] Paso 3: Crear Procfile
- [x] Paso 4: Subir cambios a GitHub
- [x] Paso 5: Configurar despliegue continuo
- [x] Paso 6: Verificar despliegue
- [ ] Paso 7: Probar despliegue continuo (opcional)

---

## Troubleshooting

**Error "Container failed to start":**
- Verificar Procfile
- Revisar logs: `gcloud run logs read webapp-termostato --region=us-central1`

**Error de conexion con backend:**
- Verificar variable API_URL en Cloud Run
- Probar backend: `curl https://app-termostato-1090421346746.us-central1.run.app/comprueba/`

**Build falla en Cloud Build:**
- Verificar requirements.txt
- Ver logs en [Cloud Build](https://console.cloud.google.com/cloud-build/builds)

---

## Comandos utiles

```bash
# Ver logs en tiempo real
gcloud run logs tail webapp-termostato --region=us-central1

# Ver historial de builds
gcloud builds list --limit=5

# Forzar nuevo deploy sin cambios en codigo
gcloud run deploy webapp-termostato --source . --region us-central1

# Ver detalles del servicio
gcloud run services describe webapp-termostato --region=us-central1
```

---

## Flujo de trabajo diario

Una vez configurado:

1. Desarrollas localmente
2. `git push origin master`
3. Cloud Build construye automaticamente
4. Cloud Run despliega automaticamente
5. Verificas en la URL publica

No necesitas ejecutar ningun comando de `gcloud` para deploys rutinarios.

---

*Plan actualizado el 2025-12-27*
*Metodo: Despliegue continuo desde GitHub*
*Estado: COMPLETADO*
