from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from datetime import datetime
from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer, primary_key=True, index=True, autoincrement=True, nullable=False
    )
    full_name = Column(String, index=True, nullable=False)
    preferred_name = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    joined_date = Column(DateTime, default=datetime.utcnow)
    is_project_owner = Column(Boolean, default=False)
    projects_owned = relationship("Project", back_populates="owner")
    is_backer = Column(Boolean, default=False)
    # projects_backed = relationship(
    #     "Project", secondary="backers_projects", back_populates="project"
    # )
