from datetime import datetime

from pydantic import BaseModel


class Order(BaseModel):
    order_id: str
    created_at: datetime
    total_amount: float
    currency: str
