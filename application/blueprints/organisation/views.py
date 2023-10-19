from flask import Blueprint, redirect, render_template, request, url_for

from application.models import Organisation
from application.utils import (
    get_adopted_local_plans,
    get_organisations_expected_to_publish_plan,
    split_orgs_by_adopted_locl_plan,
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

    all_orgs = get_organisations_expected_to_publish_plan()
    adopted_local_plans = get_adopted_local_plans()
    with_adopted_lp, without_adopted_lp = split_orgs_by_adopted_locl_plan(
        adopted_local_plans, all_orgs
    )

    orgs = all_orgs
    if request.args.get("planningAuthorityFilter"):
        if request.args.get("planningAuthorityFilter") == "with":
            orgs = with_adopted_lp
        elif request.args.get("planningAuthorityFilter") == "without":
            org_ids_to_remove = {org.organisation for org in with_adopted_lp}
            orgs = [
                org for org in all_orgs if org.organisation not in org_ids_to_remove
            ]

    return render_template(
        "organisation/index.html",
        organisations_expected_to_publish=all_orgs,
        organisations=orgs,
        adopted_plans=adopted_local_plans,
        orgs_with_adopted_plan=with_adopted_lp,
        planning_authority_filter=request.args.get("planningAuthorityFilter"),
    )


@organisation_bp.route("/<string:reference>")
def organisation(reference):
    organisation = Organisation.query.get(reference)
    plans = {}
    for plan in organisation.development_plans:
        plans.setdefault(plan.development_plan_type, []).append(plan)

    return render_template(
        "organisation/organisation.html", organisation=organisation, plans=plans
    )
