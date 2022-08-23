from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

import app.models as models
from app.main import get_db
import app.schemas.project as schema

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Hello World, from FastAPI"}


@router.get("/projects/", response_model=List[schema.ProjectOut])
def read_notes(database: Session = Depends(get_db)):
    all_projects = database.query(models.Project).all()
    return all_projects


# @router.post("/notes/", status_code=status.HTTP_201_CREATED, response_model=schema.Note)
# def create_note(note: schema.NoteIn, database: Session = Depends(get_db)):
#     new_note = models.Project(text=note.text, completed=note.completed)
#     database.add(new_note)
#     database.commit()
#     database.refresh(new_note)

#     return new_note
