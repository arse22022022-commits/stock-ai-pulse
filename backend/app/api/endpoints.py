from fastapi import APIRouter, HTTPException, Request, Depends
from ..services.data_provider import data_provider
from ..services.analysis import train_hmm_returns, train_hmm_diff, generate_ai_recommendation, get_historical_verdicts
from ..services.llm import llm_service
import logging
import asyncio
import numpy as np
from datetime import datetime
from ..services.chat import generate_market_explanation, ChatRequest, ChatResponse
from starlette.concurrency import run_in_threadpool
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

router = APIRouter()

# Executor global compartido para todos los requests (evita crear/destruir pools por request)
_EXECUTOR = ThreadPoolExecutor(max_workers=4)

# Semáforo para serializar inferencia pesada (HMM + Chronos/PyTorch)
# PyTorch no es thread-safe con múltiples inferencias concurrentes en CPU
_INFERENCE_SEMAPHORE = asyncio.Semaphore(1)
logger = logging.getLogger(__name__)
_log = logger # Harmonize logging names

@router.get("/ping")
async def ping():
    return {"status": "ok"}

# Input validation
def validate_ticker(ticker: str) -> bool:
    return bool(re.match(r'^[A-Z0-9]{1,10}(\.[A-Z]{1,3})?$', ticker))

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

def _run_full_analysis(data: pd.DataFrame, ticker: str, lite_mode: bool) -> dict:
    """
    SYNCHRONOUS function: runs ALL CPU-bound work (HMM + Chronos) in one place.
    Designed to be called via loop.run_in_executor() so the asyncio event loop
    is NEVER blocked. Chronos/PyTorch inference is safe here because it runs
    in a dedicated thread, not in the event loop.
    """
    # Blacklist certain tickers that cause native library instability (SIGSEGV) in Windows/Torch
    _CHRONOS_BLACKLIST = ["EOAN.DE"]
    is_blacklisted = any(b in ticker for b in _CHRONOS_BLACKLIST)
    if is_blacklisted:
        _log.warning(f"Ticker {ticker} is blacklisted for Chronos. Using GBM fallback.")
        lite_mode = True

    try:
        # Step 1: HMM (hmmlearn / numpy)
        regimes_ret, probs_ret, final_ret_stats = train_hmm_returns(data)
        regimes_diff, probs_diff, final_diff_stats = train_hmm_diff(data)
        
        # Step 2: Forecast (Chronos with GBM fallback)
        price_col = 'Close'
        last_price = float(data[price_col].iloc[-1])
        last_date = data.index[-1]
        
        forecast = []
        if not lite_mode:
            from ..services.chronos import chronos_service
            from datetime import timedelta
            
            # Try Chronos first
            chronos_success = False
            if chronos_service.enabled:
                try:
                    _log.info("Attempting Chronos prediction...")
                    chronos_pred = chronos_service.predict(data[price_col].values[-30:], 10)
                    if chronos_pred:
                        forecast = [
                            {
                                "date": (last_date + timedelta(days=i+1)).strftime("%Y-%m-%d"),
                                "price": chronos_pred["prices"][i],
                                "price_low": chronos_pred["lows"][i],
                                "price_high": chronos_pred["highs"][i],
                                "type": "forecast",
                                "source": "chronos"
                            }
                            for i in range(len(chronos_pred["prices"]))
                        ]
                        chronos_success = True
                except Exception as ce:
                    _log.warning(f"Chronos failed: {ce}. Falling back to GBM.")
            
            if not chronos_success:
                # GBM fallback (Geometric Brownian Motion)
                import numpy as _np
                returns = _np.diff(_np.log(data[price_col].values[-60:])) if len(data) > 1 else [0]
                mu = float(_np.mean(returns)) if len(returns) > 0 else 0
                sigma = float(_np.std(returns)) if len(returns) > 0 else 0.01
                
                for i in range(10):
                    drift = _np.exp((mu - 0.5 * sigma**2) * (i+1))
                    uncertainty = 1.96 * sigma * _np.sqrt(i+1)
                    price_est = float(last_price * drift)
                    forecast.append({
                        "date": (last_date + timedelta(days=i+1)).strftime("%Y-%m-%d"),
                        "price": price_est,
                        "price_low": float(price_est * _np.exp(-uncertainty)),
                        "price_high": float(price_est * _np.exp(uncertainty)),
                        "type": "forecast",
                        "source": "gbm"
                    })
        
        # Step 3: Hysteresis state machine
        verdicts, scores = get_historical_verdicts(
            data, regimes_ret, regimes_diff, final_ret_stats, final_diff_stats
        )
        stable_state = int(verdicts[-1]) if len(verdicts) > 0 else 0
        smoothed_score = float(scores[-1]) if len(scores) > 0 else 50.0
        
        return {
            "regimes_ret": regimes_ret,
            "probs_ret": probs_ret,
            "final_ret_stats": final_ret_stats,
            "regimes_diff": regimes_diff,
            "probs_diff": probs_diff,
            "final_diff_stats": final_diff_stats,
            "forecast": forecast,
            "stable_state": stable_state,
            "smoothed_score": smoothed_score,
            "verdicts": verdicts,
        }
    except Exception as e:
        import traceback
        _log.error(f"_run_full_analysis failed: {e}")
        _log.error(traceback.format_exc())
        return None

@router.get("/analyze/{ticker}")
async def analyze_stock(ticker: str, lite_mode: bool = False):
    if not validate_ticker(ticker):
        raise HTTPException(status_code=400, detail=f"Ticker inválido '{ticker}'.")

    logger.info(f"Analyzing {ticker}...")
    
    try:
        # 1. Fetch Data (Async - yfinance runs in thread pool inside data_provider)
        data, currency = await data_provider.fetch_ticker_data(ticker)
        
        if data.empty:
            raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' no encontrado o sin datos.")
        
        if len(data) < 60:
            raise HTTPException(status_code=400, detail=f"Datos insuficientes ({len(data)} días). Mínimo 60.")

        # 2. ALL CPU-bound work runs in a SINGLE executor call to avoid event loop blocking.
        # The semaphore serializes concurrent requests to prevent PyTorch/BLAS thread contention.
        # 2. Run FULL Analysis (CPU bound work in threadpool)
        # Using run_in_threadpool instead of manual executor for better exception handling
        async with _INFERENCE_SEMAPHORE:
            result = await run_in_threadpool(_run_full_analysis, data, ticker, lite_mode)
        
        if result is None:
            raise HTTPException(status_code=500, detail="El análisis interno falló. Revisa los logs.")
        
        regimes_ret = result["regimes_ret"]
        probs_ret = result["probs_ret"]
        final_ret_stats = result["final_ret_stats"]
        regimes_diff = result["regimes_diff"]
        probs_diff = result["probs_diff"]
        final_diff_stats = result["final_diff_stats"]
        forecast_result = result["forecast"]
        stable_state = result["stable_state"]
        smoothed_score = result["smoothed_score"]
        verdicts = result.get("verdicts", [])
        
        # 3. Recommendation with hysteresis state (prevents abrupt flips)
        ai_rec = generate_ai_recommendation(
            data, regimes_ret, regimes_diff, probs_ret, probs_diff, 
            forecast_result, final_ret_stats, final_diff_stats,
            stable_state=stable_state,
            smoothed_score=smoothed_score
        )

        
        # 4. Assemble Response
        price_col = 'Close'
        last_price = float(data[price_col].iloc[-1])
        previous_price = float(data[price_col].iloc[-2])
        change_pct = ((last_price - previous_price) / previous_price) * 100
        
        mean_ret = data['Returns'].mean()
        std_ret = data['Returns'].std()
        risk_reward_ratio = float(mean_ret / std_ret) if std_ret != 0 else 0.0

        history = []
        if not lite_mode:
            for i in range(len(data)):
                # Use hysteresis verdict for chart coloring (smoother, no daily flips)
                # Falls back to raw HMM regime if verdicts array is shorter
                chart_regime = int(verdicts[i]) if i < len(verdicts) else int(regimes_ret[i])
                history.append({
                    "date": data.index[i].strftime("%Y-%m-%d"),
                    "price": float(data[price_col].iloc[i]),
                    "regime": chart_regime,
                    "rvol": float(data['RVOL'].iloc[i]) if 'RVOL' in data.columns else 1.0
                })

        response_data = {
            "ticker": ticker,
            "currency": currency,
            "current_price": last_price,
            "change_pct": change_pct,
            "risk_reward_ratio": risk_reward_ratio,
            "history": history,
            "forecast": forecast_result,
            "recommendation": ai_rec,
            "current_regime_ret": int(regimes_ret[-1]),
            "current_regime_diff": int(regimes_diff[-1]),
            "regime_probs_ret": probs_ret[-1].tolist(),
            "regime_probs_diff": probs_diff[-1].tolist(),
            "state_stats_ret": final_ret_stats,
            "state_stats_diff": final_diff_stats,
        }
        
        return sanitize_for_json(response_data)

    except asyncio.TimeoutError:
        logger.error(f"Timeout analyzing {ticker}")
        raise HTTPException(status_code=504, detail=f"Análisis de '{ticker}' tardó demasiado. Inténtalo de nuevo.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/portfolio")
async def analyze_portfolio(tickers: list[str]):
    if not tickers:
        raise HTTPException(status_code=400, detail="Se requiere al menos un ticker")
    
    if len(tickers) > 300:
        tickers = tickers[:300] # Limit increased for composite indices
    
    # Run analyses in parallel!
    tasks = [analyze_stock(ticker, lite_mode=True) for ticker in tickers]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    valid_results = []
    failed = []
    
    for i, res in enumerate(results):
        if isinstance(res, Exception):
            logger.error(f"Error in portfolio for {tickers[i]}: {res}")
            failed.append(tickers[i])
        else:
            valid_results.append(res)
            
    if not valid_results:
         raise HTTPException(status_code=400, detail="No se pudo analizar ningún activo del portfolio")

    # Aggregation Logic (Copied from original server.py)
    reg_list = [r['current_regime_ret'] for r in valid_results]
    bullish_count = reg_list.count(1)
    stable_count = reg_list.count(0)
    volatile_count = reg_list.count(2)
    
    total = len(valid_results)
    bullish_ratio = (bullish_count / total) * 100
    risk_ratio = (volatile_count / total) * 100
    
    # Buckets
    buckets = {"STRONG_BUY": [], "COMPRA": [], "MANTENER": [], "VENTA": [], "VENTA_FUERTE": []}
    # Populate buckets using simplified robust logic
    for r in valid_results:
        ticker = r['ticker']
        v = r.get('recommendation', {}).get('verdict', 'MANTENER').upper()
        
        if "COMPRA" in v and "FUERTE" in v:
            buckets["STRONG_BUY"].append(ticker)
        elif "COMPRA" in v:
            buckets["COMPRA"].append(ticker)
        elif "VENTA" in v:
            buckets["VENTA"].append(ticker)
        else:
            buckets["MANTENER"].append(ticker)
             
    leaders = [r['ticker'] for r in valid_results if r['current_regime_ret'] == 1 and r['current_regime_diff'] == 1]
    warnings = [r['ticker'] for r in valid_results if r['change_pct'] > 0 and r['current_regime_diff'] == 2]
    
    # Narrative - High Fidelity structure matching Premium version
    advice_parts = []
    if risk_ratio > 40:
        advice_parts.append(f"⚠️ ALERTA: Cartera en zona de turbulencia ({risk_ratio:.0f}% volatilidad).")
        risk_level = "Alto"
    elif bullish_ratio > 60:
        advice_parts.append(f"✅ SÓLIDA: Estructura técnica dominante alcista ({bullish_ratio:.0f}%).")
        risk_level = "Bajo"
    else:
        advice_parts.append(f"⚖️ MIXTA: Equilibrio entre activos estables y en desarrollo.")
        risk_level = "Medio"
        
    to_sell = buckets["VENTA"] + buckets["VENTA_FUERTE"]
    if to_sell:
        advice_parts.append(f"• ACCIÓN PRIORITARIA: Se detecta debilidad estructural en {', '.join(to_sell)}. Considerar reducir exposición.")
    else:
        if buckets["MANTENER"]:
            advice_parts.append(f"• OPTIMIZACIÓN: {', '.join(buckets['MANTENER'])} están en fase lateral; vigilar para acumular si rompen al alza.")
        else:
            advice_parts.append("• MANTENIMIENTO: Todos los activos muestran métricas técnicas saludables.")
            
    effective_leaders = list(dict.fromkeys(leaders + buckets["STRONG_BUY"]))
    if effective_leaders:
        advice_parts.append(f"• LÍDERES: {', '.join(effective_leaders)} muestran el mejor momentum para sobre-ponderar.")
    
    if buckets["COMPRA"]:
        advice_parts.append(f"• OPORTUNIDAD: {', '.join(buckets['COMPRA'])} presentan configuraciones técnica favorables.")
        
    if warnings:
        advice_parts.append(f"• OJO AVIZOR: {', '.join(warnings)} muestran divergencia (sube precio, baja impulso). Riesgo de agotamiento.")


    # AI Portfolio Evaluation (Groq) - optional, does not block if it fails
    portfolio_stats = {
        "total_assets": total,
        "bullish_count": bullish_count,
        "bullish_ratio": bullish_ratio,
        "stable_count": stable_count,
        "volatile_count": volatile_count,
        "risk_ratio": risk_ratio,
    }
    ai_insight = await llm_service.evaluate_portfolio_async(portfolio_stats)

    return {
        "assets": valid_results,
        "summary": {
            "total_assets": total,
            "regime_distribution": {
                "bullish": bullish_count,
                "stable": stable_count,
                "volatile": volatile_count
            },
            "risk_level": risk_level,
            "advice": "\n\n".join(advice_parts),
            "bullish_ratio": bullish_ratio,
            "risk_ratio": risk_ratio,
            "leaders": effective_leaders,
            "alerts": warnings,
            "to_remove": to_sell,
            "ai_insight": ai_insight,
        }
    }


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Prepare context data
        context = {
            "ticker": request.ticker,
            "price": request.price,
            "hmm_state": request.hmm_state,
            "impulse_state": request.impulse_state,
            "rvol": request.rvol,
            "verdict": request.verdict,
            "user_query": request.user_query
        }

        
        response_text = await llm_service.generate_market_explanation_async(context)
        return ChatResponse(response=response_text)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

