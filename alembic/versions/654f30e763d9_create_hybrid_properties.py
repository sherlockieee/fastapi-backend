"""create hybrid properties

Revision ID: 654f30e763d9
Revises: 30cefa4a2487
Create Date: 2022-11-27 15:32:43.622049+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "654f30e763d9"
down_revision = "30cefa4a2487"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("projects", "total_backers")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "projects",
        sa.Column("total_backers", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    # ### end Alembic commands ###
