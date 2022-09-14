from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

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
from app.schemas.currency import Currency


def get_database_url(url):
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


SQLALCHEMY_DATABASE_URI = get_database_url(settings.DATABASE_URL)


engine = create_engine(SQLALCHEMY_DATABASE_URI)


Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = {"extend_existing": True}

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
    # tags = relationship("Tag", secondary="project_tags", back_populates="projects")

    def __repr__(self):
        return f"{self.title}: {self.tags}"


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

Base.metadata.create_all(engine)
session.commit()
