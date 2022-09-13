from uuid import uuid4
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
    Text,
    Enum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base
from app.schemas.currency import Currency


class Project(Base):
    __tablename__ = "projects"

    id = Column(
        Integer, primary_key=True, index=True, autoincrement=True, nullable=False
    )
    uuid = Column(UUID(as_uuid=True), default=uuid4, index=True, nullable=False)
    title = Column(String, nullable=False, index=True)
    funding_needed = Column(Float, nullable=False)
    currency = Column(Enum(Currency))
    total_raised = Column(Float)
    total_backers = Column(Integer)
    description = Column(Text)
    created = Column(DateTime(timezone=True), default=datetime.utcnow)
    end_date = Column(DateTime)
    tags = relationship("Tag", secondary="project_tags", back_populates="projects")

    def __repr__(self):
        return f"{self.title}: {self.tags}"
