import logging
import os
import threading
import json
import asyncio
import numpy as np
import google.generativeai as genai
from datetime import timedelta
from .chronos import chronos_service

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.model = None
        self.enabled = False
        self.lock = threading.Lock()
        self._load_model()

    def _load_model(self):
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                logger.warning("GOOGLE_API_KEY not found in environment. LLM will use statistical fallback.")
                self.enabled = False
                return

            genai.configure(api_key=api_key)
            # Fetch model from env, fallback to gemini-1.5-pro
            model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
            self.model = genai.GenerativeModel(model_name)
            self.enabled = True
            logger.info(f"{model_name} initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini 1.5 Pro: {str(e)}", exc_info=True)
            self.enabled = False

    async def predict(self, data_series: np.ndarray, prediction_length: int = 10, last_date=None, last_price=0.0):
        """
        Generate forecast. If Gemini is active, use it for intelligent forecasting.
        Otherwise, use statistical fallback (GBM).
        """
        if self.enabled and self.model:
            try:
                # Prepare data for prompt
                # We send the last 60 days of closing prices to give context
                prices_str = ", ".join([f"{p:.2f}" for p in data_series[-60:]])
                
                prompt = f"""
                Analyze the following historical stock price series (last 60 days):
                [{prices_str}]

                Last known price: {last_price:.2f}
                Last known date: {last_date.strftime("%Y-%m-%d") if last_date else "N/A"}

                Task:
                Generate a {prediction_length}-day price forecast starting from the next day.
                Provide a JSON response with a list of dictionaries. Each dictionary must have:
                - "date": Date in YYYY-MM-DD format.
                - "price": Predicted closing price (float).
                - "price_low": Estimated lower bound (10th percentile, float).
                - "price_high": Estimated upper bound (90th percentile, float).

                Focus on structural efficiency and momentum based on the provided series.
                Return ONLY the JSON array.
                """

                # Call Gemini with advanced reasoning config
                # thinking_level="MEDIUM" is a new feature for Gemini 3.1 Pro
                # Call Gemini with advanced reasoning config
                # thinking_level="MEDIUM" is a new feature for Gemini 3.1 Pro
                response = await asyncio.wait_for(
                    self.model.generate_content_async(
                        prompt,
                        generation_config={
                            "response_mime_type": "application/json",
                            "thinking_level": "MEDIUM"
                        }
                    ),
                    timeout=30.0
                )
                
                logger.info("Gemini forecast generated successfully.")
                
                forecast_data = json.loads(response.text)
                
                # Ensure the response is in the correct format for the frontend
                forecast_result = []
                for entry in forecast_data:
                    entry["type"] = "forecast"
                    entry["source"] = "genai"
                    forecast_result.append(entry)
                
                return forecast_result

            except Exception as e:
                logger.error(f"Gemini prediction failed: {e}. Falling back to statistical model.")
                # Fall through to fallback
        
                # Fall through to Chronos fallback
        
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
        Since generate_content_async is natively supported, we no longer need the run_in_executor wrapper here
        """
        return await self.predict(data_series, prediction_length, last_date, last_price)

    async def evaluate_portfolio_async(self, portfolio_stats: dict) -> dict:
        """
        Use Gemini 1.5 Pro to evaluate a portfolio's overall health and diversification using aggregated metrics.
        The returned dictionary matches the properties expected by the frontend.
        """
        # Fallback dictionary if LLM is disabled or fails
        fallback_response = {
            "verdict": "ANÁLISIS NO DISPONIBLE",
            "reason": "La IA de análisis global no está activa o falló al recibir contexto.",
            "color": "#6b7280", # Gray
            "score": 0.0
        }

        if not self.enabled or not self.model:
            return fallback_response

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
            # We don't necessarily need "MEDIUM" thinking here as it's a fast summarization task,
            # but we use standard parameters to ensure a fast JSON response.
            # We don't necessarily need "MEDIUM" thinking here as it's a fast summarization task,
            # but we use standard parameters to ensure a fast JSON response.
            response = await asyncio.wait_for(
                self.model.generate_content_async(
                    prompt,
                    generation_config={
                        "response_mime_type": "application/json",
                    }
                ),
                timeout=25.0
            )
            
            logger.info("Portfolio Gemini analysis generated successfully.")
            
            res_dict = json.loads(response.text)
            
            # Type casting to ensure rigid contract
            return {
                "verdict": str(res_dict.get("verdict", "ANÁLISIS COMPLETADO")),
                "reason": str(res_dict.get("reason", "Se ha analizado la cartera con éxito.")),
                "color": str(res_dict.get("color", "#3b82f6")), # Default blue
                "score": float(res_dict.get("score", 50.0))
            }
            
        except Exception as e:
            logger.error(f"Failed to generate Gemini Portfolio Analysis: {e}", exc_info=True)
            return fallback_response

# Global instance
llm_service = LLMService()

