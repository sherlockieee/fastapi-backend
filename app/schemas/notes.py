from pydantic import BaseModel


class NoteIn(BaseModel):
    text: str
    completed: bool


class Note(NoteIn):
    id: int

    class Config:
        orm_mode = True
