from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

import app.models as models
from app.api.deps import get_db
import app.schemas.tag as schema

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=List[schema.TagOut])
def get_tags(database: Session = Depends(get_db)):
    all_tags = database.query(models.Tag).all()
    return all_tags


@router.get("/{tag_id}", response_model=schema.TagOut)
def get_one_tag(tag_id: int, database: Session = Depends(get_db)):
    tag = database.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.TagOut)
def create_tag(tag: schema.TagIn, database: Session = Depends(get_db)):
    new_tag = models.Tag(**tag.dict())
    database.add(new_tag)
    database.commit()
    database.refresh(new_tag)
    return new_tag
