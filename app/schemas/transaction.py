from datetime import datetime
from pydantic import BaseModel

from app.schemas.currency import Currency
from app.schemas.backer_status import BackerStatus


class TransactionBase(BaseModel):
    quantity: int
    amount: float
    currency: Currency


class TransactionIn(TransactionBase):
    project_id: int


class TransactionOut(TransactionBase):
    date_ordered: datetime
    backer: "UserInProject"
    project: "ProjectInBacker"
    status: BackerStatus

    class Config:
        orm_mode = True


from app.schemas.user import UserInProject
from app.schemas.project import ProjectInBacker

TransactionOut.update_forward_refs()
