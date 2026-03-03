from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Union, List

from app.schemas.currency import Currency


class LineItem(BaseModel):
    name: str
    description: str
    amount: float
    currency: Currency
    quantity: int


class PaymentIn(BaseModel):
    project_id: int
    amount: float
    quantity: int
    currency: Currency
    successUrl: str
    cancelUrl: str
