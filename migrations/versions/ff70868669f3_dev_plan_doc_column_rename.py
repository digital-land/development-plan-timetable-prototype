"""dev plan doc column rename

Revision ID: ff70868669f3
Revises: d3db89280ef7
Create Date: 2024-09-12 10:50:27.935851

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ff70868669f3"
down_revision = "d3db89280ef7"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "development_plan_document",
        "development_plan_reference",
        new_column_name="development_plan",
    )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "development_plan_document",
        "development_plan",
        new_column_name="development_plan_reference",
    )

    # ### end Alembic commands ###