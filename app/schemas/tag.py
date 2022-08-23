from pydantic import BaseModel
from typing import List


class TagBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


from app.schemas.project import ProjectBase


class TagSchema(TagBase):
    projects: List[ProjectBase]
