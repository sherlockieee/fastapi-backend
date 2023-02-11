from datetime import datetime
from enum import Enum
from sqlalchemy import Column, ForeignKey, Integer, Float, Enum, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.schemas.transaction_status import TransactionStatus
from app.schemas.currency import Currency


class Refund(Base):
    __tablename__ = "refunds"
    id = Column(
        Integer, primary_key=True, index=True, autoincrement=True, nullable=False
    )
    user_id = Column(ForeignKey("users.id"), index=True)
    project_id = Column(ForeignKey("projects.id"), index=True)
    transaction_id = Column(ForeignKey("transactions.id"), index=True)
    quantity = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    date_refunded = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(TransactionStatus, create_type=False))
    currency = Column(Enum(Currency, create_type=False))

    user = relationship("User", back_populates="projects_refunded")
    project = relationship("Project", back_populates="refunders")
    transaction = relationship("Transaction", back_populates="refund")

    def __getitem__(self, key):
        return self.__dict__[key] if key in self.__dict__ else None
