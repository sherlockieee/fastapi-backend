"""add status column

Revision ID: 30cefa4a2487
Revises: 360bd105612d
Create Date: 2022-11-14 18:38:51.889176+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "30cefa4a2487"
down_revision = "360bd105612d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    projectstatus = postgresql.ENUM(
        "CREATED",
        "IN_FUNDING",
        "SUCCESS",
        "FAIL",
        "BANNED",
        "IN_PROGRESS",
        "CREDITS_AVAILABLE",
        name="projectstatus",
    )

    projectstatus.create(op.get_bind())

    op.add_column(
        "projects",
        sa.Column(
            "status",
            projectstatus,
            nullable=True,
        ),
    )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    op.drop_column("projects", "status")
    op.execute("DROP TYPE projectstatus")
    # ### end Alembic commands ###
