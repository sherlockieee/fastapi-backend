from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from app.schemas.currency import Currency
from app.schemas.transaction_status import TransactionStatus


class PayoutBase(BaseModel):
    quantity: int
    amount: float
    currency: Currency


class PayoutIn(PayoutBase):
    project_id: int


class PayoutOut(PayoutBase):
    id: int
    created_at: datetime
    user: "UserInProject"
    project: "ProjectInBacker"
    status: TransactionStatus

    class Config:
        orm_mode = True

from app.schemas.user import UserInProject
from app.schemas.project import ProjectInBacker


PayoutOut.update_forward_refs()
