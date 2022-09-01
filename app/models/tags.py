from sqlalchemy import (
    Column,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from app.db import Base


class Tag(Base):
    __tablename__ = "tags"
    id = Column(
        Integer, primary_key=True, index=True, autoincrement=True, nullable=False
    )
    name = Column(String, nullable=False)
    projects = relationship("ProjectTag", back_populates="tag")
