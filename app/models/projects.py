from uuid import uuid4
import sqlalchemy as sa
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
    Text,
    Enum,
    ForeignKey,
    select,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property


from app.db.base_class import Base
from app.schemas.currency import Currency
from app.schemas.project_status import ProjectStatus
from app.models.transactions import Transaction
from app.models.user import User
from app.models.refunds import Refund


class Project(Base):
    __tablename__ = "projects"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        unique=True,
    )
    uuid = Column(UUID(as_uuid=True), default=uuid4, index=True, nullable=False)
    title = Column(String, nullable=False, index=True)
    funding_needed = Column(Float, nullable=False)
    currency = Column(Enum(Currency))
    total_raised = Column(Float)
    description = Column(Text)
    created = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    total_credits = Column(Integer)
    cost_per_credit = Column(Float)
    credits_sold = Column(Integer)
    tags = relationship("Tag", secondary="project_tags", back_populates="projects")
    owner_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(ProjectStatus))
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    image_url = Column(
        String, default="https://arbordayblog.org/wp-content/uploads/2016/06/tree.jpg"
    )

    owner = relationship("User", back_populates="projects_owned")
    users = relationship("Transaction", back_populates="project")
    refunds = relationship("Refund", back_populates="project")
    payout = relationship("Payout", back_populates="project")

    def __getitem__(self, key):
        return self.__dict__[key]

    @hybrid_property
    def remaining_credits(self):
        return max(self.total_credits - self.credits_sold, 0)

    @remaining_credits.expression
    def remaining_credits(cls):
        return sa.case(
            [
                (
                    cls.total_credits - cls.credits_sold > 0,
                    cls.total_credits - cls.credits_sold,
                ),
            ],
            else_=0,
        ).label("remaining_credits")

    @hybrid_property
    def remaining_funding(self) -> int:
        return (
            self.funding_needed - self.total_raised
            if self.funding_needed > self.total_raised
            else 0
        )

    @remaining_funding.expression
    def remaining_funding(cls):
        return sa.case(
            [
                (
                    cls.funding_needed - cls.total_raised > 0,
                    cls.funding_needed - cls.total_raised,
                ),
            ],
            else_=0,
        ).label("remaining_funding")

    @hybrid_property
    def percentage_raised(self) -> int:
        return round((self.total_raised / self.funding_needed) * 100)

    @percentage_raised.expression
    def percentage_raised(cls):
        return sa.func.round((cls.total_raised / cls.funding_needed) * 100).label(
            "percentage_raised"
        )

    @hybrid_property
    def days_remaining(self) -> int:
        days_difference = (
            (self.end_date - datetime.utcnow()).total_seconds() / 3600 / 24
        )
        return max(days_difference, 0)

    @days_remaining.expression
    def days_remaining(cls):
        days_remaining_query = sa.func.round(
            sa.func.extract("epoch", (cls.end_date - sa.func.now())) / 86400
        )
        return sa.case(
            [
                (
                    days_remaining_query > 0,
                    days_remaining_query,
                ),
            ],
            else_=0,
        ).label("days_remaining")


#    @hybrid_property
# def total_users(self) -> int:
#     return len(set(self.users))

# @total_users.expression
# def total_users(cls):
#     # return (
#     #     sa.select(Transaction.user_id)
#     #     .group_by(Transaction.user_id)
#     #     .join(Transaction, cls.id == Transaction.project_id)
#     #     .where(Transaction.project_id == cls.id)
#     #     .count()
#     #     .label("total_users")
#     # )
#     return sa.select(
#         [sa.func.count(Transaction.user_id).where(Transaction.project_id == cls.id)]
#     ).label("total_users")


# print(select(Project.total_users))
