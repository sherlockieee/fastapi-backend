from typing import Optional, List, Any

from pydantic import BaseModel
from pydantic.utils import GetterDict


class UserBase(BaseModel):
    email: str
    is_active: Optional[bool] = True
    is_admin: Optional[bool] = False
    full_name: str
    preferred_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInProject(UserBase):
    id: int

    class Config:
        orm_mode = True


class ProjectBackerGetter(GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        if key in {
            "id",
            "email",
            "full_name",
            "preferred_name",
            "is_admin",
            "is_active",
        }:
            return getattr(self._obj.user, key)
        else:
            return super(ProjectBackerGetter, self).get(key, default)


class UserInProjectNested(UserInProject):
    class Config:
        orm_mode = True
        getter_dict = ProjectBackerGetter


class UserInDBBase(UserBase):
    id: int
    projects_owned: Optional[List["ProjectInOwner"]]
    projects_backed: Optional[List["ProjectInBackerNested"]]

    class Config:
        orm_mode = True


class UserOut(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str


from app.schemas.project import ProjectInBacker, ProjectInOwner, ProjectInBackerNested

UserInDBBase.update_forward_refs()
UserOut.update_forward_refs()
UserInDB.update_forward_refs()
