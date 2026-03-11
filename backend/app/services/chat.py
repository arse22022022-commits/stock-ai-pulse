import os
from groq import Groq
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# Configure API Key securely from Environment Variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Define request model for the chat endpoint
class ChatRequest(BaseModel):
    ticker: str
    price: float
    hmm_state: str
    impulse_state: str
    user_query: str
    rvol: float = 1.0   # frontend sends as number
    verdict: str = "No disponible"

class ChatResponse(BaseModel):
    response: str

async def generate_market_explanation(request: ChatRequest) -> str:
    """
    Generates a financial explanation using Groq (Llama 3) based on the provided market context.
    """
    if not GROQ_API_KEY:
        # DEMO MODE: Return a simulated response if no key is configured
        return (
            f"🔒 **MODO DEMO** (Sin API Key)\n\n"
            f"Como analista virtual, veo que {request.ticker} está en un régimen **{request.hmm_state}** "
            f"con un impulso **{request.impulse_state}**.\n\n"
            f"📝 *Para obtener respuestas reales de la IA, necesitas configurar tu Groq API Key.*\n"
            f"1. Ve a [console.groq.com](https://console.groq.com)\n"
            f"2. Crea una clave gratuita.\n"
            f"3. Pónmela aquí y yo la configuro."
        )

    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        # System Prompt Engineering
        rvol_str = f"{request.rvol:.2f}x" if isinstance(request.rvol, float) else str(request.rvol)
        system_prompt = f"""
        Actúa como un **Analista Financiero Senior de Wall Street** con 20 años de experiencia.
        Estás analizando la acción **{request.ticker}** que cotiza a **{request.price}**.
        
        **Datos Técnicos del Sistema:**
        *   **Régimen de Tendencia (HMM - Hidden Markov Model):** {request.hmm_state}
        *   **Régimen de Impulso (Momentum):** {request.impulse_state}
        *   **Volumen Relativo (RVOL):** {rvol_str}
        *   **Veredicto IA / Previsión Chronos:** {request.verdict}
        
        **Instrucciones:**
        1.  Responde en **Español**.
        2.  Sé directo, profesional pero accesible (como a un cliente de banca privada).
        3.  Explica qué significan los regímenes HMM e Impulso en este contexto específico.
        4.  Si el HMM es Alcista pero el Impulso es Volátil/Bajista, advierte del riesgo (divergencia).
        5.  Menciona expresamente el Veredicto IA y el RVOL en tu análisis.
        6.  No des consejos de inversión explícitos, sino interpretación analítica.
        7.  Usa emojis con moderación para destacar puntos clave.
        """

        # Run synchronous Groq call in thread pool to prevent blocking main loop
        import asyncio
        loop = asyncio.get_running_loop()
        
        def _call_groq():
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": request.user_query
                    }
                ],
                model="llama-3.1-8b-instant",
            )
            return chat_completion.choices[0].message.content

        return await loop.run_in_executor(None, _call_groq)

    except Exception as e:
        logger.error(f"Error calling Groq: {e}")
        return f"⚠️ Error al conectar con la IA: {str(e)}"
