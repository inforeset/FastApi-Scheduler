import datetime

from pydantic import BaseModel


class OrderSchema(BaseModel):
    id: int
    order: int
    delivery_date: datetime.datetime
    cost_dollar: float
    cost_ruble: float

    class Config:
        orm_mode = True