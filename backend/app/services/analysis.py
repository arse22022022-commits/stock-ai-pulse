import numpy as np
import pandas as pd
from hmmlearn import hmm

# --- HMM TRAINING LOGIC ---

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
    elif impulse_mean <= -0.5: momentum_score = 0 # Strong deceleration
    
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
