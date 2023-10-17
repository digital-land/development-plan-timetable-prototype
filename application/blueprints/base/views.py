from flask import Blueprint, current_app, render_template

from application.models import DevelopmentPlan
from application.utils import (
    adopted_local_plan_count,
    adopted_plan_count,
    get_adopted_local_plans,
    get_adopted_plans,
    get_organisations_expected_to_publish_plan,
    local_plan_count,
    plan_count,
    plans_with_geography_count,
)

base = Blueprint("base", __name__)


@base.route("/")
def index():
    limit = current_app.config["MAX_DEVELOPMENT_PLANS"]
    development_plans = DevelopmentPlan.query.limit(limit).all()
    adopted_plans, orgs_with_adopted_plan = get_adopted_plans()
    organisations = get_organisations_expected_to_publish_plan()
    return render_template(
        "index.html",
        development_plans=development_plans,
        organisations=organisations,
        adopted_plans=adopted_plans,
        orgs_with_adopted_plan=orgs_with_adopted_plan,
    )


@base.route("/stats")
def stats():
    adopted_local_plans = get_adopted_local_plans()
    return render_template(
        "stats.html",
        plan_count=plan_count(),
        adopted_plan_count=adopted_plan_count(),
        local_plan_count=local_plan_count(),
        adopted_local_plan_count=adopted_local_plan_count(),
        organisation_count=len(get_organisations_expected_to_publish_plan()),
        orgs_with_adopted_lp_count=len(
            [
                organisation
                for plan in adopted_local_plans
                for organisation in plan.organisations
            ]
        ),
        plans_with_geography_count=plans_with_geography_count(),
    )
