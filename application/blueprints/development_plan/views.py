from flask import Blueprint, render_template

from application.blueprints.development_plan.forms import PlanForm
from application.models import DevelopmentPlan

development_plan = Blueprint(
    "development_plan", __name__, url_prefix="/development-plan"
)


@development_plan.route("/<string:reference>")
def plan(reference):
    development_plan = DevelopmentPlan.query.get(reference)
    return render_template("plan.html", development_plan=development_plan)


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


@development_plan.route("/add")
def new():
    # check if creating record for a given LPA
    # requests.get...

    form = PlanForm()
    if form.validate_on_submit():
        # handle form
        pass

    return render_template("plan/new.html", form=form)
