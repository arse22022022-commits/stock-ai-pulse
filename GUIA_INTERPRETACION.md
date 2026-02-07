# Guía de Interpretación Stock AI Pulse 🔭📈

Esta guía explica la lógica técnica detrás de las recomendaciones generadas por nuestra Inteligencia Artificial basada en Modelos Ocultos de Markov (HMM) y Redes Neuronales.

---

## 1. El Sistema de Consenso (Las 3 Capas)
La IA no "adivina" el precio; calcula probabilidades mediante el consenso de tres capas analíticas:

### A. Capa Estructural (HMM Retornos)
Analiza el comportamiento histórico del precio para clasificarlo en tres estados:
- **Estado 1 (Alcista)**: Rendimiento positivo con volatilidad controlada.
- **Estado 0 (Estable)**: Movimiento lateral, fase de acumulación o descanso.
- **Estado 2 (Volátil)**: Alta incertidumbre, riesgo de caídas bruscas o giros violentos.

### B. Capa de Impulso (HMM Diferencias)
Es el "corazón" de la salud técnica. Analiza la **aceleración** del precio:
- Evalúa si el movimiento tiene **Inercia** (fuerza continuada).
- Detecta si hay **Convergencia** (el precio y la fuerza van de la mano).

### C. Capa Predictiva (Neural Forecast)
Utiliza un modelo neuronal (LLM) que proyecta los próximos 10 días de cotización. Esta capa aporta la visión de futuro, filtrando si la inercia actual es sostenible matemáticamente.

---

## 2. Diccionario de Alertas de la IA 🔍

Cuando el sistema detecta una anomalía, añade una nota entre paréntesis. Aquí explicamos qué significan y qué acción tomar:

| Alerta | Significado Técnico | Acción Recomendada |
| :--- | :--- | :--- |
| **Impulso alcista incipiente** | El movimiento positivo lleva menos de 3 días activo. Podría ser un rebote falso o "ruido". | **Esperar**. Confirmar 24h más de permanencia en este estado antes de entrar. |
| **Señales de agotamiento** | La probabilidad matemática del modelo está cayendo, aunque el precio siga subiendo. | **Vigilar**. No abrir nuevas posiciones. Ajustar órdenes de venta (Stop Loss). |
| **Riesgo de sobre-extensión** | El precio está un 8% o más alejado de su media móvil de 20 días. | **Cautela**. El riesgo de una "toma de beneficios" (caída técnica) es muy alto. |
| **Divergencia detectada** | El precio sube, pero el modelo de impulso (aceleración) está bajando o es inestable. | **Alerta Roja**. Es un síntoma clásico de fin de tendencia. Riesgo de trampa. |
| **Deriva negativa en fase estable** | El mercado está en calma (poca volatilidad), pero el precio "gotea" hacia abajo. | **Evitar**. El activo no tiene interés comprador en este momento. |

---

## 3. Interpretación de los Veredictos

### 🟢 COMPRA FUERTE (Puntuación > 5)
Consenso total. La estructura es alcista, el impulso es firme (con inercia > 3 días) y el forecast es positivo. Es el escenario de mayor probabilidad de éxito.

### 🟡 COMPRA (Puntuación 2 a 4)
Contexto positivo, pero con matices. Puede haber una alerta de "sobre-extensión" o un impulso "incipiente". Sugiere una entrada escalonada o con stop amplio.

### ⚪ MANTENER (Puntuación 0 a 1)
Zona neutral o de conflicto. Un modelo dice "sube" y otro dice "baja". El sistema recomienda esperar a que los modelos se alineen.

### 🔴 VENTA / VENTA FUERTE (Puntuación negativa)
El impulso se ha quebrado o la volatilidad es demasiado alta. El sistema prioriza la **preservación del capital** sobre la búsqueda de beneficios.

---

## 4. Consejos de Uso
1. **Confirma la Inercia**: Un "Impulso consolidado" es mucho más fiable que uno "incipiente".
2. **Mira las Probabilidades**: En el panel lateral, si el estado actual tiene una probabilidad cercana al 90-100%, la señal es muy robusta. Si está cerca del 50-60%, hay dudas en el modelo.
3. **Usa el Forecast como filtro**: Si el veredicto es compra pero el forecast (línea punteada) va hacia abajo, la IA está dándote un aviso de que la subida podría ser corta.

---
*Nota: Esta herramienta es un asistente analítico basado en matemáticas avanzadas. No constituye asesoramiento financiero directo.*
