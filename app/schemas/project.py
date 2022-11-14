from datetime import datetime
from pydantic import BaseModel
from pydantic.utils import GetterDict
from typing import List, Optional, Any
from uuid import UUID

from app.schemas.currency import Currency
from app.schemas.project_status import ProjectStatus


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
    credits_sold: Optional[int] = 0
    status: Optional[ProjectStatus] = ProjectStatus.IN_FUNDING


class ProjectIn(ProjectBase):
    tags: Optional[List["TagInProjectIn"]] = []


class ProjectInTag(ProjectBase):
    id: int
    uuid: UUID
    created: datetime
    owner: Optional["UserInProject"] = None
    backers: Optional[List["UserInProjectNested"]] = None

    class Config:
        orm_mode = True


class ProjectInOwner(ProjectBase):
    id: int
    uuid: UUID
    created: datetime
    tags: List["TagInProject"]
    backers: Optional[List["UserInProjectNested"]] = None

    class Config:
        orm_mode = True


class ProjectInBacker(ProjectBase):
    id: int
    uuid: UUID
    created: datetime
    tags: List["TagInProject"]
    owner: Optional["UserInProject"] = None

    class Config:
        orm_mode = True


class BackerProjectGetter(GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        if key in {
            "id",
            "uuid",
            "created",
            "tags",
            "owner",
            "title",
            "funding_needed",
            "currency",
            "total_raised",
            "total_backers",
            "description",
            "end_date",
            "total_credits",
            "cost_per_credit",
            "credits_sold",
        }:
            return getattr(self._obj.project, key)
        else:
            return super(BackerProjectGetter, self).get(key, default)


class ProjectInBackerNested(ProjectInBacker):
    class Config:
        orm_mode = True
        getter_dict = BackerProjectGetter


class Project(ProjectIn):
    id: int
    uuid: UUID
    created: datetime
    owner: Optional["UserInProject"] = None
    backers: Optional[List["UserInProjectNested"]] = None

    class Config:
        use_enum_values = True
        orm_mode = True


class ProjectOut(Project):
    pass


class ProjectInBackerSummary(ProjectInBacker):
    total_credits_bought: int


from app.schemas.tag import TagInProject, TagInProjectIn
from app.schemas.user import UserInProject, UserInProjectNested

ProjectInTag.update_forward_refs()
ProjectInOwner.update_forward_refs()
ProjectInBacker.update_forward_refs()
ProjectInBackerNested.update_forward_refs()
ProjectIn.update_forward_refs()
Project.update_forward_refs()
ProjectOut.update_forward_refs()
ProjectInBackerSummary.update_forward_refs()
