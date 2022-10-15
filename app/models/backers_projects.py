from enum import Enum
from sqlalchemy import Column, ForeignKey, Integer, Float, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.schemas.backer_status import BackerStatus
from app.schemas.currency import Currency


class BackerProject(Base):
    __tablename__ = "backers_projects"
    id = Column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    backer_id = Column(ForeignKey("users.id"), primary_key=True, index=True)
    project_id = Column(ForeignKey("projects.id"), primary_key=True, index=True)
    total_credits_purchased = Column(Integer, nullable=False, default=0)
    transactions = relationship("BackerOrderProject", back_populates="backer_project")

    backer = relationship("User", back_populates="projects_backed")
    project = relationship("Project", back_populates="backers")
