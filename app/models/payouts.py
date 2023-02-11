from datetime import datetime
from enum import Enum
from sqlalchemy import Column, ForeignKey, Integer, Float, Enum, DateTime
from sqlalchemy.orm import relationship, backref
from app.db.base_class import Base
from app.schemas.transaction_status import TransactionStatus, TransactionType
from app.schemas.currency import Currency


class Payout(Base):
    __tablename__ = "payouts"
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        unique=True,
    )
    user_id = Column(ForeignKey("users.id"), index=True, unique=True)
    project_id = Column(ForeignKey("projects.id"), index=True, unique=True)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(Enum(TransactionStatus, create_type=False))
    currency = Column(Enum(Currency, create_type=False))

    user = relationship("User", back_populates="projects_payout")
    project = relationship("Project", back_populates="payout")

    def __getitem__(self, key):
        return self.__dict__[key]
