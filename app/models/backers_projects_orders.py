from datetime import datetime
from enum import Enum
from sqlalchemy import Column, ForeignKey, Integer, Float, Enum, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.schemas.backer_status import BackerStatus
from app.schemas.currency import Currency


class BackerProjectOrder(Base):
    __tablename__ = "backers_projects_orders"

    backer_id = Column(ForeignKey("users.id"), primary_key=True, index=True)
    project_id = Column(ForeignKey("projects.id"), primary_key=True, index=True)
    quantity = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    date_ordered = Column(DateTime(timezone=True), default=datetime.utcnow)
    status = Column(Enum(BackerStatus))
    currency = Column(Enum(Currency))
