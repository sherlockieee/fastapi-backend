"""create notes table

Revision ID: 88c449c9ae11
Revises: 
Create Date: 2022-08-10 11:49:02.746675

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "88c449c9ae11"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "notes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("text", sa.String),
        sa.Column("completed", sa.Boolean),
    )


def downgrade():
    op.drop_table("notes")
