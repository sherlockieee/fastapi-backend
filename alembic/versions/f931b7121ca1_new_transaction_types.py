"""new transaction types

Revision ID: f931b7121ca1
Revises: 654f30e763d9
Create Date: 2023-02-02 05:04:26.890034+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "f931b7121ca1"
down_revision = "654f30e763d9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.rename_table("backers_projects_orders", "transactions")
    op.execute("ALTER INDEX ix_backers_projects_orders_id RENAME TO ix_transactions_id")
    op.execute(
        "ALTER INDEX ix_backers_projects_orders_project_id RENAME TO ix_transactions_project_id"
    )
    op.execute(
        "ALTER INDEX ix_backers_projects_orders_backer_id RENAME TO ix_transactions_user_id"
    )
    op.alter_column(
        "transactions", "backer_id", nullable=False, new_column_name="user_id"
    )
    transactiontype = postgresql.ENUM(
        "CROWDFUND", "REFUND", "PAYOUT", name="transactiontype"
    )
    transactiontype.create(op.get_bind())
    op.add_column(
        "transactions",
        sa.Column(
            "type",
            sa.Enum("CROWDFUND", "REFUND", "PAYOUT", name="transactiontype"),
            nullable=True,
            default="CROWDFUND",
        ),
    )
    op.execute("UPDATE transactions SET type = 'CROWDFUND' WHERE type IS NULL")
    op.alter_column("transactions", "type", nullable=False)
    op.add_column("projects", sa.Column("updated_at", sa.DateTime(), nullable=True))
    op.alter_column(
        "projects",
        "created",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "projects",
        "created",
        existing_type=sa.DateTime(),
        type_=postgresql.TIMESTAMP(timezone=True),
        existing_nullable=True,
    )
    op.drop_column("projects", "updated_at")
    op.rename_table("transactions", "backers_projects_orders")
    op.execute("ALTER INDEX ix_transactions_id RENAME TO ix_backers_projects_orders_id")
    op.execute(
        "ALTER INDEX ix_transactions_project_id RENAME TO ix_backers_projects_orders_project_id"
    )
    op.execute(
        "ALTER INDEX ix_transactions_user_id RENAME TO ix_backers_projects_orders_backer_id"
    )
    op.alter_column(
        "backers_projects_orders",
        "user_id",
        nullable=False,
        new_column_name="backer_id",
    )
    op.drop_column("backers_projects_orders", "type")
    transactiontype = postgresql.ENUM(
        "CROWDFUND", "REFUND", "PAYOUT", name="transactiontype"
    )
    transactiontype.drop(op.get_bind())

    # ### end Alembic commands ###