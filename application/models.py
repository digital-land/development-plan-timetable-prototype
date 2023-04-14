from sqlalchemy.orm import mapped_column

from application.extensions import db


class DateModel(db.Model):
    __abstract__ = True

    entry_date = db.Column(db.Date, default=db.func.current_date())
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)


class DevelopmentPlanType(DateModel):

    __tablename__ = "development_plan_type"

    reference = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)


class DevelopmentPlanEvent(DateModel):

    __tablename__ = "development_plan_event"

    reference = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)
    notes = db.Column(db.Text)


class DocumentType(DateModel):

    __tablename__ = "document_type"

    reference = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)
    category = db.Column(db.Text)


class DevelopmentPlan(DateModel):

    __tablename__ = "development_plan"

    reference = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    development_plan_type = mapped_column(
        db.ForeignKey("development_plan_type.reference")
    )
    period_start_date = db.Column(db.Integer)
    period_end_date = db.Column(db.Integer)
    documentation_url = db.Column(db.Text)
    notes = db.Column(db.Text)
    organisation = db.Column(db.Text)

    timetable = db.relationship("DevelopmentPlanTimetable")

    documents = db.relationship("DevelopmentPlanDocument")


class DevelopmentPlanTimetable(DateModel):

    __tablename__ = "development_plan_timetable"

    reference = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)
    development_plan_event = mapped_column(
        db.ForeignKey("development_plan_event.reference")
    )
    event_date = db.Column(db.String)
    notes = db.Column(db.Text)
    organisation = db.Column(db.Text)

    development_plan = mapped_column(db.ForeignKey("development_plan.reference"))


class DevelopmentPlanDocument(DateModel):

    __tablename__ = "development_plan_document"

    reference = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    document_type = mapped_column(db.ForeignKey("document_type.reference"))
    documentation_url = db.Column(db.Text)
    document_url = db.Column(db.Text)
    notes = db.Column(db.Text)
    organisation = db.Column(db.Text)

    development_plan = mapped_column(db.ForeignKey("development_plan.reference"))
