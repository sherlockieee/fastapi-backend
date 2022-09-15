from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Union
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


class ProjectInTag(ProjectBase):
    id: int
    uuid: UUID
    created: datetime

    class Config:
        orm_mode = True


class ProjectIn(ProjectBase):
    tags: Union[List["TagBase"], List["TagInProject"]]


class Project(ProjectIn):
    id: int
    uuid: UUID
    created: datetime
    tags: List["TagInProject"]

    class Config:
        use_enum_values = True
        orm_mode = True


class ProjectOut(Project):
    pass


from app.schemas.tag import TagBase, TagInProject

ProjectIn.update_forward_refs()
Project.update_forward_refs()
ProjectOut.update_forward_refs()
