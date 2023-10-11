from sqlalchemy import JSON
from sqlalchemy.orm import mapped_column

from application.extensions import db


class DateModel(db.Model):
    __abstract__ = True

    entry_date = db.Column(db.Date, default=db.func.current_date())
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    def as_dict(self):
        return {
            "entry-date": self.entry_date,
            "start-date": self.start_date,
            "end-date": self.end_date,
        }


class DevelopmentPlanType(DateModel):
    __tablename__ = "development_plan_type"

    reference = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)

    def as_dict(self):
        return {
            "reference": self.reference,
            "name": self.name,
            "description": self.description,
        } | super().as_dict()


class DevelopmentPlanEventType(DateModel):
    __tablename__ = "development_plan_event_type"

    reference = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)
    notes = db.Column(db.Text)

    # for csv export
    def as_dict(self):
        return {
            "reference": self.reference,
            "name": self.name,
            "notes": self.notes,
        } | super().as_dict()

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

    def as_dict(self):
        return {
            "reference": self.reference,
            "name": self.name,
            "category": self.category,
        } | super().as_dict()


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

development_plan_event_organisation = db.Table(
    "development_plan_event_organisation",
    db.Column(
        "development_plan_event",
        db.Text,
        db.ForeignKey("development_plan_event.reference"),
    ),
    db.Column("organisation", db.Text, db.ForeignKey("organisation.organisation")),
)


class DevelopmentPlanGeography(DateModel):
    reference = db.Column(db.Text, primary_key=True)
    prefix = db.Column(db.Text)
    name = db.Column(db.Text)
    notes = db.Column(db.Text)
    geometry = db.Column(db.Text)
    geojson = db.Column(JSON)
    point = db.Column(db.Text)
    development_plan_geography_type = db.Column(db.Text)
    development_plan_reference = mapped_column(
        db.ForeignKey("development_plan.reference")
    )
    development_plan = db.relationship("DevelopmentPlan")
    point = db.Column(db.Text)


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

    # use string as date may be incomplete - e.g. 2023-10
    adopted_date = db.Column(db.String)

    organisations = db.relationship(
        "Organisation",
        secondary=development_plan_organisation,
        lazy="subquery",
        back_populates="development_plans",
    )

    timetable = db.relationship(
        "DevelopmentPlanEvent",
        back_populates="development_plan",
        order_by="DevelopmentPlanEvent.event_date",
    )

    documents = db.relationship(
        "DevelopmentPlanDocument", back_populates="development_plan"
    )

    geographies = db.relationship(
        "DevelopmentPlanGeography", back_populates="development_plan"
    )

    def as_dict(self):
        orgs = ";".join([org.organisation for org in self.organisations])
        return {
            "reference": self.reference,
            "name": self.name,
            "description": self.description,
            "development-plan-type": self.development_plan_type,
            "period-start-date": self.period_start_date,
            "period-end-date": self.period_end_date,
            "documentation-url": self.documentation_url,
            "adopted-date": self.adopted_date,
            "notes": self.notes,
            "organisations": orgs,
        } | super().as_dict()


class DevelopmentPlanEvent(DateModel):
    __tablename__ = "development_plan_event"

    reference = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)
    development_plan_event = db.Column(db.Text)
    event_date = db.Column(db.String)
    notes = db.Column(db.Text)

    organisations = db.relationship(
        "Organisation",
        secondary=development_plan_event_organisation,
        lazy="subquery",
        back_populates="development_plan_timetables",
    )

    development_plan_reference = mapped_column(
        db.ForeignKey("development_plan.reference")
    )
    development_plan = db.relationship("DevelopmentPlan")

    def as_dict(self):
        orgs = ";".join([org.organisation for org in self.organisations])
        return {
            "reference": self.reference,
            "name": self.name,
            "event-date": self.event_date,
            "development-plan": self.development_plan_reference,
            "notes": self.notes,
            "organisations": orgs,
        } | super().as_dict()


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

    def as_dict(self):
        orgs = ";".join([org.organisation for org in self.organisations])
        return {
            "reference": self.reference,
            "name": self.name,
            "description": self.description,
            "document-type": self.document_type,
            "documentation-url": self.documentation_url,
            "document-url": self.document_url,
            "development-plan": self.development_plan_reference,
            "notes": self.notes,
            "organisations": orgs,
        } | super().as_dict()


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
        "DevelopmentPlanEvent",
        secondary=development_plan_event_organisation,
        lazy="subquery",
        back_populates="organisations",
    )
