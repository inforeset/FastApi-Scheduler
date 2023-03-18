import datetime
import os

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from log_config import logger
from models import Order, Base
from utils import get_exchange

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def write_to_db(data: list) -> None:
    logger.info('update table in database')
    list_orders = []
    exchange = await get_exchange()

    for record in data:
        order = dict(
            order=int(record[1]),
            cost_dollar=float(record[2]),
            delivery_date=datetime.datetime.strptime(record[3], "%d.%m.%Y"),
            cost_ruble=float(record[2]) * exchange
        )
        list_orders.append(order)

    stmt = insert(Order).values(list_orders)

    async with engine.begin() as conn:
        stmt = stmt.on_conflict_do_update(
            index_elements=[Order.order],
            set_={
                "cost_dollar": stmt.excluded.cost_dollar,
                "delivery_date": stmt.excluded.delivery_date,
                "cost_ruble": stmt.excluded.cost_ruble
            }
        )
        try:
            await conn.execute(stmt)
        except SQLAlchemyError as exc:
             logger.error('Error when trying update database', exc_info=exc)
