from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db import Base


project_tags = Table(
    "project_tags",
    Base.metadata,
    Column("project_id", ForeignKey("projects.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)
