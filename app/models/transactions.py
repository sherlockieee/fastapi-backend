from datetime import datetime
from enum import Enum
from sqlalchemy import Column, ForeignKey, Integer, Float, Enum, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.schemas.transaction_status import TransactionStatus, TransactionType
from app.schemas.currency import Currency


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(
        Integer, primary_key=True, index=True, autoincrement=True, nullable=False
    )
    user_id = Column(ForeignKey("users.id"), index=True, primary_key=True)
    project_id = Column(ForeignKey("projects.id"), index=True, primary_key=True)
    quantity = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    date_ordered = Column(DateTime(timezone=True), default=datetime.utcnow)
    status = Column(Enum(TransactionStatus, create_type=False))
    currency = Column(Enum(Currency))
    type = Column(Enum(TransactionType, create_type=False))

    user = relationship("User", back_populates="projects_backed")
    project = relationship("Project", back_populates="users")

    def __getitem__(self, key):
        return self.__dict__[key]
