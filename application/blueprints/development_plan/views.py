from datetime import datetime

from flask import Blueprint, abort, redirect, render_template, url_for

from application.blueprints.development_plan.forms import (
    DocumentForm,
    EventForm,
    PlanForm,
)
from application.extensions import db
from application.models import (
    DevelopmentPlan,
    DevelopmentPlanDocument,
    DevelopmentPlanEvent,
    DevelopmentPlanTimetable,
    DevelopmentPlanType,
    DocumentType,
    Organisation,
)

development_plan = Blueprint(
    "development_plan", __name__, url_prefix="/development-plan"
)


@development_plan.route("/<string:reference>")
def plan(reference):
    development_plan = DevelopmentPlan.query.get(reference)
    return render_template("plan/plan.html", development_plan=development_plan)


@development_plan.route("/<string:reference>/edit", methods=["GET", "POST"])
def edit(reference):
    plan = DevelopmentPlan.query.get(reference)

    form = PlanForm(obj=plan)
    form.organisations.choices = _get_organisation_choices()
    form.development_plan_type.choices = _get_plan_type_choices()
    if form.validate_on_submit():
        plan = _populate_plan(form, plan)
        db.session.add(plan)
        db.session.commit()
        return redirect(url_for("development_plan.plan", reference=plan.reference))

    return render_template("plan/edit.html", development_plan=plan, form=form)


@development_plan.route("/add", methods=["GET", "POST"])
def new():
    # check if creating record for a given LPA
    # requests.get...

    form = PlanForm()
    form.organisations.choices = _get_organisation_choices()
    form.development_plan_type.choices = _get_plan_type_choices()

    if form.validate_on_submit():
        plan = _populate_plan(form, DevelopmentPlan())
        db.session.add(plan)
        db.session.commit()
        return redirect(url_for("development_plan.plan", reference=plan.reference))

    return render_template("plan/new.html", form=form)


@development_plan.route("/<string:reference>/timetable/add", methods=["GET", "POST"])
def add_event(reference):
    plan = DevelopmentPlan.query.get(reference)

    form = EventForm()
    form.organisations.choices = _get_organisation_choices()
    form.development_plan_event.choices = _get_event_choices()

    if form.validate_on_submit():
        # model might need changing - this might be better modelled as plan has
        # one timetable which has many events.
        timetable = DevelopmentPlanTimetable()
        ref = f"{plan.reference}-{form.development_plan_event.data.lower().replace(' ', '-')}"
        timetable.reference = ref
        timetable.event_date = f"{form.event_date_year.data}-{form.event_date_month.data}-{form.event_date_day.data}"
        organisations = form.organisations.data
        del form.organisations
        form.populate_obj(timetable)
        for org in organisations:
            organisation = Organisation.query.get(org)
            timetable.organisations.append(organisation)

        plan.timetable.append(timetable)
        db.session.add(plan)
        db.session.commit()
        return redirect(url_for("development_plan.plan", reference=reference))

    return render_template("plan/add-event.html", development_plan=plan, form=form)


@development_plan.route(
    "/<string:reference>/timetable/<string:event_reference>/edit",
    methods=["GET", "POST"],
)
def edit_event(reference, event_reference):
    event = DevelopmentPlanTimetable.query.filter(
        DevelopmentPlanTimetable.development_plan_reference == reference,
        DevelopmentPlanTimetable.reference == event_reference,
    ).one_or_none()

    if event is None:
        return abort(404)

    form = EventForm(obj=event)
    form.organisations.choices = _get_organisation_choices()
    form.development_plan_event.choices = _get_event_choices()

    if form.validate_on_submit():
        # TODO: update event
        return redirect(url_for("development_plan.plan", reference=reference))

    # TODO: fix this as no edit event template exists yet
    return render_template("plan/edit-event.html", development_plan=plan, form=form)


@development_plan.get("/<string:reference>/timetable/<string:event_reference>/delete")
def delete_event(reference, event_reference):
    event = DevelopmentPlanTimetable.query.filter(
        DevelopmentPlanTimetable.development_plan_reference == reference,
        DevelopmentPlanTimetable.reference == event_reference,
    ).one_or_none()

    if event is None:
        return abort(404)
    event.end_date = datetime.today()
    db.session.add(event)
    db.session.commit()
    return redirect(url_for("development_plan.plan", reference=reference))


@development_plan.route("/<string:reference>/document/add", methods=["GET", "POST"])
def add_document(reference):
    plan = DevelopmentPlan.query.get(reference)

    form = DocumentForm()
    form.organisations.choices = _get_organisation_choices()
    form.document_type.choices = _get_document_type_choices()

    if form.validate_on_submit():
        document = DevelopmentPlanDocument()
        document.reference = f"{form.name.data.lower().replace(' ', '-')}"

        organisations = form.organisations.data
        del form.organisations
        form.populate_obj(document)
        for org in organisations:
            organisation = Organisation.query.get(org)
            document.organisations.append(organisation)

        plan.documents.append(document)
        db.session.add(plan)
        db.session.commit()
        return redirect(url_for("development_plan.plan", reference=reference))

    return render_template("plan/add-document.html", development_plan=plan, form=form)


def _populate_plan(form, plan):
    organisations = form.organisations.data
    del form.organisations

    form.populate_obj(plan)

    for org in organisations:
        organisation = Organisation.query.get(org)
        plan.organisations.append(organisation)

    return plan


def _get_organisation_choices():
    return [(org.organisation, org.name) for org in Organisation.query.all()]


def _get_plan_type_choices():
    return [
        (plan_type.reference, plan_type.name)
        for plan_type in DevelopmentPlanType.query.all()
    ]


def _get_event_choices():
    return [
        (evt.reference, evt.name)
        for evt in DevelopmentPlanEvent.query.order_by(DevelopmentPlanEvent.name).all()
    ]


def _get_document_type_choices():
    return [(doc.reference, doc.name) for doc in DocumentType.query.all()]
