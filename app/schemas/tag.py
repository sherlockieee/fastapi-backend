from pydantic import BaseModel
from typing import List


class TagBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class Tag(TagBase):
    pass


class TagSchema(TagBase):
    projects: "List[Project]"


from app.schemas.project import Project

Tag.update_forward_refs()
