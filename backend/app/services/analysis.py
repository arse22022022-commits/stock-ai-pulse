import numpy as np
import pandas as pd
from hmmlearn import hmm

# --- HMM TRAINING CONFIGURATION ---
HMM_COMPONENTS = 3
HMM_COVARIANCE = "full"
HMM_ITERATIONS = 1000
HMM_RANDOM_STATE = 42

# --- SCORING THRESHOLDS ---
RR_OPTIMAL = 0.15
RR_GOOD = 0.05
RR_MINIMAL = 0.0
MOMENTUM_HIGH = 0.5
MOMENTUM_MODERATE = 0.0
MOMENTUM_SLOWING = -0.5
PROJECTION_BULLISH = 0.03
PROJECTION_BEARISH = -0.03

# --- FLASH CORRECTION CONFIG ---
CRASH_THRESHOLD = -0.025 # -2.5% en un día
PANIC_RVOL = 1.3         # Volumen de pánico
SHORT_TERM_WINDOW = 10   # Ventana para tendencia rápida

# --- HMM TRAINING LOGIC ---

def train_hmm_returns(data: pd.DataFrame):
    """Train HMM on Returns data"""
    returns_data = data[['Returns']].values
    model_ret = hmm.GaussianHMM(n_components=HMM_COMPONENTS, covariance_type=HMM_COVARIANCE, n_iter=HMM_ITERATIONS, random_state=HMM_RANDOM_STATE)
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
    regimes_ret_raw = np.array([map_ret[r] for r in raw_regimes_ret])
    
    # POST-PROCESSING: Smoothing regimes to avoid daily noise/oscillation
    # We use a rolling mode with window 5 to consolidate states
    regimes_series = pd.Series(regimes_ret_raw)
    regimes_ret = regimes_series.rolling(window=5, center=True).apply(lambda x: x.mode().iloc[0]).fillna(method='ffill').fillna(method='bfill').astype(int).values
    
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
    model_diff = hmm.GaussianHMM(n_components=HMM_COMPONENTS, covariance_type=HMM_COVARIANCE, n_iter=HMM_ITERATIONS, random_state=HMM_RANDOM_STATE)
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
    regimes_diff_raw = np.array([map_diff[r] for r in raw_regimes_diff])
    
    # POST-PROCESSING: Smoothing regimes
    reg_series_diff = pd.Series(regimes_diff_raw)
    regimes_diff = reg_series_diff.rolling(window=5, center=True).apply(lambda x: x.mode().iloc[0]).fillna(method='ffill').fillna(method='bfill').astype(int).values
    
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


# --- TRIPLE-PILLAR RECOMMENDATION ENGINE ---

def _calculate_score(data_slice, last_reg_ret, last_reg_diff, ret_stats, diff_stats, forecast_trend=None):
    """Helper to calculate the 0-100 consolidated score for a specific point in time"""
    # VOLUME METRICS
    last_rvol = float(data_slice['RVOL'].iloc[-1])
    vol_trend = float(data_slice['RVOL'].iloc[-3:].mean() - data_slice['RVOL'].iloc[-5:-2].mean()) if len(data_slice) > 5 else 0
    last_ret = float(data_slice['Returns'].iloc[-1])
    
    # PILLAR 1: Structural Efficiency (Anclaje)
    current_ret_stats = next((s for s in ret_stats if s['regime'] == last_reg_ret), {"ratio_rr": 0})
    rr_ratio = current_ret_stats.get("ratio_rr", 0)
    
    structure_score = 0
    if rr_ratio > RR_OPTIMAL: structure_score = 100
    elif rr_ratio > RR_GOOD: structure_score = 70
    elif rr_ratio >= RR_MINIMAL: structure_score = 40
    else: structure_score = 10 

    # MODULATION 1: Directional RVOL (Acumulación vs Distribución)
    struct_multiplier = 1.0
    if last_rvol > 1.5:
        if last_ret > 0: struct_multiplier = 1.25 # Acumulación
        else: struct_multiplier = 0.5            # Distribución/Pánico
    elif last_rvol < 0.7:
        if last_ret > 0: struct_multiplier = 0.8  # Agotamiento
        else: struct_multiplier = 1.1            # Secado de oferta
            
    structure_score = min(100, structure_score * struct_multiplier)
    
    # PILLAR 2: Dynamic Momentum (30%)
    current_diff_stats = next((s for s in diff_stats if s['regime'] == last_reg_diff), {"mean": 0})
    impulse_mean = current_diff_stats.get("mean", 0)
    
    momentum_score = 50 
    if impulse_mean > MOMENTUM_HIGH: momentum_score = 100 
    elif impulse_mean > MOMENTUM_MODERATE: momentum_score = 75  
    elif impulse_mean > MOMENTUM_SLOWING: momentum_score = 30 
    elif impulse_mean <= MOMENTUM_SLOWING: momentum_score = 0 

    # MODULATION 2: Divergence
    price_trend = float(data_slice['Close'].iloc[-1] / data_slice['Close'].iloc[-5] - 1) if len(data_slice) > 5 else 0
    if price_trend > 0 and vol_trend < -0.1:
        momentum_score *= 0.7
    elif price_trend > 0 and vol_trend > 0.1:
        momentum_score = min(100, momentum_score * 1.1)
    
    # PILLAR 3: Predictive Projection (20%)
    projection_score = 50
    if forecast_trend is not None:
        if forecast_trend > PROJECTION_BULLISH: projection_score = 100
        elif forecast_trend > 0: projection_score = 70
        elif forecast_trend < PROJECTION_BEARISH: projection_score = 0
        else: projection_score = 20
    
    # --- FLASH CORRECTION (REFLEJOS) ---
    panic_penalty = 1.0
    
    # 1. Detección de Caída Vertical (Crash)
    if last_ret <= CRASH_THRESHOLD and last_rvol >= PANIC_RVOL:
        panic_penalty *= 0.5 # Tajo del 50% al score final
        structure_score = min(30, structure_score) # Destruye la confianza estructural
        
    # 2. Rotura de Tendencia de Corto Plazo (EMA 10)
    if len(data_slice) >= SHORT_TERM_WINDOW:
        ema_short = data_slice['Close'].ewm(span=SHORT_TERM_WINDOW).mean().iloc[-1]
        current_price = data_slice['Close'].iloc[-1]
        if current_price < ema_short:
            panic_penalty *= 0.85 # Penalización por debilidad de corto plazo
            
    final_score = (structure_score * 0.6) + (momentum_score * 0.2) + (projection_score * 0.2)
    final_score *= panic_penalty # Aplicar reflejos de protección
    
    return final_score, last_rvol, rr_ratio, impulse_mean, forecast_trend


def generate_ai_recommendation(data, reg_ret, reg_diff, probs_ret, probs_diff, forecast, ret_stats, diff_stats, stable_state=0, smoothed_score=50.0):
    """Generates the final AI response supervised by the stable state from hysteresis"""
    
    # VERDICT LOGIC BASED ON STABLE STATE (Hysteresis-driven)
    # 0: Hold (Yellow), 1: Buy (Green), 2: Sell (Red)
    if stable_state == 1: # COMPRA
        verdict = "COMPRA FUERTE" if smoothed_score >= 80 else "COMPRA"
        main_reason = "Impulso estructural alcista confirmado por el modelo de histéresis."
    elif stable_state == 2: # VENTA
        verdict = "VENTA FUERTE" if smoothed_score <= 20 else "VENTA"
        main_reason = "Deterioro de eficiencia detectado. Se recomienda precaución extrema."
    else: # MANTENER
        verdict = "MANTENER"
        main_reason = "Zona de equilibrio estable. Los pilares no muestran convicción direccional."
        
    colors = {"COMPRA FUERTE": "#10b981", "COMPRA": "#34d399", "MANTENER": "#fbbf24", "VENTA": "#f87171", "VENTA FUERTE": "#ef4444"}
    
    return {
        "verdict": verdict, 
        "reason": main_reason, 
        "color": colors.get(verdict, "#94a3b8"), 
        "score": round(float(smoothed_score), 1),
        "rvol": float(data['RVOL'].iloc[-1]) if 'RVOL' in data.columns else 1.0,
        "breakdown": {
            "structure": None, 
            "momentum": None,
            "projection": None
        }
    }

def get_historical_verdicts(data, reg_ret, reg_diff, ret_stats, diff_stats):
    """Calculates historical recommendation states (0-4) for matching the 5-tier AI verdicts"""
    raw_scores = []
    for i in range(len(data)):
        if i < 5:
            raw_scores.append(50.0)
            continue
        data_slice = data.iloc[:i+1]
        score, _, _, _, _ = _calculate_score(
            data_slice, int(reg_ret[i]), int(reg_diff[i]), ret_stats, diff_stats
        )
        raw_scores.append(score)
    
    # Smooth scores (3-day rolling mean) for stability while maintaining category accuracy
    scores = pd.Series(raw_scores).rolling(window=3, center=False).mean().fillna(method='bfill').values
    
    # FORCE SYNC: The very last point must match the raw score to avoid contradiction with the dashboard
    if len(scores) > 0:
        scores[-1] = raw_scores[-1]
    
    # Apply Hysteresis State Machine to the smoothed scores
    verdicts = []
    current_state = 0 # 0: Mantener, 1: Compra, 2: Venta
    
    for score in scores:
        if current_state == 1: # Previamente en COMPRA
            if score < 50: # Salida de Compra (buffer de 15ptos)
                if score <= 30: current_state = 2 # Salto directo a Venta
                else: current_state = 0 # Retroceso a Mantener
        elif current_state == 2: # Previamente en VENTA
            if score > 45: # Salida de Venta (buffer de 15ptos)
                if score >= 65: current_state = 1 # Salto directo a Compra
                else: current_state = 0 # Recuperación a Mantener
        else: # Previamente en MANTENER
            if score >= 65: current_state = 1 # Entrada a Compra (necesita fuerza)
            elif score <= 30: current_state = 2 # Entrada a Venta (necesita debilidad)
            
        verdicts.append(current_state)
        
    return verdicts, scores
