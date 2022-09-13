from pydantic import BaseModel
from typing import List


class TagBase(BaseModel):
    name: str


class TagIn(TagBase):
    pass


class TagInProject(TagBase):
    id: int

    class Config:
        orm_mode = True


class Tag(TagBase):
    id: int
    projects: List["ProjectInTag"]

    class Config:
        orm_mode = True


class TagOut(Tag):
    pass


from app.schemas.project import ProjectInTag

Tag.update_forward_refs()
TagOut.update_forward_refs()
