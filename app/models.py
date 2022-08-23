from uuid import uuid4
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class ProjectTag(Base):
    __tablename__ = "project_tags"

    project_id = Column(ForeignKey("projects.id"), primary_key=True)
    tag_id = Column(ForeignKey("tags.id"), primary_key=True)
    project = relationship("Project", back_populates="tags")
    tag = relationship("Tag", back_populates="projects")


class Project(Base):
    __tablename__ = "projects"

    id = Column(
        Integer, primary_key=True, index=True, autoincrement=True, nullable=False
    )
    uuid = Column(UUID(as_uuid=True), default=uuid4, index=True, nullable=False)
    title = Column(String, nullable=False, index=True)
    funding_needed = Column(Float, nullable=False)
    currency = Column(String)
    total_raised = Column(Float)
    total_backers = Column(Integer)
    description = Column(Text)
    created = Column(DateTime)
    end_date = Column(DateTime)
    tags = relationship("ProjectTag", back_populates="project")


class Tag(Base):
    __tablename__ = "tags"
    id = Column(
        Integer, primary_key=True, index=True, autoincrement=True, nullable=False
    )
    name = Column(String, nullable=False)
    projects = relationship("ProjectTag", back_populates="tag")
