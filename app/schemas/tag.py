from pydantic import BaseModel
from typing import List


class TagBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class TagIn(TagBase):
    pass


class Tag(TagBase):
    projects: List["Project"]
    pass


class TagOut(Tag):
    pass


from app.schemas.project import Project

Tag.update_forward_refs()
TagOut.update_forward_refs()
