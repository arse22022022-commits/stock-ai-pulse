---
description: Ejecuta un test de estrés sobre la API de Google Gemini para auditar sus cuotas y respuestas.
---

Este workflow llama repetidas veces a los servidores de GenAI para probar la disponibilidad regional de Google, medir latencia, y prever bloqueos por cuota ("Resource Exhausted"). Útil ante quejas de "Analista No Disponible".

// turbo-all

1. Lanza el banco de pruebas de estrés para Gemini
```powershell
python test_genai.py
```
