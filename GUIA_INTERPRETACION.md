# Guía de Interpretación Stock AI Pulse 🔭📈

Esta guía explica la lógica técnica detrás de las recomendaciones generadas por nuestra Inteligencia Artificial basada en Modelos Ocultos de Markov (HMM) y Redes Neuronales.

---

## 1. El Sistema de Consenso (Triple Pilar) 🏛️

La recomendación final ("COMPRA", "VENTA", etc.) es el resultado de una suma ponderada de tres modelos independientes. La puntuación va de 0 a 100.

| Pilar | Peso | Qué Analiza | Métrica Clave |
| :--- | :--- | :--- | :--- |
| **1. Estructura** | **60%** | Salud y eficiencia a largo plazo | **Ratio R/R** (Estructura HMM) + **Filtro Direccional** |
| **2. Impulso** | **20%** | Aceleración del precio actual | **Media** del Régimen HMM de Diferencias |
| **3. Proyección** | **20%** | Escenario futuro (Thinking Model) | **Razonamiento Zero-Shot** de Gemini 3.1 Pro |


### Desglose de Puntuación

#### A. Pilar Estructural (Max 60 pts) - El "Anclaje"
Es la base del veredicto. Mira la calidad del estado actual y lo valida con el volumen:
-   **Anclaje Alcista**: Ratio R/R > 0.15 (Estructura limpia).
-   **Filtro Direccional (NUEVO)**: 
    -   Si el volumen es alto (**RVOL > 1.5**) y el precio sube -> **Confirmación de Acumulación** (+25% score).
    -   Si el volumen es alto (**RVOL > 1.5**) y el precio cae -> **Alerta de Distribución/Pánico** (-50% score).

#### B. Pilar de Impulso (Max 20 pts)
Mide la "fuerza G" del movimiento en la sesión actual.

#### C. Pilar de Proyección (Max 20 pts)
Mira hacia el futuro con la capacidad de razonamiento de Gemini 3.1 Pro.

---

## 2. La Estabilidad del Veredicto (Modelo de Histéresis) 🛡️

Para evitar que el color del gráfico cambie constantemente por pequeños ruidos diarios, el sistema aplica un "Modelo de Histéresis" a la puntuación total:

- **Puerta de Entrada alta**: Para que un activo cambie de estado a **COMPRA**, el sistema exige que la fuerza impulsora rompa un "techo" de seguridad (un score de **65** sobre 100).
- **Puerta de Salida baja**: Una vez que el activo entra en el estado de "COMPRA", el modelo de histéresis lo mantiene ahí, tolerando retrocesos normales de mercado. No te sacará de "COMPRA" hasta que el score caiga por debajo de **50**.

*Esto crea bloques de color sólidos en la gráfica y evita el peligroso "parpadeo visual" (entrar y salir constantemente de la acción).*

---

## 3. Veredictos y Criterios 🎯

La suma de los puntos anteriores genera el veredicto final:

| Puntuación Total | Veredicto | Significado | Estrategia Sugerida |
| :--- | :--- | :--- | :--- |
| **>= 80** | **🟢 COMPRA FUERTE** | Estructura perfecta + Inercia + Futuro alcista. | **Entrada agresiva**. Ideal para aumentar posición. |
| **60 - 79** | **🟡 COMPRA** | Estructura positiva, pero falla algún pilar (ej. poco impulso). | **Entrada escalonada**. Buscar confirmación de precio. |
| **40 - 59** | **⚪ MANTENER** | Zona de equilibrio. Fuerzas alcistas y bajistas empatadas. | **No operar**. Si tienes posición, mantenla con Stop Loss ajustado. |
| **20 - 39** | **🟠 VENTA** | Pérdida de eficiencia. El riesgo empieza a superar al beneficio. | **Reducir riesgo**. Cerrar parciales o ajustar stops muy ceñidos. |
| **< 20** | **🔴 VENTA FUERTE** | Colapso estructural y aceleración negativa. | **Salida inmediata**. No intentar "cazar el suelo". |

---

## 4. Glosario de Justificaciones 🗣️

Aquí explicamos el significado exacto de las frases que utiliza la IA para justificar su recomendación:

| Frase de la IA | Qué significa realmente |
| :--- | :--- |
| **"Eficiencia estructural óptima con fuerte inercia alcista confirmada."** | **El escenario ideal.** El precio sube de forma limpia (sin apenas retrocesos) y además está acelerando. Es una tendencia robusta y saludable. |
| **"Estructura positiva. El mercado muestra calidad y potencial de crecimiento."** | **Buen momento.** La tendencia es alcista y el riesgo es bajo, aunque quizás le falta un poco de "explosividad" o aceleración para ser perfecta. |
| **"Zona de equilibrio. Los pilares muestran señales mixtas o estables."** | **Indecisión.** Puede que el precio suba pero con mucha volatilidad (ruido), o que esté lateral. No hay una ventaja estadística clara para entrar. |
| **"Pérdida de eficiencia. Se detecta ruido o sesgo bajista en el impulso."** | **Precaución.** La tendencia se está ensuciando (muchos dientes de sierra) o está perdiendo fuerza. Aumentan las probabilidades de corrección. |
| **"Deterioro crítico. Colapso de eficiencia y aceleración negativa."** | **Peligro.** El activo está cayendo con fuerza o con mucha volatilidad. Es un entorno tóxico para el capital. |

---

## 5. Diccionario de Alertas de la IA 🔍

Cuando el sistema detecta una anomalía, añade una nota entre paréntesis. Aquí explicamos qué significan y qué acción tomar:

| Alerta | Significado Técnico | Acción Recomendada |
| :--- | :--- | :--- |
| **Riesgo elevado (R/R negativo)** | El estado actual es destructivo; la volatilidad es mayor que el retorno promedio. | **Evitar nuevas entradas** hasta que cambie el régimen. |
| **Deceleración detectada** | El precio sube, pero el impulso (segunda derivada) está bajando. Signo de agotamiento. | **Vigilar**. No perseguir el precio. Riesgo de techo de mercado. |
| **Proyección bajista** | El modelo neuronal anticipa una caída en los próximos 10 días, contradiciendo quizás la subida actual. | **Cautela**. El modelo detecta patrones de distribución no visibles a simple vista. |
| **Anomalía de volumen** | Entrada masiva de capital (RVOL > 2.0). Señal de fuerte interés institucional. | **Confirmación**. Valida el movimiento actual con alta convicción. |
| **Falta de convicción** | El precio sube o rompe estructura pero con volumen muy bajo (RVOL < 0.7). | **Precaución**. Riesgo de trampa; el movimiento podría no estar respaldado por "manos fuertes". |
| **Divergencia: Agotamiento** | El precio sube pero el volumen está cayendo de forma sostenida. | **Alerta**. El movimiento está perdiendo gasolina. Riesgo de giro inminente. |

---

## 6. Consejos de Uso Práctico

1.  **Confirma la Inercia**: Un "Impulso consolidado" (Estado HMM estable) es mucho más fiable que uno que cambia cada día.
2.  **Mira las Probabilidades**: En el panel lateral, si el estado actual tiene una probabilidad cercana al **90-100%**, la señal es muy robusta. Si está cerca del 50-60%, el mercado está indeciso.
3.  **Usa los dos HMM**:
    *   **HMM Rep (Retornos)** te dice "Dónde estamos" (Alcista, Bajista, Lateral).
    *   **HMM Diff (Impulso)** te dice "A qué velocidad vamos".
    *   *Ejemplo*: Si HMM Rep es "Alcista" pero HMM Diff es "Volátil/Bajista", el movimiento está perdiendo gasolina.

---

## 7. Índices Globales y Filtrado 🌍

La nueva sección de **Índices Globales** permite analizar mercados completos (IBEX 35, DAX 40, NASDAQ 100, etc.) en busca de oportunidades.

### Filtrado Inteligente "Solo Oportunidades"

Al seleccionar un índice, el sistema analiza **todos** sus componentes pero **solo muestra** aquellos con veredicto **🟢 COMPRA FUERTE**.

*   Esto elimina el ruido y te centra únicamente en los activos con la mejor estructura técnica y momento.
*   Si no se muestran resultados, significa que ningún activo del índice cumple los estrictos criterios de excelencia de la IA en este momento.

---

## 8. Analyst AI (Chat Financiero) 🤖💬

El sistema incluye un **Analista Virtual** basado en Google Gemini 1.5 Pro (con respaldo técnico de Chronos). Puedes preguntarle sobre cualquier activo analizado.

### Características Clave:
*   **Contexto Automático**: La IA ya "sabe" el precio, la tendencia y la volatilidad del activo que estás viendo. No necesitas explicárselo.
*   **Interpretación Humana**: Traduce los datos técnicos complejos (HMM, Impulso) a un lenguaje natural y comprensible.
*   **Seguridad y Estabilidad**:
    *   Funciona en segundo plano. Si la IA tarda en pensar, **no bloquea** el resto de la aplicación.
    *   **Modo "Descanso"**: Si usas la versión gratuita y alcanzas el límite de consultas (Error 429), la IA te avisará amablemente de que necesita una pausa de 30 segundos, sin colgar el sistema.

---

## 9. Flash Correction (Reflejos Rápidos) 🏁

Aunque el sistema de histéresis es muy estable, no es ciego. Posee **"reflejos ante el pánico"**:
- **Crash Detection**: Si el precio cae >2.5% con volumen, el sistema activa el veredicto de **Venta/Mantener inmediatamente**, ignorando la inercia alcista previa.
- **EMA-10 Check**: Si el precio rompe su tendencia de corto plazo (Media 10 días), se aplica una penalización del 15% al score.

---
*Nota: Esta herramienta es un asistente analítico basado en matemáticas avanzadas. No constituye asesoramiento financiero directo.*
