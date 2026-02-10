# Manual Técnico: Fundamentos Matemáticos de StockAI Pulse

Este documento detalla los cálculos estadísticos y financieros realizados por el motor de análisis de StockAI Pulse.

## 1. Cálculo de Rendimientos (Returns)

La aplicación utiliza **Rendimientos Logarítmicos** para el análisis de series temporales. A diferencia de los rendimientos simples, los logarítmicos son aditivos en el tiempo y manejan mejor la composición.

La fórmula utilizada es:
$$R_t = \ln\left(\frac{P_t}{P_{t-1}}\right)$$

Donde:
- $P_t$: Precio de cierre ajustado en el tiempo $t$.
- $P_{t-1}$: Precio de cierre ajustado en el tiempo anterior.

## 2. Diferencia de Rendimientos (Diff Returns)

Para detectar cambios en la "fuerza" o "impulso" del precio, calculamos la primera diferencia de los rendimientos. Esto actúa como una **aceleración** del movimiento del precio.

La fórmula es:
$$\Delta R_t = R_t - R_{t-1}$$

Un valor positivo en $\Delta R_t$ indica que el rendimiento está aumentando (aceleración alcista), mientras que un valor negativo indica una pérdida de momentum o aceleración bajista.

## 3. Ratio Rentabilidad / Riesgo por Estado

A diferencia de un análisis global, StockAI Pulse desglosa la eficiencia de cada **Estado de Mercado** (Régimen HMM) de forma independiente. Esto permite identificar qué regímenes son rentables y cuáles son destructivos de capital.

La fórmula para cada uno de los 3 estados es:
$$\text{Ratio R/R}_{\text{estado}} = \frac{\mu_{\text{estado}}}{\sigma_{\text{estado}}}$$

Donde:
- $\mu_{\text{estado}}$: Rendimiento medio logarítmico cuando el mercado está en ese estado.
- $\sigma_{\text{estado}}$: Volatilidad (desviación estándar) asociada exclusivamente a ese estado.

**Interpretación de la Calidad del Estado:**
- **Estado Eficiente (> 0.15)**: Tendencia limpia, ideal para posiciones largas.
- **Estado de Ruido (0 a 0.10)**: Movimiento positivo pero errático.
- **Estado Destructivo (< 0)**: Riesgo sistémico; la volatilidad supera al rendimiento medio.

## 4. Análisis de Impulso (Media de Diferencias)

El sistema analiza el valor medio de $\Delta R_t$ (aceleración) del estado actual de diferencias. 
- Si la media es **positiva**, el activo está ganando inercia alcista.
- Si la media es **negativa**, el activo está perdiendo fuerza (deceleración), lo que suele preceder a giros de mercado.

## 5. Motor de Recomendación (Sistema de Tres Pilares)

La recomendación final de la IA no se basa en un solo indicador, sino en un **Consenso de Peso (Scoring)** entre tres dimensiones:

1. **Eficiencia Estructural (40%)**: Basada en el **Ratio R/R del Estado Actual** de rendimientos. Evalúa si el entorno actual es "de calidad" para invertir.
2. **Momento Dinámico (30%)**: Basada en la **Media del Estado Actual de Diferencias**. Detecta si el movimiento tiene inercia o está agotado.
3. **Proyección Predictiva (30%)**: Basada en la **Pendiente del Forecast (Chronos)** a 10 días. Aporta la visión de futuro del modelo de lenguaje profundo.

Este sistema de triple filtro evita señales falsas y asegura que los veredictos de "COMPRA" o "VENTA" tengan una base matemática multidisciplinar.
