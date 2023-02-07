"""create refund table

Revision ID: 257b66d9f085
Revises: f931b7121ca1
Create Date: 2023-02-07 05:34:31.533906+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from app.schemas.currency import Currency


# revision identifiers, used by Alembic.
revision = "257b66d9f085"
down_revision = "f931b7121ca1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    currency_enum = postgresql.ENUM(Currency, name="currency_enum", create_type=False)
    currency_enum.create(op.get_bind(), checkfirst=True)
    op.create_unique_constraint("uq_transaction_id", "transactions", ["id"])

    op.create_table(
        "refunds",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column(
            "transaction_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("date_refunded", sa.DateTime(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "SUCCESS", "PENDING", "CANCELLED", "BANNED", name="transactionstatus"
            ),
            nullable=True,
        ),
        sa.Column(
            "currency",
            currency_enum,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
        ),
        sa.ForeignKeyConstraint(
            ["transaction_id"],
            ["transactions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_refunds_id"), "refunds", ["id"], unique=False)
    op.create_index(
        op.f("ix_refunds_project_id"), "refunds", ["project_id"], unique=False
    )
    op.create_index(
        op.f("ix_refunds_transaction_id"), "refunds", ["transaction_id"], unique=False
    )
    op.create_index(op.f("ix_refunds_user_id"), "refunds", ["user_id"], unique=False)

    op.drop_column("transactions", "type")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "transactions",
        sa.Column(
            "type",
            postgresql.ENUM("CROWDFUND", "REFUND", "PAYOUT", name="transactiontype"),
            autoincrement=False,
            nullable=False,
        ),
    )

    op.drop_index(op.f("ix_refunds_user_id"), table_name="refunds")
    op.drop_index(op.f("ix_refunds_transaction_id"), table_name="refunds")
    op.drop_index(op.f("ix_refunds_project_id"), table_name="refunds")
    op.drop_index(op.f("ix_refunds_id"), table_name="refunds")
    op.drop_constraint("uq_transaction_id", "transactions")

    op.drop_table("refunds")
    # ### end Alembic commands ###
