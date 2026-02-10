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

## 3. Ratio Rentabilidad / Riesgo

Este ratio permite evaluar la calidad del rendimiento obtenido en relación a la volatilidad soportada para el ticker analizado durante el periodo de estudio (último año). Es una versión simplificada del *Ratio de Sharpe*.

La fórmula es:
$$\text{Ratio Rentabilidad/Riesgo} = \frac{\mu}{\sigma}$$

Donde:
- $\mu$: Rendimiento medio logarítmico del periodo.
- $\sigma$: Desviación estándar de los rendimientos logarítmicos (volatilidad).

**Interpretación:**
- **> 0.1**: El activo genera retornos positivos consistentes con su riesgo.
- **0 a 0.1**: Rendimiento positivo pero con alta volatilidad asociada.
- **< 0**: El activo tiene un sesgo negativo en el periodo analizado.
