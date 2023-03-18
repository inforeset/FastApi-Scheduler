import datetime

from sqlalchemy import Numeric, Column
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    order: Mapped[int] = mapped_column(nullable=False, unique=True)
    delivery_date: Mapped[datetime.datetime] = mapped_column(nullable=False)
    cost_dollar = Column(Numeric(10, 2), nullable=False)
    cost_ruble = Column(Numeric(10, 2), nullable=False)

