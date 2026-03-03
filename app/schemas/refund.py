from datetime import datetime
from pydantic import BaseModel

from app.schemas.currency import Currency
from app.schemas.transaction_status import TransactionStatus


class RefundBase(BaseModel):
    quantity: int
    amount: float
    currency: Currency
    transaction_id: int


class RefundOut(RefundBase):
    id: int
    date_refunded: datetime
    user: "UserInProject"
    project: "ProjectInBacker"
    status: TransactionStatus
    transaction: "TransactionInRefund"

    class Config:
        orm_mode = True


class RefundInTransaction(RefundBase):
    id: int
    date_refunded: datetime
    status: TransactionStatus

    class Config:
        orm_mode = True


from app.schemas.user import UserInProject
from app.schemas.project import ProjectInBacker
from app.schemas.transaction import TransactionInRefund

RefundOut.update_forward_refs()

