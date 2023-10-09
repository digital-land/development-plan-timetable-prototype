"""set adopted dates from existing plan timetables

Revision ID: a9f3e5e747b5
Revises: 4d9c0c4a7e08
Create Date: 2023-10-09 13:48:02.709867

"""
from alembic import op
from sqlalchemy.orm.session import Session

import sqlalchemy as sa

from application.models import DevelopmentPlan

# revision identifiers, used by Alembic.
revision = "a9f3e5e747b5"
down_revision = "4d9c0c4a7e08"
branch_labels = None
depends_on = None


def upgrade():
    session = Session(bind=op.get_bind())
    plans = session.query(DevelopmentPlan).all()
    for plan in plans:
        for event in plan.timetable:
            if event.development_plan_event == "plan-adopted":
                plan.adopted_date = event.event_date
                session.add(plan)
                session.commit()
                break


def downgrade():
    pass
