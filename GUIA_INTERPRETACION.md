# Guía de Interpretación Stock AI Pulse 🔭📈

Esta guía explica la lógica técnica detrás de las recomendaciones generadas por nuestra Inteligencia Artificial basada en Modelos Ocultos de Markov (HMM) y Redes Neuronales.

---

## 1. El Sistema de Consenso (Triple Pilar) 🏛️

La recomendación final ("COMPRA", "VENTA", etc.) es el resultado de una suma ponderada de tres modelos independientes. La puntuación va de 0 a 100.

| Pilar | Peso | Qué Analiza | Métrica Clave |
| :--- | :--- | :--- | :--- |
| **1. Estructura** | **40%** | Eficiencia del mercado actual | **Ratio R/R** (Rentabilidad/Riesgo) del Régimen HMM actual |
| **2. Impulso** | **30%** | Aceleración del precio | **Media** del Régimen HMM de Diferencias |
| **3. Proyección** | **30%** | Futuro probable (10 días) | **Pendiente** de la predicción del modelo Chronos (LLM) |

### Desglose de Puntuación

#### A. Pilar Estructural (Max 40 pts)
Se basa en la calidad del estado actual de rendimientos:
-   **100 pts**: Ratio R/R > 0.15 (Tendencia muy limpia)
-   **70 pts**: Ratio R/R > 0.05 (Tendencia positiva estándar)
-   **40 pts**: Ratio R/R >= 0 (Mercado lateral/ruido)
-   **10 pts**: Ratio R/R < 0 (Ineficiente/Riesgoso)

#### B. Pilar de Impulso (Max 30 pts)
Mide la "fuerza G" del movimiento:
-   **100 pts**: Media > 0.5 (Fuerte aceleración)
-   **75 pts**: Media > 0 (Aceleración moderada)
-   **30 pts**: Media > -0.5 (Desaceleración/Frenada)
-   **0 pts**: Media <= -0.5 (Caída libre)

#### C. Pilar de Proyección (Max 30 pts)
Mira hacia el futuro con IA Generativa:
-   **100 pts**: Tendencia > +3% en 10 días
-   **70 pts**: Tendencia > 0%
-   **20 pts**: Tendencia plana o ligeramente bajista
-   **0 pts**: Tendencia < -3% (Proyección de caída fuerte)

---

## 2. Veredictos y Criterios 🎯

La suma de los puntos anteriores genera el veredicto final:

| Puntuación Total | Veredicto | Significado | Estrategia Sugerida |
| :--- | :--- | :--- | :--- |
| **>= 80** | **🟢 COMPRA FUERTE** | Estructura perfecta + Inercia + Futuro alcista. | **Entrada agresiva**. Ideal para aumentar posición. |
| **60 - 79** | **🟡 COMPRA** | Estructura positiva, pero falla algún pilar (ej. poco impulso). | **Entrada escalonada**. Buscar confirmación de precio. |
| **40 - 59** | **⚪ MANTENER** | Zona de equilibrio. Fuerzas alcistas y bajistas empatadas. | **No operar**. Si tienes posición, mantenla con Stop Loss ajustado. |
| **20 - 39** | **🟠 VENTA** | Pérdida de eficiencia. El riesgo empieza a superar al beneficio. | **Reducir riesgo**. Cerrar parciales o ajustar stops muy ceñidos. |
| **< 20** | **🔴 VENTA FUERTE** | Colapso estructural y aceleración negativa. | **Salida inmediata**. No intentar "cazar el suelo". |

---

## 3. Glosario de Justificaciones 🗣️

Aquí explicamos el significado exacto de las frases que utiliza la IA para justificar su recomendación:

| Frase de la IA | Qué significa realmente |
| :--- | :--- |
| **"Eficiencia estructural óptima con fuerte inercia alcista confirmada."** | **El escenario ideal.** El precio sube de forma limpia (sin apenas retrocesos) y además está acelerando. Es una tendencia robusta y saludable. |
| **"Estructura positiva. El mercado muestra calidad y potencial de crecimiento."** | **Buen momento.** La tendencia es alcista y el riesgo es bajo, aunque quizás le falta un poco de "explosividad" o aceleración para ser perfecta. |
| **"Zona de equilibrio. Los pilares muestran señales mixtas o estables."** | **Indecisión.** Puede que el precio suba pero con mucha volatilidad (ruido), o que esté lateral. No hay una ventaja estadística clara para entrar. |
| **"Pérdida de eficiencia. Se detecta ruido o sesgo bajista en el impulso."** | **Precaución.** La tendencia se está ensuciando (muchos dientes de sierra) o está perdiendo fuerza. Aumentan las probabilidades de corrección. |
| **"Deterioro crítico. Colapso de eficiencia y aceleración negativa."** | **Peligro.** El activo está cayendo con fuerza o con mucha volatilidad. Es un entorno tóxico para el capital. |

---

## 4. Diccionario de Alertas de la IA 🔍

Cuando el sistema detecta una anomalía, añade una nota entre paréntesis. Aquí explicamos qué significan y qué acción tomar:

| Alerta | Significado Técnico | Acción Recomendada |
| :--- | :--- | :--- |
| **Riesgo elevado (R/R negativo)** | El estado actual es destructivo; la volatilidad es mayor que el retorno promedio. | **Evitar nuevas entradas** hasta que cambie el régimen. |
| **Deceleración detectada** | El precio sube, pero el impulso (segunda derivada) está bajando. Signo de agotamiento. | **Vigilar**. No perseguir el precio. Riesgo de techo de mercado. |
| **Proyección bajista** | El modelo neuronal anticipa una caída en los próximos 10 días, contradiciendo quizás la subida actual. | **Cautela**. El modelo detecta patrones de distribución no visibles a simple vista. |

---

## 5. Consejos de Uso Práctico

1.  **Confirma la Inercia**: Un "Impulso consolidado" (Estado HMM estable) es mucho más fiable que uno que cambia cada día.
2.  **Mira las Probabilidades**: En el panel lateral, si el estado actual tiene una probabilidad cercana al **90-100%**, la señal es muy robusta. Si está cerca del 50-60%, el mercado está indeciso.
3.  **Usa los dos HMM**:
    *   **HMM Rep (Retornos)** te dice "Dónde estamos" (Alcista, Bajista, Lateral).
    *   **HMM Diff (Impulso)** te dice "A qué velocidad vamos".
    *   *Ejemplo*: Si HMM Rep es "Alcista" pero HMM Diff es "Volátil/Bajista", el movimiento está perdiendo gasolina.

---

## 6. Índices Globales y Filtrado 🌍

La nueva sección de **Índices Globales** permite analizar mercados completos (IBEX 35, DAX 40, NASDAQ 100, etc.) en busca de oportunidades.

### Filtrado Inteligente "Solo Oportunidades"

Al seleccionar un índice, el sistema analiza **todos** sus componentes pero **solo muestra** aquellos con veredicto **🟢 COMPRA FUERTE**.

*   Esto elimina el ruido y te centra únicamente en los activos con la mejor estructura técnica y momento.
*   Si no se muestran resultados, significa que ningún activo del índice cumple los estrictos criterios de excelencia de la IA en este momento.

---

## 7. Analyst AI (Chat Financiero) 🤖💬

El sistema incluye un **Analista Virtual** basado en Google Gemini 2.0 Flash. Puedes preguntarle sobre cualquier activo analizado.

### Características Clave:
*   **Contexto Automático**: La IA ya "sabe" el precio, la tendencia y la volatilidad del activo que estás viendo. No necesitas explicárselo.
*   **Interpretación Humana**: Traduce los datos técnicos complejos (HMM, Impulso) a un lenguaje natural y comprensible.
*   **Seguridad y Estabilidad**:
    *   Funciona en segundo plano. Si la IA tarda en pensar, **no bloquea** el resto de la aplicación.
    *   **Modo "Descanso"**: Si usas la versión gratuita y alcanzas el límite de consultas (Error 429), la IA te avisará amablemente de que necesita una pausa de 30 segundos, sin colgar el sistema.

---

## 8. Nota sobre la Estabilidad del Sistema 🛡️

Hemos implementado protecciones avanzadas "Anti-Crash":

*   **Carga Perezosa (Lazy Loading)**: Los modelos pesados (Chronos) solo se activan cuando son necesarios, acelerando el inicio.
*   **Predicción Asíncrona**: Los cálculos matemáticos complejos se realizan en hilos paralelos para mantener la fluidez de la interfaz.
*   **Fallback Estadístico**: En el improbable caso de que el modelo de IA falle, el sistema cambiará automáticamente a un modelo estadístico robusto (Movimiento Browniano Geométrico) para garantizar que siempre tengas una proyección disponible.

---
*Nota: Esta herramienta es un asistente analítico basado en matemáticas avanzadas. No constituye asesoramiento financiero directo.*
