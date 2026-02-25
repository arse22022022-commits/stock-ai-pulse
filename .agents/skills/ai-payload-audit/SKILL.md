---
name: ai-payload-audit
description: Auditoría obligatoria de datos serializados antes de ser enviados al motor LLM de Google Gemini
---

# Auditoría Estricta de Payload IA

Esta skill define cómo debemos manipular, crear o ampliar la información (prompts, JSON, contextos) que la aplicación envía a los LLMs (como Gemini).

## Contexto de Fallos Comunes
En este proyecto, hemos sufrido regresiones silenciosas donde un cambio en la interfaz gráfica (UI) o una refactorización de Python causaba que la IA recibiera variables `null`, campos vacíos (`""`), o diccionarios malformados sin que el servidor diera un "Error 500". Esto resulta en respuestas alucinadas de la IA o disculpas genéricas (Ej: "RVOL no disponible").

## Protocolo Obligatorio

**SIEMPRE** que se te pida modificar:
- Un *Prompt* en `llm.py`
- La estructura del contexto enviado desde `endpoints.py` al LLM
- El payload JSON que el frontend de React (`ChatWidget.jsx`, `StockDashboard.jsx`, etc.) envía al backend.

Debes aplicar esta rutina de auditoría:

1. **Revisión del Ciclo Completo (Cradle to Grave):**
   Si añades la variable `VARX` para que la lea Gemini:
   - Verifica que `VARX` sale impresa correctamente en el front-end React.
   - Verifica que `VARX` se envía en el `body: JSON.stringify()` del `fetch`.
   - Verifica que `VARX` está declarada en el modelo Pydantic del `Request` en `endpoints.py`.
   - Verifica que la función que llama a `llm_service` le pasa explícitamente `VARX`.

2. **Console Log Defensivo (Temporal):**
   Durante la codificación del cambio, inyecta temporalmente un `logger.info(f"Payload to LLM: {context}")` justo antes de la llamada a la API de Google, para forzar al desarrollador a leer qué está viajando por la red en caso de fallo.
