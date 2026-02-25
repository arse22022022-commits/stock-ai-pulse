---
name: full-stack-build
description: Protocolo obligatorio para compilar y servir de forma segura los cambios del frontend al backend
---

# Reconstrucción Full-Stack (React -> FastAPI)

Esta skill define el procedimiento estricto que debes seguir siempre que el usuario te pida modificar o depurar el código de la interfaz gráfica (React/JSX/CSS).

## Contexto y Problemática
En este proyecto, la aplicación React (`stock-ai-app`) y el servidor FastAPI comparten el mismo dominio en producción. El servidor Python está configurado para leer y servir los archivos desde una carpeta estática en la raíz (`static/`). Los cambios visuales no surten efecto hasta que se compilan y se copian allí.

## Protocolo Obligatorio

**SIEMPRE** que edites un archivo `.jsx`, `.js`, o `.css` en la carpeta `stock-ai-app`, debes ejecutar el siguiente flujo de comandos de PowerShell antes de dar la tarea por concluida:

1. **Compilar Frontend:**
   ```bash
   cd stock-ai-app
   npm run build
   cd ..
   ```

2. **Limpiar y Mover (Deploy Local):**
   Asegúrate de borrar la caché antigua del servidor y mover los nuevos archivos construidos (`dist\*`) a la carpeta `static\` raíz. Usa comandos seguros para Windows (PowerShell):
   ```bash
   mkdir static -ErrorAction SilentlyContinue
   Remove-Item -Recurse -Force static\*
   Copy-Item -Recurse -Force stock-ai-app\dist\* static\
   ```

3. **Notificación al Usuario:**
   Tras hacer esto, si el servidor `python server.py` ya estaba encendido, **debemos reiniciarlo**. 
   Al informar al usuario, debes indicarle siempre la regla de oro del navegador: *"He rehecho la build. Por favor, haz un Hard Refresh (Ctrl+F5 o Cmd+Shift+R) para forzar la carga de los nuevos recursos."*
