# StockAI Pulse 📈🤖

Un dashboard premium de análisis bursátil que combina **Modelos Ocultos de Markov (HMM)** para detectar regímenes de mercado y **LLMs (Amazon Chronos)** para predicción de precios.

## 🚀 Características
- **Glassmorphism Design:** Interfaz moderna, oscura y elegante.
- **Análisis de Regímenes:** Identifica estados del mercado (Alcista, Estable, Volátil).
- **Predicción con IA:** Utiliza el modelo Chronos de Amazon para predecir los próximos 10 días.
- **Datos en Tiempo Real:** Integración con `yfinance`.

## 🛠️ Instalación

### Backend (Python)
```bash
# Instalar dependencias
pip install fastapi uvicorn yfinance pandas numpy hmmlearn chronos-forecasting torch
# Ejecutar servidor
python server.py
```

### Frontend (React)
```bash
cd stock-ai-app
npm install
npm run dev
```

## 📝 Nota sobre el modelo de IA
El proyecto incluye un fallback estadístico. Si el modelo Chronos no se carga (debido a requisitos de hardware o dependencias), el sistema usará un modelo de promediado inteligente para garantizar que el gráfico siempre funcione.

---
Creado con Antigravity.
