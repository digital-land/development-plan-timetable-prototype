from flask import Blueprint, redirect, render_template, url_for

from application.blueprints.development_plan.forms import (
    DocumentForm,
    EventForm,
    PlanForm,
)
from application.extensions import db
from application.models import DevelopmentPlan, DevelopmentPlanType, Organisation

development_plan = Blueprint(
    "development_plan", __name__, url_prefix="/development-plan"
)


@development_plan.route("/<string:reference>")
def plan(reference):
    development_plan = DevelopmentPlan.query.get(reference)
    return render_template("plan/plan.html", development_plan=development_plan)


@development_plan.route("/<string:reference>/edit")
def edit(reference):
    development_plan = DevelopmentPlan.query.get(reference)

    form = PlanForm()
    if form.validate_on_submit():
        # handle form
        pass

    return render_template(
        "plan/edit.html", development_plan=development_plan, form=form
    )


@development_plan.route("/add", methods=["GET", "POST"])
def new():
    # check if creating record for a given LPA
    # requests.get...

    form = PlanForm()
    form.organisations.choices = [
        (org.organisation, org.name) for org in Organisation.query.all()
    ]
    form.development_plan_type.choices = [
        (plan_type.reference, plan_type.name)
        for plan_type in DevelopmentPlanType.query.all()
    ]
    if form.validate_on_submit():
        plan = DevelopmentPlan()
        plan.reference = form.reference.data
        plan.name = form.name.data
        plan.development_plan_type = form.development_plan_type.data
        # plan.notes = form.notes.data
        plan.description = form.description.data
        plan.documentation_url = form.documentation_url.data
        plan.period_start_date = form.period_start_date.data
        plan.period_end_date = form.period_end_date.data

        for org in form.organisations.data:
            organisation = Organisation.query.get(org)
            plan.organisations.append(organisation)

        db.session.add(plan)
        db.session.commit()
        return redirect(url_for("development_plan.plan", reference=plan.reference))

    return render_template("plan/new.html", form=form)


@development_plan.route("/<string:reference>/timetable/add")
def add_event(reference):
    development_plan = DevelopmentPlan.query.get(reference)

    form = EventForm()
    if form.validate_on_submit():
        # handle form
        pass

    return render_template(
        "plan/add-event.html", development_plan=development_plan, form=form
    )


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
