from fastapi import status, HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.schemas.user import UserCreate, UserOut
from app.utils.password import get_hashed_password
from app.main import get_db
import app.models as models

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # querying database to check if user already exist
    existing_user = (
        db.query(models.User).filter(models.User.email == user.email).first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist",
        )

    user_obj = models.User(
        email=user.email,
        hashed_password=get_hashed_password(user.password),
        full_name=user.full_name,
        preferred_name=user.preferred_name or user.full_name,
        is_admin=user.is_admin,
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user


@router.get("/", response_model=List[UserOut])
def get_users(db: Session = Depends(get_db), offset: int = 0, limit: int = 100):
    all_users = db.query(models.User).offset(offset).limit(limit).all()
    return all_users
