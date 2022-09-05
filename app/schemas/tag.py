from pydantic import BaseModel
from typing import List


class TagBase(BaseModel):
    name: str


class TagIn(TagBase):
    pass


class TagInProject(TagBase):
    id: int


class Tag(TagBase):
    id: int
    projects: List["Project"]

    class Config:
        orm_mode = True


class TagOut(Tag):
    pass


from app.schemas.project import Project

Tag.update_forward_refs()
TagOut.update_forward_refs()
