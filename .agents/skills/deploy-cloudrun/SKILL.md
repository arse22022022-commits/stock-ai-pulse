---
name: deploy-cloudrun
description: Protocolo estricto para desplegar la aplicación en Google Cloud Run respetando las reglas de seguridad
---

# Despliegue en Cloud Run

Esta skill define el protocolo obligatorio que debes seguir SIEMPRE que se te pida desplegar la aplicación en Google Cloud.

## REGLA DE ORO (MÁXIMA PRIORIDAD)
**NUNCA** ejecutes un comando `gcloud run deploy` de forma automatizada o por tu cuenta. 

## Protocolo de Despliegue

1. **Verificación Local**:
    - Asegúrate de que el código backend (`server.py`, `llm.py`) y frontend compilan y no tienen errores sintácticos.
    
2. **Construcción del Frontend**:
    - Si ha habido cambios en la UI, ejecuta SIEMPRE:
      ```bash
      cd stock-ai-app
      npm run build
      Remove-Item -Recurse -Force ..\static\*
      Copy-Item -Recurse -Force dist\* ..\static\
      ```
    
3. **Commit en Git**:
    - Realiza un commit claro describiendo los cambios que se van a subir a producción.
      ```bash
      git add .
      git commit -m "chore(release): preparing deployment for [razón]"
      ```

4. **SOLICITUD DE PERMISO (Pausa Obligatoria)**:
    - Debes usar la herramienta `notify_user` para pedir permiso EXPLÍCITO al usuario antes de proceder.
    - Ejemplo de mensaje: *"He preparado todo el entorno local. ¿Me das permiso para lanzar el comando de despliegue a Google Cloud Run?"*

5. **Ejecución (Solo tras confirmación explícita)**:
    - Una vez que el usuario responda "Sí", "Adelante" o similar, ejecuta el comando de despliegue en la raíz del proyecto, asegurándote de inyectar todas las variables ambientales clave para la IA y la gestión de hilos:
      ```bash
      gcloud run deploy stock-ai-pulse --source . --project stock-ai-pulse --region us-central1 --allow-unauthenticated --set-env-vars "GOOGLE_API_KEY=[mantener_la_del_entorno],GEMINI_MODEL=gemini-2.5-flash-lite-preview-09-2025,PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python,OMP_NUM_THREADS=1,MKL_NUM_THREADS=1" --memory 2Gi --cpu 2 --timeout 600
      ```
