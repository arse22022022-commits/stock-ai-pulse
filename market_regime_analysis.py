import yfinance as yf
import pandas as pd
import numpy as np
from hmmlearn import hmm
import matplotlib.pyplot as plt

def analyze_stock_regimes(ticker="NVDA", start_date="2020-01-01", end_date="2025-01-01"):
    print(f"Descargando datos para {ticker}...")
    data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)
    
    # Manejar MultiIndex si es necesario (yfinance > 0.2.40)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Con auto_adjust=True, 'Close' es el precio ajustado
    price_col = 'Close'
    data['Returns'] = np.log(data[price_col] / data[price_col].shift(1))
    # Calcular volatilidad (rango diario)
    data['Range'] = (data['High'] - data['Low']) / data['Low']
    
    data.dropna(inplace=True)
    
    # Preparar datos para el modelo HMM
    # Usamos Retornos y Rango (Volatilidad) como observaciones
    X = data[['Returns', 'Range']].values
    
    print("Entrenando Modelo Oculto de Markov (HMM)...")
    model = hmm.GaussianHMM(n_components=3, covariance_type="full", n_iter=1000, random_state=42)
    model.fit(X)
    
    # Predecir los estados (regímenes)
    data['Regime'] = model.predict(X)
    
    # Visualización
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
    
    # Gráfico de Precios con colores por régimen
    colors = ['green', 'red', 'blue']
    for i in range(model.n_components):
        mask = data['Regime'] == i
        ax1.scatter(data.index[mask], data[price_col][mask], 
                   label=f'Régimen {i}', s=10, color=colors[i])
    
    ax1.set_title(f"Análisis de Regímenes de Mercado para {ticker} (HMM)")
    ax1.set_ylabel("Precio Ajustado ($)")
    ax1.legend()
    
    # Gráfico de los regímenes a lo largo del tiempo
    ax2.step(data.index, data['Regime'], where='post', color='gray', alpha=0.5)
    ax2.set_title("Estados Detectados (0, 1, 2)")
    ax2.set_ylabel("Estado")
    ax2.set_xlabel("Fecha")
    
    plt.tight_layout()
    output_path = "market_regimes_nvda.png"
    plt.savefig(output_path)
    print(f"Análisis completado. Gráfico guardado en {output_path}")
    
    # Mostrar estadísticas por régimen
    print("\nEstadísticas por Régimen:")
    for i in range(model.n_components):
        regime_data = data[data['Regime'] == i]
        print(f"Régimen {i}: {len(regime_data)} días")
        print(f"  Media de Retorno: {regime_data['Returns'].mean():.4f}")
        print(f"  Volatilidad Media: {regime_data['Range'].mean():.4f}")

if __name__ == "__main__":
    analyze_stock_regimes()
