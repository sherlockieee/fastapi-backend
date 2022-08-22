from typing import List
import app.models as models
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session


from app.main import get_db
import app.schemas.notes as schema

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Hello World, from FastAPI"}


@router.get("/notes/", response_model=List[schema.Note])
def read_notes(database: Session = Depends(get_db)):
    all_notes = database.query(models.Notes).all()
    return all_notes


@router.post("/notes/", status_code=status.HTTP_201_CREATED, response_model=schema.Note)
def create_note(note: schema.NoteIn, database: Session = Depends(get_db)):
    new_note = models.Notes(text=note.text, completed=note.completed)
    database.add(new_note)
    database.commit()
    database.refresh(new_note)

    return new_note
