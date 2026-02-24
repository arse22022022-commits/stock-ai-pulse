from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
import sys

# CRITICAL: Set threading environment variables BEFORE any numerical imports
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import yfinance as yf
import pandas as pd
import numpy as np
from hmmlearn import hmm
from datetime import datetime, timedelta
import re
import logging
from concurrent.futures import ThreadPoolExecutor
import time
import asyncio
import torch
torch.set_num_threads(1)
if torch.get_num_interop_threads() > 1:
    torch.set_num_interop_threads(1)
# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv

# Load environment variables from .env file
# We check both the root and the backend/ folder for the .env file
if os.path.exists(".env"):
    load_dotenv(".env")
    logger.info("Cargando .env desde el directorio raíz")
elif os.path.exists("backend/.env"):
    load_dotenv("backend/.env")
    logger.info("Cargando .env desde el directorio /backend")
else:
    logger.warning("No se encontró ningún archivo .env")

# specialized executors for different task types
# Specialized executors for different task types
# io_executor: Network/Disk bound (yfinance, Gemini fallback)
io_executor = ThreadPoolExecutor(max_workers=30)
# cpu_executor: Computationally intensive (HMM, Chronos)
# Strictly 1 worker on Windows to prevent any possibility of library deadlocks
cpu_executor = ThreadPoolExecutor(max_workers=1)

from backend.app.services.chronos import chronos_service

# Redundant Local Chronos loading removed in favor of chronos_service
pipeline = chronos_service.pipeline
logger.info("Sistema de predicción Chronos vinculado desde servicios centrales")

# ... (rest of imports)
VERSION = "v1.3.1-fix-prediction"

from pydantic import BaseModel

class ChatRequest(BaseModel):
    ticker: str
    price: float
    hmm_state: str
    impulse_state: str
    user_query: str

class ChatResponse(BaseModel):
    response: str

app = FastAPI()
logger.info(f"Starting StockAI Pulse Backend - {VERSION}")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos (Frontend React compilado)
# Se asume que la carpeta 'static' existe en el mismo directorio (copiada por Docker)
if os.path.exists("static"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    if os.path.exists("static/index.html"):
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "Frontend no encontrado (Ejecute build y asegúrese de tener la carpeta static)"

# Catch-all para React Router (cualquier ruta no API redirige a index.html)
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    if request.url.path.startswith("/api"):
        return {"detail": "API endpoint not found"}
    if os.path.exists("static/index.html"):
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"detail": "Not found"}

# ... (rest of the code)

# Input validation
def validate_ticker(ticker: str) -> bool:
    """
    Validate ticker format:
    - Standard: 1-5 uppercase letters (e.g., AAPL, MSFT)
    - International: letters/numbers + .SUFFIX (e.g., MTS.MC, VOW3.DE, 7203.T)
    """
    return bool(re.match(r'^[A-Z0-9]{1,10}(\.[A-Z]{1,3})?$', ticker))

# Rate limiting (requires slowapi: pip install slowapi)
try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return HTTPException(
            status_code=429,
            detail="Demasiadas peticiones. Intenta de nuevo en un minuto."
        )
    
    RATE_LIMIT_ENABLED = True
    logger.info("Rate limiting habilitado")
except ImportError:
    logger.warning("slowapi no instalada. Rate limiting deshabilitado")
    logger.info("Para habilitar rate limiting: pip install slowapi")
    RATE_LIMIT_ENABLED = False
    limiter = None

from backend.app.services.analysis import train_hmm_returns, train_hmm_diff, generate_ai_recommendation

# Response cache (TTL: 5 minutes) - DISABLED FOR VERIFICATION
response_cache = {}
CACHE_TTL = 0  # Set to 0 to bypass cache

def get_from_cache(cache_key: str):
    return None # Always miss for now

def save_to_cache(cache_key: str, data: dict):
    """Save response to cache with current timestamp"""
    response_cache[cache_key] = (datetime.now(), data)
    logger.debug(f"Saved to cache: {cache_key}")

# Redundant functions removed (using backend.app.services.analysis)
def train_hmms_combined(data: pd.DataFrame):
    """Run both HMM trainings in a single synchronous block to save thread overhead"""
    logger.debug("Iniciando entrenamiento combinado de HMMs")
    r_reg, r_prob, r_stats = train_hmm_returns(data)
    d_reg, d_prob, d_stats = train_hmm_diff(data)
    return r_reg, r_prob, r_stats, d_reg, d_prob, d_stats

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint to monitor server status"""
    return {
        "status": "healthy",
        "chronos_loaded": pipeline is not None,
        "rate_limiting": RATE_LIMIT_ENABLED,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/analyze/{ticker}")
@limiter.limit("10/minute") if RATE_LIMIT_ENABLED and limiter else lambda f: f
async def analyze_stock(ticker: str, request: Request):
    # Validación de input
    if not validate_ticker(ticker):
        logger.warning(f"Ticker inválido recibido: '{ticker}'")
        raise HTTPException(
            status_code=400,
            detail=f"Ticker inválido '{ticker}'. Use formato: AAPL, MSFT, MTS.MC, VOW3.DE"
        )
    
    logger.info(f"Análisis solicitado para: {ticker}")
    
    # Check cache first
    cache_key = f"{ticker}_{datetime.now().date()}"
    cached_response = get_from_cache(cache_key)
    if cached_response:
        return cached_response
    
    # Track start time for performance measurement
    start_time = time.time()
    
    try:
        # Extender end_date un día para asegurar que yfinance incluya datos intradía de hoy si el mercado está abierto
        end_date = datetime.now() + timedelta(days=1)
        start_date = datetime.now() - timedelta(days=365)
        
        # Obtener datos de forma asíncrona para no bloquear el loop
        logger.debug(f"Descargando datos para {ticker} desde {start_date.date()} hasta {end_date.date()}")
        ticker_obj = yf.Ticker(ticker)
        
        loop = asyncio.get_running_loop()
        # Fetch history and info concurrently in the executor to save time
        def fetch_data():
            hist = ticker_obj.history(start=start_date, end=end_date, auto_adjust=True)
            info = ticker_obj.info
            return hist, info
            
        data, info = await asyncio.wait_for(
            loop.run_in_executor(io_executor, fetch_data),
            timeout=25.0
        )
        currency = info.get('currency', 'USD')
        
        if data.empty:
            logger.error(f"No se encontraron datos para el ticker: {ticker}")
            raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' no encontrado o sin datos disponibles")
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        price_col = 'Close'
        data['Returns'] = np.log(data[price_col] / data[price_col].shift(1))
        data['Diff_Returns'] = data['Returns'].diff()
        
        # Calculate Volume Metrics (RVOL)
        data['Vol_SMA'] = data['Volume'].rolling(window=20).mean()
        data['RVOL'] = data['Volume'] / data['Vol_SMA']
        
        data.dropna(inplace=True)
        
        # Validar datos suficientes
        if len(data) < 60:
            logger.error(f"Datos insuficientes para {ticker}: {len(data)} días (mínimo: 60)")
            raise HTTPException(
                status_code=400,
                detail=f"Datos insuficientes: {len(data)} días disponibles. Se requieren al menos 60 días de datos históricos para análisis confiable."
            )
        
        logger.info(f"Datos cargados: {len(data)} días para {ticker}")
        
        # HMM training (CPU Bound)
        logger.debug("Iniciando entrenamiento de HMMs")
        hmm_start = time.time()
        
        # We use a combined function to ensure each asset uses exactly ONE worker
        # and doesn't compete for threads within itself.
        loop = asyncio.get_running_loop()
        
        # Add a safety timeout (60s) for the combined HMM training to allow queue waiting
        regimes_ret, probs_ret, final_ret_stats, regimes_diff, probs_diff, final_diff_stats = await asyncio.wait_for(
            loop.run_in_executor(cpu_executor, train_hmms_combined, data),
            timeout=60.0
        )
        
        hmm_duration = time.time() - hmm_start
        logger.debug(f"HMM completado en {hmm_duration:.2f}s")


        # LLM Forecast (Chronos) with confidence bands
        prediction_length = 10
        forecast_result = []
        last_date = data.index[-1]
        
        if chronos_service.enabled:
            try:
                # Use unified chronos_service prediction logic
                forecast_data = await asyncio.wait_for(
                    loop.run_in_executor(cpu_executor, lambda: chronos_service.predict(data[price_col].values, prediction_length)),
                    timeout=60.0
                )
                
                if forecast_data:
                    for i in range(prediction_length):
                        forecast_result.append({
                            "date": (last_date + timedelta(days=i+1)).strftime("%Y-%m-%d"),
                            "price": forecast_data["prices"][i],
                            "price_low": forecast_data["lows"][i],
                            "price_high": forecast_data["highs"][i],
                            "type": "forecast"
                        })
                    logger.debug("Predicción Chronos completada con éxito")
                else:
                    raise ValueError("Chronos service returned empty data")
            except Exception as e:
                logger.warning(f"Error en predicción Chronos: {e}. Usando fallback estadístico")
                lp, ar, vol = float(data[price_col].iloc[-1]), data['Returns'].mean(), data['Returns'].std()
                for i in range(prediction_length):
                    # Simple geometric brownian motion fallback with 1.96 * std for 95% band
                    drift = np.exp((ar - 0.5 * vol**2) * (i+1))
                    uncertainty = 1.96 * vol * np.sqrt(i+1)
                    forecast_result.append({
                        "date": (last_date + timedelta(days=i+1)).strftime("%Y-%m-%d"), 
                        "price": float(lp * drift),
                        "price_low": float(lp * drift * np.exp(-uncertainty)),
                        "price_high": float(lp * drift * np.exp(uncertainty)),
                        "type": "forecast"
                    })
        else:
            lp, ar, vol = float(data[price_col].iloc[-1]), data['Returns'].mean(), data['Returns'].std()
            for i in range(prediction_length):
                drift = np.exp((ar - 0.5 * vol**2) * (i+1))
                uncertainty = 1.96 * vol * np.sqrt(i+1)
                forecast_result.append({
                    "date": (last_date + timedelta(days=i+1)).strftime("%Y-%m-%d"), 
                    "price": float(lp * drift),
                    "price_low": float(lp * drift * np.exp(-uncertainty)),
                    "price_high": float(lp * drift * np.exp(uncertainty)),
                    "type": "forecast"
                })

        # Calcular veredictos históricos para el coloreado del gráfico y estabilidad del veredicto
        from backend.app.services.analysis import get_historical_verdicts
        hist_verdicts, smoothed_scores = get_historical_verdicts(data, regimes_ret, regimes_diff, final_ret_stats, final_diff_stats)
        
        # Preparar historial
        result = []
        for i in range(len(data)):
            result.append({
                "date": data.index[i].strftime("%Y-%m-%d"),
                "price": float(data[price_col].iloc[i]),
                "regime": int(hist_verdicts[i]), # Usamos el veredicto con histéresis (0:Hold, 1:Buy, 2:Sell)
                "rvol": float(data['RVOL'].iloc[i]) if 'RVOL' in data.columns else 1.0
            })
        
        current_price = float(data[price_col].iloc[-1])
        previous_price = float(data[price_col].iloc[-2])
        change_pct = ((current_price - previous_price) / previous_price) * 100
        
        # LLM Recommendation (Estabilizada con Histéresis y Supervisor de Estado)
        ai_rec = generate_ai_recommendation(
            data, regimes_ret, regimes_diff, probs_ret, probs_diff, 
            forecast_result, final_ret_stats, final_diff_stats,
            stable_state=hist_verdicts[-1],
            smoothed_score=smoothed_scores[-1]
        )
        
        # Calcular Ratio Rentabilidad/Riesgo del ticker (periodo anual)
        mean_ret = data['Returns'].mean()
        std_ret = data['Returns'].std()
        risk_reward_ratio = float(mean_ret / std_ret) if std_ret != 0 else 0.0

        # Calculate total processing time
        total_time = time.time() - start_time
        logger.info(f"Análisis completado exitosamente para {ticker} en {total_time:.2f}s (Precio: {currency} {current_price:.2f}, Cambio: {change_pct:+.2f}%)")
        # Helper function to sanitize NaN/Infinity for JSON
        def sanitize_for_json(obj):
            """Replace NaN and Infinity with None for JSON compliance"""
            if isinstance(obj, float):
                if np.isnan(obj) or np.isinf(obj):
                    return None
                return obj
            elif isinstance(obj, dict):
                return {k: sanitize_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [sanitize_for_json(item) for item in obj]
            return obj
        
        # Combinar histórico y forecast
        response_data = {
            "ticker": ticker,
            "currency": currency,
            "current_price": current_price,
            "change_pct": change_pct,
            "risk_reward_ratio": risk_reward_ratio,
            "history": result,
            "forecast": forecast_result,
            "recommendation": ai_rec,
            "current_regime_ret": int(regimes_ret[-1]),
            "current_regime_diff": int(regimes_diff[-1]),
            "regime_probs_ret": probs_ret[-1].tolist(),
            "regime_probs_diff": probs_diff[-1].tolist(),
            "state_stats_ret": final_ret_stats,
            "state_stats_diff": final_diff_stats,
            "processing_time": round(total_time, 2)
        }
        
        # Sanitize for JSON compliance (replace NaN/Infinity with None)
        response_data = sanitize_for_json(response_data)
        
        # Save to cache
        save_to_cache(cache_key, response_data)
        
        return response_data
        
    except HTTPException:
        # Re-raise HTTP exceptions (already properly formatted)
        raise
    except ValueError as e:
        logger.error(f"Error de validación de datos para {ticker}: {e}")
        raise HTTPException(status_code=400, detail=f"Error procesando datos: {str(e)}")
    except ConnectionError as e:
        logger.error(f"Error de conexión al obtener datos para {ticker}: {e}")
        raise HTTPException(status_code=503, detail="Servicio de datos temporalmente no disponible. Intente nuevamente.")
    except Exception as e:
        logger.error(f"Error inesperado procesando {ticker}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor. Por favor contacte al administrador.")

@app.post("/api/portfolio")
async def analyze_portfolio(tickers: list[str], request: Request):
    """Analyze multiple tickers and provide portfolio-level insights"""
    if not tickers:
        raise HTTPException(status_code=400, detail="Se requiere al menos un ticker")

    results = []
    # ULTIMATE STABILITY: Sequential processing for portfolio on Windows
    # Instead of parallel, we process each asset one by one.
    # This prevents CPU saturation and ensures the event loop remains responsive.
    for ticker in tickers:
        if await request.is_disconnected():
            logger.warning(f"El cliente se ha desconectado. Abortando el análisis de la cartera en el ticker {ticker}.")
            break
            
        try:
            res = await analyze_stock(ticker, request)
            results.append(res)
        except Exception as e:
            logger.error(f"Error analizando {ticker} en portfolio: {e}")
            continue

    if not results:
        raise HTTPException(status_code=400, detail="No se pudo analizar ningún activo del portfolio")

    # Aggregate stats for rebalancing
    # 1. Regime distribution
    reg_list = [r['current_regime_ret'] for r in results]
    bullish_count = reg_list.count(1)
    stable_count = reg_list.count(0)
    volatile_count = reg_list.count(2)
    
    # 2. Reasoning & Advice logic
    total = len(results)
    bullish_ratio = (bullish_count / total) * 100
    risk_ratio = (volatile_count / total) * 100
    
    # --- 3. ADVANCED REASONING ENGINE ---
    
    # Categorize assets
    buckets = {
        "STRONG_BUY": [], "COMPRA": [], "MANTENER": [], "VENTA": [], "VENTA_FUERTE": []
    }
    
    for r in results:
        v = r['recommendation']['verdict'].replace(" ", "_") # Normalize VENTA FUERTE -> VENTA_FUERTE
        if v in buckets:
            buckets[v].append(r['ticker'])
        elif v == "COMPRA_FUERTE": # Handle mapping
            buckets["STRONG_BUY"].append(r['ticker'])
            
    # Calculate weighted metrics
    avg_bullishness = np.mean([1 if r['current_regime_ret'] == 1 else 0 for r in results]) * 100
    
    # Identify Leaders (Convergent Bullish)
    leaders = [r['ticker'] for r in results if r['current_regime_ret'] == 1 and r['current_regime_diff'] == 1]
    
    # Identify Warnings (Divergent: Price up but Impulse down)
    warnings = []
    for r in results:
        if r['change_pct'] > 0 and r['current_regime_diff'] == 2:
            warnings.append(r['ticker'])
            
    # Construction of the Narrative
    advice_parts = []
    
    # A. Contexto General
    if risk_ratio > 40:
        advice_parts.append(f"⚠️ ALERTA: Cartera en zona de turbulencia ({risk_ratio:.0f}% volatilidad).")
        risk_level = "Alto"
    elif bullish_ratio > 60:
        advice_parts.append(f"✅ SÓLIDA: Estructura técnica dominante alcista ({bullish_ratio:.0f}%).")
        risk_level = "Bajo"
    else:
        advice_parts.append(f"⚖️ MIXTA: Equilibrio entre activos estables y en desarrollo.")
        risk_level = "Medio"
        
    # B. Acción Específica (Ventas/Limpieza)
    to_sell = buckets["VENTA"] + buckets["VENTA_FUERTE"]
    if to_sell:
        advice_parts.append(f"ACCIÓN PRIORITARIA: Se detecta debilidad crítica en {', '.join(sorted(to_sell))}. Considerar rotación inmediata para proteger capital.")
    else:
        # Si NO hay ventas, dar consejo de optimización
        if buckets["MANTENER"]:
            advice_parts.append(f"• OPTIMIZACIÓN: {', '.join(sorted(buckets['MANTENER']))} están en fase lateral; vigilar para acumular si rompen al alza.")
        else:
            advice_parts.append("MANTENIMIENTO: Todos los activos contribuyen positivamente. No se requieren ventas.")

    # C. Oportunidades (Compras)
    strong_opportunities = buckets["STRONG_BUY"]
    if strong_opportunities:
        advice_parts.append(f"• LÍDERES: {', '.join(sorted(strong_opportunities))} muestran el mejor momentum para sobre-ponderar.")
        
    # D. Notas Técnicas (Divergencias)
    if warnings:
        advice_parts.append(f"• OJO AVIZOR: {', '.join(sorted(warnings))} suben de precio pero con calidad interna (impulso) deteriorada.")

    full_advice = "\n\n".join(advice_parts)
    
    # Map back to old variable names for return compatibility
    alerts = warnings
    to_remove = to_sell
    
    # 4. Integrate Gemini AI Analyst
    portfolio_stats = {
        "total_assets": total,
        "bullish_count": bullish_count,
        "bullish_ratio": bullish_ratio,
        "volatile_count": volatile_count,
        "risk_ratio": risk_ratio,
        "stable_count": stable_count
    }
    
    from backend.app.services.llm import llm_service
    ai_insight = await llm_service.evaluate_portfolio_async(portfolio_stats)

    return {
        "assets": results,
        "summary": {
            "total_assets": total,
            "regime_distribution": {
                "bullish": bullish_count,
                "stable": stable_count,
                "volatile": volatile_count
            },
            "risk_level": risk_level,
            "advice": full_advice,
            "bullish_ratio": bullish_ratio,
            "risk_ratio": risk_ratio,
            "leaders": leaders,
            "alerts": alerts,
            "to_remove": to_remove,
            "ai_insight": ai_insight
        }
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        from backend.app.services.llm import llm_service
        # Prepare context data
        context = {
            "ticker": request.ticker,
            "price": request.price,
            "hmm_state": request.hmm_state,
            "impulse_state": request.impulse_state,
            "user_query": request.user_query
        }
        
        response_text = await llm_service.generate_market_explanation_async(context)
        return ChatResponse(response=response_text)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
