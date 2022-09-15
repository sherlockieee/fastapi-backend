from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import insert


import app.models as models
from app.main import get_db
import app.schemas.project as schema
from app.models import project_tags


router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[schema.ProjectOut])
def get_projects(
    database: Session = Depends(get_db), offset: int = 0, limit: int = 100
):
    all_projects = database.query(models.Project).offset(offset).limit(limit).all()
    return all_projects


@router.get("/{project_id}", response_model=schema.ProjectOut)
def get_one_project(project_id: int, database: Session = Depends(get_db)):
    project = (
        database.query(models.Project).filter(models.Project.id == project_id).first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.ProjectOut)
def create_project(project: schema.ProjectIn, database: Session = Depends(get_db)):
    new_project = models.Project(**project.dict())
    database.add(new_project)
    database.commit()
    database.refresh(new_project)
    return new_project


@router.post(
    "/{project_id}/tags/{tag_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=schema.ProjectOut,
)
def add_tag_to_project(project_id: int, tag_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.execute(insert(project_tags).values(project_id=project_id, tag_id=tag_id))
    db.commit()
    db.refresh(project)
    return project
