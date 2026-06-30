import asyncio
from agents.simulator import simulate_autonomous_loop

async def main():
    async for m in simulate_autonomous_loop('hello', 'builder', 'gemini-2.5-pro', ''):
        print(m)

asyncio.run(main())
