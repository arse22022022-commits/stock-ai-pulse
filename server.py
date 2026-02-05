from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
import yfinance as yf
import pandas as pd
import numpy as np
from hmmlearn import hmm
from datetime import datetime, timedelta

# Inicializar pipeline como None globalmente
pipeline = None
torch_lib = None

try:
    import torch as torch_lib
    from chronos import ChronosPipeline
    pipeline = ChronosPipeline.from_pretrained(
        "amazon/chronos-t5-tiny",
        device_map="cpu",
        torch_dtype=torch_lib.float32,
    )
    print(">>> Modelo Chronos (LLM) cargado con éxito.")
except Exception as e:
    print(f">>> Aviso: El modelo LLM (Chronos) no está disponible ({e}). Usando modo estadística simple.")

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/analyze/{ticker}")
async def analyze_stock(ticker: str):
    print(f">>> Recibida solicitud para: {ticker}")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # Obtener datos
        data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)
        if data.empty:
            print(f">>> Error: No hay datos para {ticker}")
            raise HTTPException(status_code=404, detail="Ticker no encontrado")
            
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        price_col = 'Close'
        data['Returns'] = np.log(data[price_col] / data[price_col].shift(1))
        data['Range'] = (data['High'] - data['Low']) / data['Low']
        data.dropna(inplace=True)
        
        X = data[['Returns', 'Range']].values
        
        # HMM Model
        model = hmm.GaussianHMM(n_components=3, covariance_type="full", n_iter=100)
        model.fit(X)
        regimes = model.predict(X)
        
        # Prepare response history
        result = []
        for i in range(len(data)):
            result.append({
                "date": data.index[i].strftime("%Y-%m-%d"),
                "price": float(data[price_col].iloc[i]),
                "regime": int(regimes[i])
            })
            
        # LLM Forecast with Chronos
        prediction_length = 10
        forecast_result = []
        last_date = data.index[-1]

        if pipeline:
            try:
                # Convert daily prices to a torch tensor
                context = torch_lib.tensor(data[price_col].values)
                forecast = pipeline.predict(context, prediction_length) 
                forecast_median = np.median(forecast[0].numpy(), axis=0)
                
                for i in range(prediction_length):
                    forecast_date = last_date + timedelta(days=i+1)
                    forecast_result.append({
                        "date": forecast_date.strftime("%Y-%m-%d"),
                        "price": float(forecast_median[i]),
                        "type": "forecast"
                    })
            except Exception as fe:
                print(f">>> Error en predicción Chronos: {fe}")
                # Fallback dentro de la petición
                last_price = float(data[price_col].iloc[-1])
                avg_return = data['Returns'].mean()
                for i in range(prediction_length):
                    forecast_date = last_date + timedelta(days=i+1)
                    forecast_price = last_price * np.exp(avg_return * (i+1))
                    forecast_result.append({
                        "date": forecast_date.strftime("%Y-%m-%d"),
                        "price": float(forecast_price),
                        "type": "forecast"
                    })
        else:
            # Fallback simple
            last_price = float(data[price_col].iloc[-1])
            avg_return = data['Returns'].mean()
            for i in range(prediction_length):
                forecast_date = last_date + timedelta(days=i+1)
                forecast_price = last_price * np.exp(avg_return * (i+1))
                forecast_result.append({
                    "date": forecast_date.strftime("%Y-%m-%d"),
                    "price": float(forecast_price),
                    "type": "forecast"
                })

        # Get latest stats
        latest_regime = int(regimes[-1])
        current_price = float(data[price_col].iloc[-1])
        previous_price = float(data[price_col].iloc[-2])
        change_pct = ((current_price - previous_price) / previous_price) * 100
        
        print(f">>> Análisis completado con éxito para {ticker}")
        return {
            "ticker": ticker,
            "current_price": current_price,
            "change_pct": change_pct,
            "current_regime": latest_regime,
            "history": result,
            "forecast": forecast_result
        }
        
    except Exception as e:
        print(f">>> Error general procesando {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
