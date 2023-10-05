from flask import Blueprint, redirect, render_template, request, url_for

from application.models import DevelopmentPlan, Organisation
from application.utils import get_organisations_expected_to_publish_plan

organisation_bp = Blueprint("organisation", __name__, url_prefix="/organisation")


@organisation_bp.route("/")
def organisations():
    if "organisation" in request.args:
        lpa = request.args.get("organisation")
        print(lpa)
        return redirect(
            url_for("organisation.organisation", reference=f"local-authority-eng:{lpa}")
        )

    # TODO: how do I get all orgs that should be publishing a plan?
    orgs = get_organisations_expected_to_publish_plan()
    adopted_plans = DevelopmentPlan.query.filter(
        DevelopmentPlan.adopted_date.isnot(None)
    ).all()
    return render_template(
        "organisation/index.html", organisations=orgs, adopted_plans=adopted_plans
    )


@organisation_bp.route("/<string:reference>")
def organisation(reference):
    organisation = Organisation.query.get(reference)
    return render_template("organisation/organisation.html", organisation=organisation)
