import os
import asyncio
from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv('backend/.env')

async def run():
    print("Testing connection to Groq...")
    client = AsyncGroq(api_key=os.getenv('GROQ_API_KEY'))
    print("Sending message...")
    try:
        response = await client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[{'role': 'user', 'content': 'hola'}],
            temperature=0.0
        )
        print("Response received:")
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    asyncio.run(run())
