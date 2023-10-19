import random

from flask import Blueprint, current_app, redirect, render_template, request, url_for
from sqlalchemy import not_

from application.models import DevelopmentPlan
from application.utils import (
    adopted_local_plan_count,
    adopted_plan_count,
    get_adopted_local_plans,
    get_adopted_plans,
    get_organisations_expected_to_publish_plan,
    get_plans_query,
    local_plan_count,
    plan_count,
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
        plans_with_geography_count=get_plans_query(
            DevelopmentPlan.geography.has(), count=True
        ),
    )


@base.route("/roulette")
def roulette():
    adopted_local_plans = get_adopted_local_plans()
    organisations = get_organisations_expected_to_publish_plan()
    orgs_with_adopted_lp = [
        organisation
        for plan in adopted_local_plans
        for organisation in plan.organisations
    ]
    orgs_without_adopted_lp = _exclude_orgs(organisations, orgs_with_adopted_lp)

    if "random" in request.args:
        option = request.args.get("random")

        # for org with no adopted local plan
        if option == "organisation":
            random_org = random.choice(orgs_without_adopted_lp)
            return redirect(
                url_for("organisation.organisation", reference=random_org.organisation)
            )

        # for plans missing something
        condition = None
        if option == "missing-geography":
            condition = not_(DevelopmentPlan.geography.has())
        if option == "no-documents":
            condition = not_(DevelopmentPlan.documents.any())
        if option == "no-events":
            condition = not_(DevelopmentPlan.timetable.any())

        if condition is not None:
            filtered_plans = get_plans_query(condition)
            random_plan = random.choice(filtered_plans)
            return redirect(
                url_for("development_plan.plan", reference=random_plan.reference)
            )

    return render_template("roulette.html")


def _exclude_orgs(main_list, to_exclude):
    orgs_to_remove = [org.organisation for org in to_exclude]
    return [org for org in main_list if org.organisation not in orgs_to_remove]


def _exclude(main_list, to_exclude, attr_name="reference"):
    items_to_remove = [getattr(item, attr_name) for item in to_exclude]
    return [
        item for item in main_list if getattr(item, attr_name) not in items_to_remove
    ]
