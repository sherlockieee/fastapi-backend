from datetime import datetime
from enum import Enum
from sqlalchemy import Column, ForeignKey, Integer, Float, Enum, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.schemas.backer_status import BackerStatus
from app.schemas.currency import Currency


class BackerOrderProject(Base):
    __tablename__ = "backers_orders_projects"
    id = Column(
        Integer, nullable=False, primary_key=True, index=True, autoincrement=True
    )
    quantity = Column(Integer, nullable=False, default=0)
    price_per_credit = Column(Float, nullable=False, default=0)
    date_ordered = Column(DateTime(timezone=True), default=datetime.utcnow)
    status = Column(Enum(BackerStatus))
    currency = Column(Enum(Currency))
    backer_project_id = Column(Integer, ForeignKey("backer_project.id"))
    backer_project = relationship("BackerProject", back_populates="transactions")
