import asyncio

from database import write_to_db
from google_table import check_change
from loader import config


async def check_table():
    data = await asyncio.to_thread(check_change, config=config)
    print(data)
    if data:
        await write_to_db(data)
