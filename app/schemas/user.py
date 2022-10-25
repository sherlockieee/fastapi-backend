from typing import Optional, List

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
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


class UserInDBBase(UserBase):
    id: int
    projects_owned: Optional[List["ProjectInOwner"]]
    projects_backed: Optional[List["ProjectInBacker"]]

    class Config:
        orm_mode = True


class UserOut(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str


from app.schemas.project import ProjectInBacker, ProjectInOwner

UserInDBBase.update_forward_refs()
UserOut.update_forward_refs()
UserInDB.update_forward_refs()
