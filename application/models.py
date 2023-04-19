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

    def to_dict(self):
        return {
            "reference": self.reference,
            "name": self.name,
            "description": self.notes,
        }


class DocumentType(DateModel):
    __tablename__ = "document_type"

    reference = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)
    category = db.Column(db.Text)


development_plan_organisation = db.Table(
    "development_plan_organisation",
    db.Column("development_plan", db.Text, db.ForeignKey("development_plan.reference")),
    db.Column("organisation", db.Text, db.ForeignKey("organisation.organisation")),
)


development_plan_document_organisation = db.Table(
    "development_plan_document_organisation",
    db.Column(
        "development_plan_document",
        db.Text,
        db.ForeignKey("development_plan_document.reference"),
    ),
    db.Column("organisation", db.Text, db.ForeignKey("organisation.organisation")),
)

development_plan_timetable_organisation = db.Table(
    "development_plan_timetable_organisation",
    db.Column(
        "development_plan_timetable",
        db.Text,
        db.ForeignKey("development_plan_timetable.reference"),
    ),
    db.Column("organisation", db.Text, db.ForeignKey("organisation.organisation")),
)


class DevelopmentPlan(DateModel):
    __tablename__ = "development_plan"

    reference = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    development_plan_type = db.Column(db.Text)
    period_start_date = db.Column(db.Integer)
    period_end_date = db.Column(db.Integer)
    documentation_url = db.Column(db.Text)
    notes = db.Column(db.Text)

    organisations = db.relationship(
        "Organisation",
        secondary=development_plan_organisation,
        lazy="subquery",
        back_populates="development_plans",
    )

    timetable = db.relationship(
        "DevelopmentPlanTimetable", back_populates="development_plan"
    )

    documents = db.relationship(
        "DevelopmentPlanDocument", back_populates="development_plan"
    )


class DevelopmentPlanTimetable(DateModel):
    __tablename__ = "development_plan_timetable"

    reference = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)
    development_plan_event = db.Column(db.Text)
    event_date = db.Column(db.String)
    notes = db.Column(db.Text)

    organisations = db.relationship(
        "Organisation",
        secondary=development_plan_timetable_organisation,
        lazy="subquery",
        back_populates="development_plan_timetables",
    )

    development_plan_reference = mapped_column(
        db.ForeignKey("development_plan.reference")
    )
    development_plan = db.relationship("DevelopmentPlan")


class DevelopmentPlanDocument(DateModel):
    __tablename__ = "development_plan_document"

    reference = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    document_type = db.Column(db.Text)
    documentation_url = db.Column(db.Text)
    document_url = db.Column(db.Text)
    notes = db.Column(db.Text)

    organisations = db.relationship(
        "Organisation",
        secondary=development_plan_document_organisation,
        lazy="subquery",
        back_populates="development_plan_documents",
    )

    development_plan_reference = mapped_column(
        db.ForeignKey("development_plan.reference")
    )
    development_plan = db.relationship("DevelopmentPlan")


class Organisation(DateModel):
    organisation = db.Column(db.Text, primary_key=True)
    addressbase_custodian = db.Column(db.Text)
    billing_authority = db.Column(db.Text)
    census_area = db.Column(db.Text)
    combined_authority = db.Column(db.Text)
    company = db.Column(db.Text)
    entity = db.Column(db.BigInteger)
    esd_inventory = db.Column(db.Text)
    local_authority_type = db.Column(db.Text)
    local_resilience_forum = db.Column(db.Text)
    name = db.Column(db.Text)
    notes = db.Column(db.Text)
    official_name = db.Column(db.Text)
    opendatacommunities_uri = db.Column(db.Text)
    parliament_thesaurus = db.Column(db.Text)
    prefix = db.Column(db.Text)
    reference = db.Column(db.Text)
    region = db.Column(db.Text)
    shielding_hub = db.Column(db.Text)
    statistical_geography = db.Column(db.Text)
    twitter = db.Column(db.Text)
    website = db.Column(db.Text)
    wikidata = db.Column(db.Text)
    wikipedia = db.Column(db.Text)

    development_plans = db.relationship(
        "DevelopmentPlan",
        secondary=development_plan_organisation,
        lazy="subquery",
        back_populates="organisations",
    )

    development_plan_documents = db.relationship(
        "DevelopmentPlanDocument",
        secondary=development_plan_document_organisation,
        lazy="subquery",
        back_populates="organisations",
    )

    development_plan_timetables = db.relationship(
        "DevelopmentPlanTimetable",
        secondary=development_plan_timetable_organisation,
        lazy="subquery",
        back_populates="organisations",
    )
