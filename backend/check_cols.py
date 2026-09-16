import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'lessons'"))
        print("LESSONS COLS:", [r[0] for r in res.fetchall()])

asyncio.run(check())
