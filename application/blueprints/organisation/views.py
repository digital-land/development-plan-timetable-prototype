from flask import Blueprint, redirect, render_template, request, url_for

from application.models import Organisation
from application.utils import (
    get_adopted_plans,
    get_organisations_expected_to_publish_plan,
)

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
    all_orgs = get_organisations_expected_to_publish_plan()
    adopted_plans, orgs_with_adopted_plan = get_adopted_plans()

    orgs = all_orgs
    if request.args.get("planningAuthorityFilter"):
        if request.args.get("planningAuthorityFilter") == "with":
            orgs = orgs_with_adopted_plan
        elif request.args.get("planningAuthorityFilter") == "without":
            org_ids_to_remove = {org.organisation for org in orgs_with_adopted_plan}
            orgs = [
                org for org in all_orgs if org.organisation not in org_ids_to_remove
            ]

    return render_template(
        "organisation/index.html",
        organisations=orgs,
        adopted_plans=adopted_plans,
        orgs_with_adopted_plan=orgs_with_adopted_plan,
        planning_authority_filter=request.args.get("planningAuthorityFilter"),
    )


@organisation_bp.route("/<string:reference>")
def organisation(reference):
    organisation = Organisation.query.get(reference)
    return render_template("organisation/organisation.html", organisation=organisation)
