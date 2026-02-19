import os
from groq import Groq
from dotenv import load_dotenv

# Load from backend/.env if needed, or current dir
load_dotenv("backend/.env")
api_key = os.getenv("GROQ_API_KEY")

print(f"Key loaded (first 8 chars): {api_key[:8] if api_key else 'None'}")

if not api_key:
    print("FAILURE: No GROQ_API_KEY found")
    exit(1)

try:
    client = Groq(api_key=api_key)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Hola, responde con 'CONECTADO'.",
            }
        ],
        model="llama-3.1-8b-instant",
    )
    print("SUCCESS")
    print(chat_completion.choices[0].message.content)
except Exception as e:
    print("FAILURE")
    print(e)
