---
description: Compila el frontend, copia los archivos estáticos y prepara el commit para el despliegue final.
---

Este flujo de trabajo automatiza el empaquetado y preparación del despliegue en Google Cloud Run. Realizará las acciones de construcción automáticamente y se detendrá para pedirte el permiso final antes de lanzar el despliegue al servidor, respetando la regla "deploy-cloudrun".

// turbo
1. Compila el frontend estático
```powershell
cd stock-ai-app ; npm run build ; cd ..
```

// turbo
2. Limpia el directorio de distribución estática del backend y copia la nueva compilación
```powershell
Remove-Item -Recurse -Force static\* -ErrorAction SilentlyContinue ; Copy-Item -Recurse -Force stock-ai-app\dist\* static\
```

// turbo
3. Añade los cambios de compilación a git listos para subirse
```powershell
git add . ; git commit -m "chore(release): empaquetado de producción preparado desde workflow automático"
```

4. Solicitar aprobación explícita al usuario para el despliegue final en la nube (Regla de Seguridad) y de ser aprobada correr lo siguiente:
```powershell
gcloud run deploy stock-ai-pulse --source . --project stock-ai-pulse --region us-central1 --allow-unauthenticated --set-env-vars "GOOGLE_API_KEY=$env:GOOGLE_API_KEY,GEMINI_MODEL=gemini-2.5-flash-lite-preview-09-2025,PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python,OMP_NUM_THREADS=1,MKL_NUM_THREADS=1" --memory 2Gi --cpu 2 --timeout 600
```
