from datetime import datetime
from enum import Enum
from sqlalchemy import Column, ForeignKey, Integer, Float, Enum, DateTime
from app.db.base_class import Base
from app.schemas.backer_status import BackerStatus
from app.schemas.currency import Currency


class BackerProjectOrder(Base):
    __tablename__ = "backers_projects_orders"
    id = Column(
        Integer, primary_key=True, index=True, autoincrement=True, nullable=False
    )
    backer_id = Column(ForeignKey("users.id"), index=True, primary_key=True)
    project_id = Column(ForeignKey("projects.id"), index=True, primary_key=True)
    quantity = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    date_ordered = Column(DateTime(timezone=True), default=datetime.utcnow)
    status = Column(Enum(BackerStatus))
    currency = Column(Enum(Currency))
