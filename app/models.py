from sqlalchemy import Column, Integer, String, Boolean
from app.db import Base


class Notes(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    completed = Column(Boolean)
