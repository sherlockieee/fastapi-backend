"""bru idek

Revision ID: 360bd105612d
Revises: 84bd6bafac82
Create Date: 2022-10-25 19:45:13.523529+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "360bd105612d"
down_revision = "84bd6bafac82"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "backers_projects_orders",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("backer_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("date_ordered", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "SUCCESS",
                "PENDING",
                "CANCELLED",
                "BANNED",
                name="backerstatus_type",
            ),
            nullable=True,
        ),
        sa.Column(
            "currency", sa.Enum("USD", "EUR", name="currency_type"), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["backer_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
        ),
        sa.PrimaryKeyConstraint("id", "backer_id", "project_id"),
    )
    op.create_index(
        op.f("ix_backers_projects_orders_backer_id"),
        "backers_projects_orders",
        ["backer_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_backers_projects_orders_id"),
        "backers_projects_orders",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_backers_projects_orders_project_id"),
        "backers_projects_orders",
        ["project_id"],
        unique=False,
    )
    op.add_column("projects", sa.Column("credits_sold", sa.Integer(), nullable=True))

    op.drop_column("projects", "needed_credits")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "projects",
        sa.Column("needed_credits", sa.INTEGER(), autoincrement=False, nullable=True),
    )

    op.drop_column("projects", "credits_sold")
    op.drop_index(
        op.f("ix_backers_projects_orders_project_id"),
        table_name="backers_projects_orders",
    )
    op.drop_index(
        op.f("ix_backers_projects_orders_id"), table_name="backers_projects_orders"
    )
    op.drop_index(
        op.f("ix_backers_projects_orders_backer_id"),
        table_name="backers_projects_orders",
    )
    op.drop_table("backers_projects_orders")
    # ### end Alembic commands ###
