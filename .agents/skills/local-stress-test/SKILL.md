---
name: local-stress-test
description: Protocolo de prueba de estrés pre-despliegue para evitar simuladores y cuelgues por paralelismo
---

# Simulador de Saturación Local

Esta skill detalla un plan de pruebas agresivo, pensado especialmente para endpoints masivos como "Análisis de Cartera".

## Contexto Predictivo
El servidor usa múltiples modelos estocásticos, hilos de álgebra lineal (MKL, OpenBLAS) y multihilo en las llamadas a red (yfinance, gemini). Un entorno que funciona cuando le pasas 1 ticker puede colapsar y quedar *"congelado para siempre"* cuando le pasas 10 en paralelo por agotamiento del `ThreadPoolExecutor` o *Deadlocks* del GIL de Python.

## Protocolo Obligatorio

Antes de permitirte usar el protocolo de publicación (`deploy-cloudrun`), si has tocado rutas API que agrupan peticiones (ej: `/api/portfolio`):

1. **Generar un Script Fuego Rápido:**
   Crea y ejecuta un script en Python (ej: `test_stress.py`) que haga peticiones múltiples al servidor local en un bucle cerrado.
   
2. **Modelo de Prueba:**
   Asegúrate de golpear con una lista pesada de tickers (mínimo 6) para saturar el `io_executor` y `cpu_executor`.
   ```python
   import requests, time
   tickers = ["AAPL", "MSFT", "GOOG", "TSLA", "NVDA", "IBE.MC", "SAN.MC"]
   print("Iniciando Test de Estrés Local...")
   start = time.time()
   res = requests.post("http://127.0.0.1:8000/api/portfolio", json=tickers, timeout=120)
   print(f"Status: {res.status_code}. Tiempo: {time.time()-start:.2f}s")
   ```

3. **Criterio de Éxito:**
   Si el script devuelve código `200` y un tiempo menor a 40 segundos, da luz verde al despliegue. Si devuelve error, un timeout, o el proceso en terminal `python server.py` se congela sin logs, reporta al usuario.
