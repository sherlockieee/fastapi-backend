from datetime import datetime
from enum import Enum
from sqlalchemy import Column, ForeignKey, Integer, Float, Enum, DateTime
from sqlalchemy.orm import relationship, backref
from app.db.base_class import Base
from app.schemas.transaction_status import TransactionStatus, TransactionType
from app.schemas.currency import Currency


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        unique=True,
        nullable=False,
    )
    user_id = Column(ForeignKey("users.id"), index=True, primary_key=True)
    project_id = Column(ForeignKey("projects.id"), index=True, primary_key=True)
    quantity = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    date_ordered = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(TransactionStatus, create_type=False))
    currency = Column(Enum(Currency, create_type=False))

    user = relationship("User", back_populates="projects_backed")
    project = relationship("Project", back_populates="users")
    refund = relationship("Refund", uselist=False, back_populates="transaction")

    def __getitem__(self, key):
        return self.__dict__[key]
