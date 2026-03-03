from fastapi import status, HTTPException, APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.schemas.token import Token
from app.schemas.user import UserCreate, UserInDB, UserOut
from app.utils.password import get_hashed_password, verify_password
from app.utils.token import create_access_token
from app.api.deps import get_db, get_current_user
import app.models as models
from app.config import settings

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserOut])
def get_users(db: Session = Depends(get_db), offset: int = 0, limit: int = 100):
    all_users = (
        db.query(models.User)
        .options(
            joinedload(models.User.projects_backed).options(
                joinedload(models.Transaction.project)
            )
        )
        .offset(offset)
        .limit(limit)
        .all()
    )
    return all_users


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

    user = models.User(
        email=user.email,
        hashed_password=get_hashed_password(user.password),
        full_name=user.full_name,
        preferred_name=user.preferred_name or user.full_name,
        is_admin=user.is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def sign_in(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user: UserInDB = (
        db.query(models.User).filter(models.User.email == form_data.username).first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User email doesn't exist"
        )
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User password is incorrect"
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserOut)
def get_current_user(user: models.User = Depends(get_current_user)):
    return user
