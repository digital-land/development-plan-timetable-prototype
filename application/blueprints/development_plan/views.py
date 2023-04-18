from flask import Blueprint, redirect, render_template, url_for

from application.blueprints.development_plan.forms import (
    DocumentForm,
    EventForm,
    PlanForm,
)
from application.extensions import db
from application.models import (
    DevelopmentPlan,
    DevelopmentPlanTimetable,
    DevelopmentPlanType,
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
        plan = _populate_plan(form, DevelopmentPlan)
        db.session.add(plan)
        db.session.commit()
        return redirect(url_for("development_plan.plan", reference=plan.reference))

    return render_template("plan/new.html", form=form)


@development_plan.route("/<string:reference>/timetable/add", methods=["GET", "POST"])
def add_event(reference):
    plan = DevelopmentPlan.query.get(reference)

    form = EventForm()
    form.organisations.choices = _get_organisation_choices()

    if form.validate_on_submit():
        # model might need changing - this might be better modelled as plan has
        # one timetable which has many events.
        timetable = DevelopmentPlanTimetable()
        ref = f"{plan.reference}-{form.development_plan_event.data.lower().replace(' ', '-')}"
        timetable.reference = ref
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


@development_plan.route("/<string:reference>/document/add")
def add_document(reference):
    development_plan = DevelopmentPlan.query.get(reference)

    form = DocumentForm()
    if form.validate_on_submit():
        # handle form
        pass

    return render_template(
        "plan/add-document.html", development_plan=development_plan, form=form
    )


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
