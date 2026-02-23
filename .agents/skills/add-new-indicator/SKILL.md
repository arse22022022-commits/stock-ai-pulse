---
name: add-new-indicator
description: Protocolo para integrar un nuevo indicador matemático o estadístico en la aplicación
---

# Añadir un Nuevo Indicador Técnico

Esta skill define cómo debe extenderse el análisis cuantitativo de la plataforma sin romper la lógica del Triple Pilar.

## Pasos de Implementación

1. **Cálculo Matemático (`server.py`)**:
    - Localiza la función `analyze_stock`.
    - Añade el cálculo utilizando las capacidades vectorizadas de `pandas` o `numpy` justo después del cálculo de `Returns` y `Diff_Returns`.
    - Ejemplo: `data['MACD'] = data['Close'].ewm(span=12).mean() - data['Close'].ewm(span=26).mean()`
    - **No elimines ni alteres el código de los indicadores originales o del HMM.**

2. **Integración en la Matriz de Recomendación**:
    - Localiza la función anidada `generate_ai_recommendation` dentro de `server.py`.
    - Modifica la ponderación (actualmente: 40% Estructura, 30% Momento, 30% Proyección) para acomodar el nuevo indicador.
    - Asegúrate de que la suma final de ponderaciones siga siendo exactamente 1 (100%).
    - Genera una lógica IF/ELSE para sumar puntos al score global basándote en el resultado del nuevo indicador (ej. "Si MACD > 0, sumar 20 puntos").

3. **Inyección en el Reporte Semántico**:
    - Modifica la lógica de la variable `notes` (dentro de `generate_ai_recommendation`) para añadir una alerta explícita en español si el indicador es destacable.
    - Ejemplo: `if macd_cross: notes.append("Cruce alcista MACD")`

4. **Retorno de Datos al Frontend**:
    - Asegúrate de empaquetar el estado final del indicador dentro del objeto `response_data` retornado por `analyze_stock`.
    - Utiliza `float()` o la función nativa `sanitize_for_json` para asegurar que el dato sea apto para transferencia HTTP (sin NaNs o floats genéricos de Numpy).
