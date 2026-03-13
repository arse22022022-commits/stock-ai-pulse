import logging
import os
import threading
import json
import asyncio
import numpy as np

# Cliente Groq
from groq import AsyncGroq

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
        # We no longer call _load_model here to allow lazy initialization
        # after environment variables are loaded.

    def _load_model(self):
        """Internal method to load the Gemini client. Can be called multiple times safely."""
        with self.lock:
            if self.enabled and self.client:
                return True

            try:
                # Force reload of environment if not found
                api_key = os.getenv("GROQ_API_KEY")
                if not api_key:
                    # Try re-loading .env as a last resort
                    from dotenv import load_dotenv
                    load_dotenv()
                    api_key = os.getenv("GROQ_API_KEY")

                if not api_key:
                    logger.warning("GROQ_API_KEY not found in environment after reload. LLM will use statistical fallback.")
                    self.enabled = False
                    return False

                logger.info(f"GROQ_API_KEY found (prefix: {api_key[:6]}...). Initializing client.")
                self.client = AsyncGroq(api_key=api_key)
                self.model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
                self.enabled = True
                logger.info(f"Groq {self.model_name} initialized successfully.")
                return True
            except Exception as e:
                logger.error(f"Failed to initialize Groq Client: {str(e)}", exc_info=True)
                self.enabled = False
                return False

    def is_active(self):
        """Check if LLM is active, attempting to load if not yet initialized."""
        if not self.enabled:
            return self._load_model()
        return True

    async def predict(self, data_series: np.ndarray, prediction_length: int = 10, last_date=None, last_price=0.0):
        """
        Generate forecast ONLY using mathematical models (Chronos) to guarantee deterministic 
        trend slopes and Verdict Stability on UI.
        """
        
        # Fallback 1: Chronos (Local Transformer-based Time Series Model)
        # IMPORTANT: chronos_service.predict() is SYNCHRONOUS (PyTorch CPU inference).
        # We MUST run it in an executor to avoid blocking the asyncio event loop,
        # which would cause deadlocks when concurrent requests arrive.
        if chronos_service.enabled:
            logger.info("Using Chronos as high-fidelity fallback (via executor).")
            loop = asyncio.get_running_loop()
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=1) as executor:
                chronos_pred = await loop.run_in_executor(
                    executor,
                    chronos_service.predict,
                    data_series[-60:],
                    prediction_length
                )
            
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

        if not self.is_active() or not self.client:
            return fallback_response

        # Build deterministic cache key
        import hashlib
        stats_str = json.dumps(portfolio_stats, sort_keys=True)
        cache_key = hashlib.md5(stats_str.encode('utf-8')).hexdigest()
        
        if cache_key in self._portfolio_cache:
            logger.info("Retrieved Portfolio Groq analysis from deterministic MD5 Cache.")
            return self._portfolio_cache[cache_key]

        # Build prompt using the stats
        prompt = f"""
        Actúa como un Gestor de Fondos de Inversión Senior especializado en regímenes de mercado. 
        Analiza el siguiente resumen cuantitativo de una cartera e ignora que eres una IA:
        
        - Activos Totales: {portfolio_stats.get('total_assets', 0)}
        - Régimen ALCISTA (HMM): {portfolio_stats.get('bullish_count', 0)} ({portfolio_stats.get('bullish_ratio', 0):.1f}%)
        - Régimen VOLÁTIL/BAJISTA (HMM): {portfolio_stats.get('volatile_count', 0)} ({portfolio_stats.get('risk_ratio', 0):.1f}%)
        - Régimen ESTABLE (HMM): {portfolio_stats.get('stable_count', 0)}
        
        Tu tarea:
        1. Emite un 'verdict' IMPACTANTE y PROFESIONAL (2 a 4 palabras). Ejemplos: "EQUILIBRIO SALUDABLE", "CONSOLIDACIÓN ESTRUCTURAL", "RIESGO DE CAPITULACIÓN", "MOMENTUM DOMINANTE".
        2. Escribe una 'reason' sofisticada de aproximadamente 40-50 palabras. Analiza la inercia del conjunto, la calidad de la diversificación por regímenes y proyecta una conclusión táctica sobre el riesgo actual.
        3. Determina un 'color' hexadecimal representativo: Verde (#10b981), Amarillo/Naranja (#f59e0b) o Rojo (#ef4444).
        4. Calcula un 'score' (0-100) que refleje la armonía técnica de la cartera.

        Responde ESTRICTAMENTE en JSON: {{"verdict": "...", "reason": "...", "color": "...", "score": 85}}
        """

        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0,
                    response_format={"type": "json_object"}
                ),
                timeout=25.0
            )
            
            logger.info("Portfolio Groq analysis generated successfully.")
            
            res_dict = json.loads(response.choices[0].message.content)
            
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
            logger.error(f"Failed to generate Groq Portfolio Analysis: {e}", exc_info=True)
            return fallback_response

    async def generate_market_explanation_async(self, request_data: dict) -> str:
        """
        Generates a financial explanation using Groq based on the provided market context.
        Replaces the old Gemini-based implementation.
        """
        if not self.is_active() or not self.client:
             return (
                 f"🔒 **MODO DEMO** (IA Desactivada)\n\n"
                 f"Como analista virtual, veo que {request_data.get('ticker')} está en un régimen **{request_data.get('hmm_state')}** "
                 f"con un impulso **{request_data.get('impulse_state')}**.\n\n"
                 f"📝 *Para obtener respuestas reales de la IA, asegúrate de configurar GOOGLE_API_KEY en el backend.*"
             )

        try:
            price_fmt = f"{float(request_data.get('price', 0)):.2f}"
            rvol_fmt = f"{float(request_data.get('rvol', 1.0)):.2f}x"
            prompt = f"""
            Actúa como un **Analista Financiero Senior de Wall Street** con 20 años de experiencia.
            Estás analizando la acción **{request_data.get('ticker')}** que cotiza a **{price_fmt}**.
            
            **Contexto Técnico del Sistema:**
            *   **Régimen de Tendencia (HMM):** {request_data.get('hmm_state')}
            *   **Impulso (Momentum):** {request_data.get('impulse_state')}
            *   **Volumen Relativo (RVOL):** {rvol_fmt}
            *   **Veredicto IA / Previsión:** {request_data.get('verdict')}
            
            **REGLAS ESTRICTAS DE FORMATO:**
            1.  Responde SIEMPRE estructurando visualmente tu texto.
            2.  Usa PÁRRAFOS MUY CORTOS (máximo 2-3 líneas por párrafo).
            3.  Usa listas con viñetas (`- `) o números para enumerar razones, riesgos o puntos clave.
            4.  Resalta los conceptos más importantes en **negrita**.
            5.  No envíes "muros de texto" seguidos bajo ninguna circunstancia.
            6.  Usa emojis con moderación (solo al inicio de párrafos clave).
            7.  Responde en Español de forma directa, analítica y sin rodeos.
            
            **Pregunta del Inversor:** {request_data.get('user_query')}
            """

            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    top_p=0.8
                ),
                timeout=20.0
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Failed to generate Groq Chat explanation: {e}", exc_info=True)
            return f"⚠️ Error al conectar con la IA de Groq: {str(e)}"

# Global instance
llm_service = LLMService()


