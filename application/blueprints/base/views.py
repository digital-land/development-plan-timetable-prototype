from flask import Blueprint, current_app, render_template

from application.models import DevelopmentPlan
from application.utils import (
    get_adopted_plans,
    get_organisations_expected_to_publish_plan,
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
