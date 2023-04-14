from flask import Blueprint, render_template

from application.models import DevelopmentPlan

development_plan = Blueprint(
    "development_plan", __name__, url_prefix="/development-plan"
)


@development_plan.route("/<string:reference>")
def plan(reference):
    development_plan = DevelopmentPlan.query.get(reference)
    return render_template("plan.html", development_plan=development_plan)
