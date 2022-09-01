from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

import app.models as models
from app.main import get_db
import app.schemas.project as schema

router = APIRouter()


@router.get("/", response_model=List[schema.ProjectOut])
def read_notes(database: Session = Depends(get_db)):
    all_projects = database.query(models.Project).all()
    return all_projects


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.ProjectOut)
def create_project(project: schema.ProjectIn, database: Session = Depends(get_db)):
    new_project = models.Project(**project.dict())
    database.add(new_project)
    database.commit()
    database.refresh(new_project)
    return new_project
