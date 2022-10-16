from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

from app.schemas.currency import Currency


class ProjectBase(BaseModel):
    title: str
    funding_needed: float
    currency: Currency
    total_raised: float = 0
    total_backers: int = 0
    description: Optional[str] = None
    end_date: datetime
    total_credits: Optional[int] = 0
    cost_per_credit: Optional[float] = 0
    needed_credits: Optional[int] = 0


class ProjectIn(ProjectBase):
    tags: List["TagInProjectIn"]
    owner: Optional["UserInProject"]


class ProjectInTag(ProjectBase):
    id: int
    uuid: UUID
    created: datetime
    owner: Optional["UserInProject"]

    class Config:
        orm_mode = True


class ProjectInUser(ProjectBase):
    id: int
    uuid: UUID
    created: datetime
    tags: List["TagInProject"]


class Project(ProjectIn):
    id: int
    uuid: UUID
    created: datetime

    class Config:
        use_enum_values = True
        orm_mode = True


class ProjectOut(Project):
    pass


from app.schemas.tag import TagInProject, TagInProjectIn
from app.schemas.user import UserInProject

ProjectInTag.update_forward_refs()
ProjectIn.update_forward_refs()
Project.update_forward_refs()
ProjectOut.update_forward_refs()
