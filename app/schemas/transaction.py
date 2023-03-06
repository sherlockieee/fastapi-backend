from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from app.schemas.currency import Currency
from app.schemas.transaction_status import TransactionStatus


class TransactionBase(BaseModel):
    quantity: int
    amount: float
    currency: Currency


class TransactionIn(TransactionBase):
    project_id: int


class TransactionOut(TransactionBase):
    id: int
    date_ordered: datetime
    user: "UserInProject"
    project: "ProjectInBacker"
    status: TransactionStatus
    refund: Optional["RefundInTransaction"]

    class Config:
        orm_mode = True


class TransactionInRefund(TransactionBase):
    id: int
    date_ordered: datetime
    status: TransactionStatus

    class Config:
        orm_mode = True


from app.schemas.user import UserInProject
from app.schemas.project import ProjectInBacker

from app.schemas.refund import RefundInTransaction

TransactionOut.update_forward_refs()
TransactionInRefund.update_forward_refs()
