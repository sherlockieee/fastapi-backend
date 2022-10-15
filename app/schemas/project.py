from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from app.schemas.user import UserOut

from app.schemas.currency import Currency


class ProjectBase(BaseModel):
    title: str
    funding_needed: float
    currency: Currency
    total_raised: float = 0
    total_backers: int = 0
    description: Optional[str] = None
    end_date: datetime
    total_credits: int
    cost_per_credit: float
    needed_credits: int
    owner: UserOut
    backers: Optional[List[UserOut]] = []


class ProjectInTag(ProjectBase):
    id: int
    uuid: UUID
    created: datetime

    class Config:
        orm_mode = True


class ProjectIn(ProjectBase):
    tags: List["TagInProjectIn"]


class Project(ProjectBase):
    id: int
    uuid: UUID
    created: datetime
    tags: List["TagInProject"]

    class Config:
        use_enum_values = True
        orm_mode = True


class ProjectOut(Project):
    pass


from app.schemas.tag import TagInProject, TagInProjectIn

ProjectIn.update_forward_refs()
Project.update_forward_refs()
ProjectOut.update_forward_refs()
