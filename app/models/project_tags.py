from sqlalchemy import (
    Column,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.db import Base


class ProjectTag(Base):
    __tablename__ = "project_tags"

    project_id = Column(ForeignKey("projects.id"), primary_key=True)
    tag_id = Column(ForeignKey("tags.id"), primary_key=True)
    project = relationship("Project", back_populates="tags")
    tag = relationship("Tag", back_populates="projects")
