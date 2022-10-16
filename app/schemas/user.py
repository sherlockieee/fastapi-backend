from typing import Optional, List

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    is_active: Optional[bool] = True
    is_admin: Optional[bool] = False
    full_name: str
    preferred_name: Optional[str] = None
    is_project_owner: Optional[bool] = False
    is_backer: Optional[bool] = False


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInProject(UserBase):
    pass


class UserInDBBase(UserBase):
    id: Optional[int] = None
    projects_owned: Optional[List["ProjectInUser"]] = []

    class Config:
        orm_mode = True


class UserOut(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str


from app.schemas.project import ProjectInUser

UserInDBBase.update_forward_refs()
UserOut.update_forward_refs()
UserInDB.update_forward_refs()
