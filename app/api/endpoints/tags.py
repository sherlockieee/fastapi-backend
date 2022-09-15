from typing import List
from fastapi import APIRouter, status, HTTPException

import app.schemas.tag as schema
from app.prisma.prisma import db


router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=List[schema.TagOut])
async def get_tags(offset: int = 0, limit: int = 100):
    all_tags = await db.tag.find_many(
        skip=offset, take=limit, include={"projects": True}
    )
    return all_tags


@router.get("/{tag_id}", response_model=schema.TagOut)
async def get_one_tag(tag_id: int):
    tag = await db.tag.find_unique(where={"id": tag_id}, include={"projects": True})
    if not tag:
        raise HTTPException(status_code=404, detail="tag not found")
    return tag


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.TagOut)
async def create_tag(tag: schema.TagIn):
    new_tag = await db.tag.create(data={**tag.dict()})

    # refresh
    new_tag = await db.tag.find_unique(
        where={"id": new_tag.id}, include={"projects": True}
    )
    return new_tag
