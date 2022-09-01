from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class Currency(Enum):
    USD = "USD"
    EUR = "EUR"


class ProjectIn(BaseModel):
    title: str
    funding_needed: float
    currency: Currency
    total_raised: float = 0
    total_backers: int = 0
    description: Optional[str] = None
    end_date: datetime
    tags: List["Tag"]


class Project(ProjectIn):
    id: int
    uuid: UUID
    created: datetime

    class Config:
        use_enum_values = True
        orm_mode = True


class ProjectOut(Project):
    pass


from app.schemas.tag import Tag

ProjectIn.update_forward_refs()
Project.update_forward_refs()
ProjectOut.update_forward_refs()
