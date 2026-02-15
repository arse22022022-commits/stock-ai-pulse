from fastapi import APIRouter, HTTPException, Request, Depends
from ..services.data_provider import data_provider
from ..services.analysis import train_hmm_returns, train_hmm_diff, generate_ai_recommendation
from ..services.llm import llm_service
import logging
import asyncio
import numpy as np
from datetime import datetime
from ..services.chat import generate_market_explanation, ChatRequest, ChatResponse
import re

router = APIRouter()
logger = logging.getLogger(__name__)

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

@router.get("/analyze/{ticker}")
async def analyze_stock(ticker: str):
    if not validate_ticker(ticker):
        raise HTTPException(status_code=400, detail=f"Ticker inválido '{ticker}'.")

    logger.info(f"Analyzing {ticker}...")
    
    try:
        # 1. Fetch Data (Async)
        data, currency = await data_provider.fetch_ticker_data(ticker)
        
        if data.empty:
            raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' no encontrado o sin datos.")
        
        if len(data) < 60:
            raise HTTPException(status_code=400, detail=f"Datos insuficientes ({len(data)} días). Mínimo 60.")

        # 2. HMM Analysis (CPU Bound - could be offloaded to process pool if needed)
        # For now, we run it directly as it's fast enough for <1000 data points
        # If blocking becomes an issue, use loop.run_in_executor
        regimes_ret, probs_ret, final_ret_stats = train_hmm_returns(data)
        regimes_diff, probs_diff, final_diff_stats = train_hmm_diff(data)
        
        # 3. Forecast
        price_col = 'Close'
        last_price = float(data[price_col].iloc[-1])
        last_date = data.index[-1]
        
        forecast_result = await llm_service.predict_async(
            data[price_col].values, 
            prediction_length=10, 
            last_date=last_date, 
            last_price=last_price
        )
        
        # 4. Recommendation
        ai_rec = generate_ai_recommendation(
            data, regimes_ret, regimes_diff, probs_ret, probs_diff, 
            forecast_result, final_ret_stats, final_diff_stats
        )
        
        # 5. Assemble Response
        current_price = last_price
        previous_price = float(data[price_col].iloc[-2])
        change_pct = ((current_price - previous_price) / previous_price) * 100
        # currency = data_provider.get_currency(ticker) # REMOVED: Blocking call
        
        mean_ret = data['Returns'].mean()
        std_ret = data['Returns'].std()
        risk_reward_ratio = float(mean_ret / std_ret) if std_ret != 0 else 0.0

        # Construct History
        history = []
        for i in range(len(data)):
            history.append({
                "date": data.index[i].strftime("%Y-%m-%d"),
                "price": float(data[price_col].iloc[i]),
                "regime": int(regimes_ret[i])
            })

        response_data = {
            "ticker": ticker,
            "currency": currency,
            "current_price": current_price,
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

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/portfolio")
async def analyze_portfolio(tickers: list[str]):
    if not tickers:
        raise HTTPException(status_code=400, detail="Se requiere al menos un ticker")
    
    if len(tickers) > 20:
        tickers = tickers[:20] # Increased limit due to async
    
    # Run analyses in parallel!
    tasks = [analyze_stock(ticker) for ticker in tickers]
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
    for r in valid_results:
        v = r['recommendation']['verdict'].replace(" ", "_")
        if v in buckets:
            buckets[v].append(r['ticker'])
        elif v == "COMPRA_FUERTE":
             buckets["STRONG_BUY"].append(r['ticker'])
             
    leaders = [r['ticker'] for r in valid_results if r['current_regime_ret'] == 1 and r['current_regime_diff'] == 1]
    warnings = [r['ticker'] for r in valid_results if r['change_pct'] > 0 and r['current_regime_diff'] == 2]
    
    # Narrative
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
        advice_parts.append(f"ACCIÓN PRIORITARIA: Debilidad en {', '.join(to_sell)}.")
    else:
        if buckets["MANTENER"]:
            advice_parts.append(f"OPTIMIZACIÓN: {', '.join(buckets['MANTENER'])} laterales.")
        else:
            advice_parts.append("MANTENIMIENTO: Todo positivo.")
            
    if buckets["STRONG_BUY"]:
        advice_parts.append(f"LÍDERES: {', '.join(buckets['STRONG_BUY'])}.")
        
    if warnings:
        advice_parts.append(f"OJO AVIZOR: {', '.join(warnings)} (Sube precio, baja impulso).")



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
            "advice": " ".join(advice_parts),
            "bullish_ratio": bullish_ratio,
            "risk_ratio": risk_ratio,
            "leaders": leaders,
            "alerts": warnings,
            "to_remove": to_sell
        }
    }

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        response_text = await generate_market_explanation(request)
        return ChatResponse(response=response_text)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

