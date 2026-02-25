---
name: safe-dependency-update
description: Protocolo de seguridad para evitar desbordes de memoria y cuelgues al gestionar librerías core de IA
---

# Gestión Segura de Dependencias Python

Esta skill dicta cómo afrontar peticiones de instalación de dependencias, especialmente si afectan a librerías nucleares (PyTorch, numpy, hmmlearn). 

## Contexto de Vulnerabilidad
El entorno backend hace un uso extremo de multihilo concurrente (`ThreadPoolExecutor` en `endpoints.py`) para procesar carteras enteras. Librerías matemáticas nativas como OpenBLAS o MKL pueden generar "Deadlocks" o cuelgues infinitos y bloqueos de CPU al competir por el mismo set de hilos si no están acotadas expresamente.

## Protocolo Obligatorio

Si el usuario te pide, o el código requiere, una alteración en el entorno virtual (`pip install` o modificar dependencias que incluyan cálculos pesados), debes:

1. **Aislamiento Previo:**
   Nunca ejecutes `pip install` a ciegas. Solicita instalarlo en un archivo de test `temp_test.py` o analiza un script de prueba primero si el servidor está crítico.

2. **Auditoría de Inyección de Threads (MANDATORIA):**
   Siempre que agregues un módulo que use tensores o álgebra lineal a `server.py` o `analysis.py`, verifica obligatoriamente que las protecciones del inicio del archivo `server.py` están intactas ANTES de importar la librería:
   ```python
   import os
   os.environ["OMP_NUM_THREADS"] = "1"
   os.environ["MKL_NUM_THREADS"] = "1"
   os.environ["OPENBLAS_NUM_THREADS"] = "1"
   os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
   os.environ["NUMEXPR_NUM_THREADS"] = "1"
   import torch
   torch.set_num_threads(1)
   ```

3. **Mantenimiento del requirements.txt:**
   Una vez verificada la ejecución sin fugas mem/hilos, anota la versión exacta probada en el `requirements.txt`. Nunca dejes la versión sin marcar (`==X.Y.Z`).
