from typing import List, Sequence, Any

import uvicorn
from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Depends
from sqlalchemy import Row, RowMapping, select
from sqlalchemy.ext.asyncio import AsyncSession

from config_reader import save_config
from database import init_db, get_session
from loader import config
from log_config import logger
from models import Order
from schemas import OrderSchema
from tasks import check_table

app = FastAPI()


@app.on_event("startup")
async def startup():
    logger.info('initialize database')
    await init_db()

    def error_handler(event):
        logger.error(f"An error occurred while executing job: {event.job_id}")
        scheduler.remove_job(event.job_id)
        logger.info('job was removed from scheduler')

    scheduler = AsyncIOScheduler()
    scheduler.start()
    logger.info('start scheduler')
    scheduler.add_listener(error_handler, EVENT_JOB_ERROR)
    scheduler.add_job(check_table, 'cron', minute='*/2')


@app.on_event("shutdown")
async def shutdown():
    logger.info('server shutdown')
    save_config(config)


@app.get('/', response_model=List[OrderSchema])
async def ingredients_get(session: AsyncSession = Depends(get_session)) -> Sequence[Row | RowMapping | Any]:
    res = await session.execute(select(Order))
    return res.scalars().all()


if __name__ == '__main__':
    uvicorn.run(app)
