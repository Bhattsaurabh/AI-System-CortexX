import asyncio
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

async def test_llm():
    try:
        print("Initializing LLM...")
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)
        print("Calling astream...")
        async for chunk in llm.astream("hello"):
            print(f"Chunk: {chunk.content}")
        print("Done!")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test_llm())
