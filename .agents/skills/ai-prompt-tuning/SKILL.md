---
name: ai-prompt-tuning
description: Reglas estrictas para modificar o crear prompts para el LLM y el motor Gemini
---

# Calibración de Prompts IA

Esta skill define las barreras de protección de los prompts y las llamadas asíncronas al modelo de LLM (`llm.py`) para evitar la variabilidad estocástica y la pérdida de formato en la interfaz gráfica.

## Reglas Inexcusables de Arquitectura

1. **Protección del Modelo Backend (`llm.py`)**:
    - Nunca sustituyas el modelo `gemini-2.5-flash-lite-preview-09-2025` por la versión estándar sin verificar expresa y previamente que el límite de Rate Limit gratuito permite más de 20 peticiones diarias.
    - Utiliza **SIEMPRE** la sintaxis del SDK `google-genai` (versión 2), no la librería antigua.

2. **Garantía Cero Variabilidad**:
    - Si el prompt es analítico (veredicto numérico cerrado), debes forzar `temperature=0.0` y `top_k=1` en el objeto `GenerateContentConfig`.
    - Si creas una función nueva para un análisis recurrente, DEBES inyectarle la envoltura HMAC `hashlib.md5(...)` para garantizar que la misma entrada numérica sirva el mismo output cacheado desde la memoria (MemCache) en lugar de consultar constantemente a la nube.

3. **Estructura Semántica Estricta en Prompts Conversacionales**:
    - Para los prompts iterativos o de soporte al usuario general (como el chat):
        - Fija la regla visual: *"Usa PÁRRAFOS MUY CORTOS (máximo 2-3 líneas por párrafo)."*
        - Fija la regla estructural: *"Usa listas con viñetas o números para enumerar razones o puntos clave."*
        - Prohíbe explícitamente y en mayúsculas: *"NO ENVÍES MUROS DE TEXTO SEGUIDOS BAJO NINGUNA CIRCUNSTANCIA."*

4. **Actualización de Entorno Frontend**:
    - Cada vez que despliegues una nueva caja conversacional de IA en el front-end React, debes envolver su respuesta renderizada dentro del componente `<ReactMarkdown />` para que el formato dictado en el paso anterior se pinte apropiadamente en el DOM del navegador.
