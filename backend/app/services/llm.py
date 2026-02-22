import logging
import os
import threading
import json
import asyncio
import numpy as np

# Nuevo SDK v2 de Google
from google import genai
from google.genai import types

from datetime import timedelta
from .chronos import chronos_service

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.client = None
        self.model_name = None
        self.enabled = False
        self.lock = threading.Lock()
        self._portfolio_cache = {}
        self._load_model()

    def _load_model(self):
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                logger.warning("GOOGLE_API_KEY not found in environment. LLM will use statistical fallback.")
                self.enabled = False
                return

            self.client = genai.Client(api_key=api_key)
            # Default to Gemini 1.5 Flash to ensure 1,500 requests per day (2.5 restricted to 20/day limit on free)
            self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            self.enabled = True
            logger.info(f"{self.model_name} initialized successfully via GenAI SDK")
        except Exception as e:
            logger.error(f"Failed to initialize GenAI Client: {str(e)}", exc_info=True)
            self.enabled = False

    async def predict(self, data_series: np.ndarray, prediction_length: int = 10, last_date=None, last_price=0.0):
        """
        Generate forecast ONLY using mathematical models (Chronos) to guarantee deterministic 
        trend slopes and Verdict Stability on UI.
        """
        
        # Fallback 1: Chronos (Local Transformer-based Time Series Model)
        if chronos_service.enabled:
            logger.info("Using Chronos as high-fidelity fallback.")
            chronos_pred = chronos_service.predict(data_series[-60:], prediction_length)
            
            if chronos_pred:
                forecast_result = []
                for i in range(prediction_length):
                    forecast_result.append({
                        "date": (last_date + timedelta(days=i+1)).strftime("%Y-%m-%d"),
                        "price": chronos_pred["prices"][i],
                        "price_low": chronos_pred["lows"][i],
                        "price_high": chronos_pred["highs"][i],
                        "type": "forecast",
                        "source": "chronos"
                    })
                return forecast_result
        
        # Fallback 2: Geometric Brownian Motion (GBM) - The "straight line"
        forecast_result = []
        returns = np.diff(np.log(data_series[-60:])) if len(data_series) > 1 else [0]
        mu = np.mean(returns) if len(returns) > 0 else 0
        sigma = np.std(returns) if len(returns) > 0 else 0.01
        
        for i in range(prediction_length):
            drift = np.exp((mu - 0.5 * sigma**2) * (i+1))
            uncertainty = 1.96 * sigma * np.sqrt(i+1)
            
            price_est = float(last_price * drift)
            forecast_result.append({
                "date": (last_date + timedelta(days=i+1)).strftime("%Y-%m-%d"), 
                "price": price_est,
                "price_low": float(price_est * np.exp(-uncertainty)),
                "price_high": float(price_est * np.exp(uncertainty)),
                "type": "forecast",
                "source": "gbm"
            })
            
        return forecast_result

    async def predict_async(self, data_series: np.ndarray, prediction_length: int = 10, last_date=None, last_price=0.0):
        """
        Wrapper as we still use this natively
        """
        return await self.predict(data_series, prediction_length, last_date, last_price)

    async def evaluate_portfolio_async(self, portfolio_stats: dict) -> dict:
        """
        Use new GenAI SDK to evaluate a portfolio's overall health and diversification using aggregated metrics.
        """
        # Fallback dictionary if LLM is disabled or fails
        fallback_response = {
            "verdict": "ANÁLISIS NO DISPONIBLE",
            "reason": "La IA de análisis global no está activa o falló al recibir contexto.",
            "color": "#6b7280", # Gray
            "score": 0.0
        }

        if not self.enabled or not self.client:
            return fallback_response

        # Build deterministic cache key
        import hashlib
        stats_str = json.dumps(portfolio_stats, sort_keys=True)
        cache_key = hashlib.md5(stats_str.encode('utf-8')).hexdigest()
        
        if cache_key in self._portfolio_cache:
            logger.info("Retrieved Portfolio Gemini analysis from deterministic MD5 Cache.")
            return self._portfolio_cache[cache_key]

        # Build prompt using the stats
        prompt = f"""
        Actúa como un gestor de fondos de alto nivel. Analiza el siguiente resumen cuantitativo de una cartera de activos e ignora que eres una IA:
        
        - Número total de activos: {portfolio_stats.get('total_assets', 0)}
        - Activos en régimen ALCISTA (HMM): {portfolio_stats.get('bullish_count', 0)} ({portfolio_stats.get('bullish_ratio', 0):.1f}%)
        - Activos en régimen VOLÁTIL/BAJISTA (HMM): {portfolio_stats.get('volatile_count', 0)} ({portfolio_stats.get('risk_ratio', 0):.1f}%)
        - Activos en régimen ESTABLE (HMM): {portfolio_stats.get('stable_count', 0)}

        Tu tarea:
        1. Emite un 'verdict' muy corto (2 a 4 palabras máximo, en mayúsculas). Ejemplos: "CRECIMIENTO SÓLIDO", "RIESGO ELEVADO", "DEFENSIVA", "INCERTIDUMBRE LATENTE".
        2. Escribe una 'reason' (explicación breve de máximo 25 palabras). Debe sonar profesional indicando la conclusión sobre la inercia actual y el riesgo.
        3. Determina un 'color' hexadecimal que represente el estado (verde para bueno/sano, amarillo/naranja para precaución, rojo para peligro).
        4. Calcula un 'score' del 0 al 100 de la salud global de la cartera.

        Debes responder ESTRICTAMENTE con un objeto JSON válido con las claves: "verdict", "reason", "color", "score" (como número). NO añadas markdown de código, asegúrate de que sea 100% parseable por json.loads.
        """

        try:
            # New async genai client format
            response = await asyncio.wait_for(
                self.client.aio.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.0,
                        top_p=0.1,
                        top_k=1
                    )
                ),
                timeout=25.0
            )
            
            logger.info("Portfolio Gemini analysis generated successfully.")
            
            res_dict = json.loads(response.text)
            
            # Type casting to ensure rigid contract
            final_result = {
                "verdict": str(res_dict.get("verdict", "ANÁLISIS COMPLETADO")),
                "reason": str(res_dict.get("reason", "Se ha analizado la cartera con éxito.")),
                "color": str(res_dict.get("color", "#3b82f6")), # Default blue
                "score": float(res_dict.get("score", 50.0))
            }
            
            # Save to Cache with LRU logic
            if len(self._portfolio_cache) > 200:
                self._portfolio_cache.pop(next(iter(self._portfolio_cache)))
            self._portfolio_cache[cache_key] = final_result
            
            return final_result
            
        except Exception as e:
            logger.error(f"Failed to generate Gemini Portfolio Analysis: {e}", exc_info=True)
            return fallback_response

# Global instance
llm_service = LLMService()


