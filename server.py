from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
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

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    logger.info("Modelo Chronos (LLM) cargado con éxito")
except Exception as e:
    logger.warning(f"El modelo LLM (Chronos) no está disponible: {e}. Usando modo estadística simple")

# ... (rest of imports)
VERSION = "v1.2.0-triple-pillar"

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

# Response cache (TTL: 5 minutes)
response_cache = {}
CACHE_TTL = 300  # seconds

def get_from_cache(cache_key: str):
    """Get cached response if still valid"""
    if cache_key in response_cache:
        cached_time, cached_data = response_cache[cache_key]
        if (datetime.now() - cached_time).total_seconds() < CACHE_TTL:
            logger.info(f"Cache HIT for {cache_key}")
            return cached_data
        else:
            # Expired cache entry
            del response_cache[cache_key]
            logger.debug(f"Cache EXPIRED for {cache_key}")
    logger.debug(f"Cache MISS for {cache_key}")
    return None

def save_to_cache(cache_key: str, data: dict):
    """Save response to cache with current timestamp"""
    response_cache[cache_key] = (datetime.now(), data)
    logger.debug(f"Saved to cache: {cache_key}")

# HMM training functions for parallel execution
def train_hmm_returns(data: pd.DataFrame):
    """Train HMM on Returns data"""
    returns_data = data[['Returns']].values
    model_ret = hmm.GaussianHMM(n_components=3, covariance_type="full", n_iter=1000, random_state=42)
    model_ret.fit(returns_data)
    raw_regimes_ret = model_ret.predict(returns_data)
    raw_probs_ret = model_ret.predict_proba(returns_data)
    
    ret_stats_raw = []
    for i in range(3):
        r = data.iloc[raw_regimes_ret == i]['Returns']
        ret_stats_raw.append({'id': i, 'mean': r.mean() if not r.empty else -999, 'std': r.std() if not r.empty else 999})
    
    bull_id_ret = sorted(ret_stats_raw, key=lambda x: x['mean'], reverse=True)[0]['id']
    rem_ret = [s for s in ret_stats_raw if s['id'] != bull_id_ret]
    vol_id_ret = sorted(rem_ret, key=lambda x: x['std'], reverse=True)[0]['id']
    stab_id_ret = [s['id'] for s in ret_stats_raw if s['id'] not in [bull_id_ret, vol_id_ret]][0]
    
    map_ret = {stab_id_ret: 0, bull_id_ret: 1, vol_id_ret: 2}
    regimes_ret = np.array([map_ret[r] for r in raw_regimes_ret])
    
    probs_ret = np.zeros_like(raw_probs_ret)
    probs_ret[:, 0] = raw_probs_ret[:, stab_id_ret]
    probs_ret[:, 1] = raw_probs_ret[:, bull_id_ret]
    probs_ret[:, 2] = raw_probs_ret[:, vol_id_ret]
    
    final_ret_stats = []
    for i in range(3):
        r = data.iloc[regimes_ret == i]['Returns']
        if not r.empty:
            m = float(r.mean() * 100)
            s = float(r.std() * 100)
            ratio = m / s if s != 0 else 0.0
            final_ret_stats.append({"regime": i, "mean": m, "std": s, "ratio_rr": ratio})
        else:
            final_ret_stats.append({"regime": i, "mean": 0.0, "std": 0.0, "ratio_rr": 0.0})
    
    return regimes_ret, probs_ret, final_ret_stats

def train_hmm_diff(data: pd.DataFrame):
    """Train HMM on Diff_Returns data"""
    diff_data = data[['Diff_Returns']].values
    model_diff = hmm.GaussianHMM(n_components=3, covariance_type="full", n_iter=1000, random_state=42)
    model_diff.fit(diff_data)
    raw_regimes_diff = model_diff.predict(diff_data)
    raw_probs_diff = model_diff.predict_proba(diff_data)
    
    diff_stats_raw = []
    for i in range(3):
        r = data.iloc[raw_regimes_diff == i]['Diff_Returns']
        diff_stats_raw.append({'id': i, 'mean': r.mean() if not r.empty else -999, 'std': r.std() if not r.empty else 999})
    
    bull_id_diff = sorted(diff_stats_raw, key=lambda x: x['mean'], reverse=True)[0]['id']
    rem_diff = [s for s in diff_stats_raw if s['id'] != bull_id_diff]
    vol_id_diff = sorted(rem_diff, key=lambda x: x['std'], reverse=True)[0]['id']
    stab_id_diff = [s['id'] for s in diff_stats_raw if s['id'] not in [bull_id_diff, vol_id_diff]][0]
    
    map_diff = {stab_id_diff: 0, bull_id_diff: 1, vol_id_diff: 2}
    regimes_diff = np.array([map_diff[r] for r in raw_regimes_diff])
    
    probs_diff = np.zeros_like(raw_probs_diff)
    probs_diff[:, 0] = raw_probs_diff[:, stab_id_diff]
    probs_diff[:, 1] = raw_probs_diff[:, bull_id_diff]
    probs_diff[:, 2] = raw_probs_diff[:, vol_id_diff]
    
    final_diff_stats = []
    for i in range(3):
        r = data.iloc[regimes_diff == i]['Diff_Returns']
        if not r.empty:
            m = float(r.mean() * 100)
            s = float(r.std() * 100)
            final_diff_stats.append({"regime": i, "mean": m, "std": s})
        else:
            final_diff_stats.append({"regime": i, "mean": 0.0, "std": 0.0})
    
    return regimes_diff, probs_diff, final_diff_stats

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
        
        # Obtener datos
        logger.debug(f"Descargando datos para {ticker} desde {start_date.date()} hasta {end_date.date()}")
        ticker_obj = yf.Ticker(ticker)
        data = ticker_obj.history(start=start_date, end=end_date, auto_adjust=True)
        currency = ticker_obj.info.get('currency', 'USD')
        
        if data.empty:
            logger.error(f"No se encontraron datos para el ticker: {ticker}")
            raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' no encontrado o sin datos disponibles")
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        price_col = 'Close'
        data['Returns'] = np.log(data[price_col] / data[price_col].shift(1))
        data['Diff_Returns'] = data['Returns'].diff()
        data.dropna(inplace=True)
        
        # Validar datos suficientes
        if len(data) < 60:
            logger.error(f"Datos insuficientes para {ticker}: {len(data)} días (mínimo: 60)")
            raise HTTPException(
                status_code=400,
                detail=f"Datos insuficientes: {len(data)} días disponibles. Se requieren al menos 60 días de datos históricos para análisis confiable."
            )
        
        logger.info(f"Datos cargados: {len(data)} días para {ticker}")
        
        # HMM training (sequential execution for thread safety)
        logger.debug("Iniciando entrenamiento de HMMs")
        hmm_start = time.time()
        
        # Train both HMMs sequentially (pandas DataFrames are not thread-safe)
        regimes_ret, probs_ret, final_ret_stats = train_hmm_returns(data)
        regimes_diff, probs_diff, final_diff_stats = train_hmm_diff(data)
        
        hmm_duration = time.time() - hmm_start
        logger.debug(f"HMM completado en {hmm_duration:.2f}s")


        # LLM Forecast (Chronos) with confidence bands
        prediction_length = 10
        forecast_result = []
        last_date = data.index[-1]
        
        if pipeline:
            try:
                context = torch_lib.tensor(data[price_col].values)
                forecast = pipeline.predict(context, prediction_length)
                
                # Calculate percentiles for confidence bands
                forecast_10th = np.quantile(forecast[0].numpy(), 0.1, axis=0)
                forecast_median = np.median(forecast[0].numpy(), axis=0)
                forecast_90th = np.quantile(forecast[0].numpy(), 0.9, axis=0)
                
                for i in range(prediction_length):
                    forecast_result.append({
                        "date": (last_date + timedelta(days=i+1)).strftime("%Y-%m-%d"),
                        "price": float(forecast_median[i]),
                        "price_low": float(forecast_10th[i]),
                        "price_high": float(forecast_90th[i]),
                        "type": "forecast"
                    })
                logger.debug("Predicción Chronos completada con éxito (con bandas de confianza)")
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

        # Preparar historial (usamos los regímenes de Rendimientos para el gráfico principal)
        result = []
        for i in range(len(data)):
            result.append({
                "date": data.index[i].strftime("%Y-%m-%d"),
                "price": float(data[price_col].iloc[i]),
                "regime": int(regimes_ret[i])
            })
        
        current_price = float(data[price_col].iloc[-1])
        previous_price = float(data[price_col].iloc[-2])
        change_pct = ((current_price - previous_price) / previous_price) * 100
        
        # --- TRIPLE-PILLAR RECOMMENDATION ENGINE ---
        def generate_ai_recommendation(data, reg_ret, reg_diff, probs_ret, probs_diff, forecast, ret_stats, diff_stats):
            last_reg_ret = int(reg_ret[-1])
            last_reg_diff = int(reg_diff[-1])
            
            # PILLAR 1: Structural Efficiency (40%)
            # Based on the R/R Ratio of the current state of Returns
            current_ret_stats = next((s for s in ret_stats if s['regime'] == last_reg_ret), {"ratio_rr": 0})
            rr_ratio = current_ret_stats.get("ratio_rr", 0)
            
            structure_score = 0
            if rr_ratio > 0.15: structure_score = 100
            elif rr_ratio > 0.05: structure_score = 70
            elif rr_ratio >= 0: structure_score = 40
            else: structure_score = 10 # Penalize negative R/R
            
            # PILLAR 2: Dynamic Momentum (30%)
            # Based on the mean of the current state of Differences (Impulse)
            current_diff_stats = next((s for s in diff_stats if s['regime'] == last_reg_diff), {"mean": 0})
            impulse_mean = current_diff_stats.get("mean", 0)
            
            momentum_score = 50 # Neutral base
            if impulse_mean > 0.5: momentum_score = 100 # High acceleration
            elif impulse_mean > 0: momentum_score = 75  # Moderate acceleration
            elif impulse_mean > -0.5: momentum_score = 30 # Slowing down
            else: momentum_score = 0 # Strong deceleration
            
            # PILLAR 3: Predictive Projection (30%)
            # Based on the 10-day forecast slope
            forecast_start = forecast[0]['price']
            forecast_end = forecast[-1]['price']
            forecast_trend = (forecast_end / forecast_start) - 1
            
            projection_score = 50
            if forecast_trend > 0.03: projection_score = 100
            elif forecast_trend > 0: projection_score = 70
            elif forecast_trend < -0.03: projection_score = 0
            else: projection_score = 20
            
            # FINAL CONSENSUS SCORE
            final_score = (structure_score * 0.4) + (momentum_score * 0.3) + (projection_score * 0.3)
            
            # VERDICT LOGIC
            if final_score >= 80:
                verdict = "COMPRA FUERTE"
                main_reason = "Eficiencia estructural óptima con fuerte inercia alcista confirmada."
            elif final_score >= 60:
                verdict = "COMPRA"
                main_reason = "Estructura positiva. El mercado muestra calidad y potencial de crecimiento."
            elif final_score >= 40:
                verdict = "MANTENER"
                main_reason = "Zona de equilibrio. Los pilares muestran señales mixtas o estables."
            elif final_score >= 20:
                verdict = "VENTA"
                main_reason = "Pérdida de eficiencia. Se detecta ruido o sesgo bajista en el impulso."
            else:
                verdict = "VENTA FUERTE"
                main_reason = "Deterioro crítico. Colapso de eficiencia y aceleración negativa."

            # Additional notes for context
            notes = []
            if rr_ratio < 0: notes.append("Riesgo elevado (R/R negativo)")
            if impulse_mean < 0: notes.append("Deceleración detectada")
            if forecast_trend < 0: notes.append("Proyección bajista")
            
            if notes:
                main_reason += " (Alertas: " + ", ".join(notes) + ")"
                
            colors = {"COMPRA FUERTE": "#10b981", "COMPRA": "#34d399", "MANTENER": "#fbbf24", "VENTA": "#f87171", "VENTA FUERTE": "#ef4444"}
            
            return {"verdict": verdict, "reason": main_reason, "color": colors.get(verdict, "#94a3b8"), "score": round(final_score, 1)}
        
        ai_rec = generate_ai_recommendation(data, regimes_ret, regimes_diff, probs_ret, probs_diff, forecast_result, final_ret_stats, final_diff_stats)
        
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
    
    # Limit number of tickers for performance in this demo
    limit = 10
    if len(tickers) > limit:
        tickers = tickers[:limit]
        logger.warning(f"Portfolio limitado a {limit} activos para optimizar rendimiento.")

    results = []
    # We use the raw analyze_stock logic (internally) to avoid redundant HTTP overhead
    # In a real app we'd refactor the core logic into a separate shared function
    for ticker in tickers:
        try:
            # We call the existing analyze_stock endpoint logic
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
        advice_parts.append(f"ACCIÓN PRIORITARIA: Se detecta debilidad crítica en {', '.join(to_sell)}. Considerar rotación inmediata para proteger capital.")
    else:
        # Si NO hay ventas, dar consejo de optimización
        if buckets["MANTENER"]:
            advice_parts.append(f"OPTIMIZACIÓN: {', '.join(buckets['MANTENER'])} están en fase lateral; vigilar para acumular si rompen al alza.")
        else:
            advice_parts.append("MANTENIMIENTO: Todos los activos contribuyen positivamente. No se requieren ventas.")

    # C. Oportunidades (Compras)
    strong_opportunities = buckets["STRONG_BUY"]
    if strong_opportunities:
        advice_parts.append(f"LÍDERES: {', '.join(strong_opportunities)} muestran el mejor momentum para sobre-ponderar.")
        
    # D. Notas Técnicas (Divergencias)
    if warnings:
        advice_parts.append(f"OJO AVIZOR: {', '.join(warnings)} suben de precio pero con calidad interna (impulso) deteriorada.")

    full_advice = " ".join(advice_parts)
    
    # Map back to old variable names for return compatibility
    alerts = warnings
    to_remove = to_sell

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
            "to_remove": to_remove
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
