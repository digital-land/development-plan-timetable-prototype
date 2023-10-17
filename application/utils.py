from sqlalchemy import Date, cast, null, or_

from application.models import DevelopmentPlan, Organisation


def kebab_case(s):
    # Convert the s to lowercase and replace any spaces or underscores with hyphens
    s = s.lower().replace(" ", "-").replace("_", "-")
    # Remove any consecutive hyphens
    while "--" in s:
        s = s.replace("--", "-")
    # Remove any leading or trailing hyphens
    s = s.strip("-")
    return s


def get_organisations_expected_to_publish_plan():
    # TODO: how do I get all orgs that should be publishing a plan?

    # this only returns current local-authorities
    orgs = (
        Organisation.query.filter(
            or_(
                Organisation.organisation.contains("local-authority"),
                Organisation.organisation.contains("national-park"),
                Organisation.organisation.contains("development-corporation"),
            )
        )
        .filter(
            or_(
                Organisation.end_date.is_(None),
                cast(Organisation.end_date, Date) == null(),
            )
        )
        .order_by(Organisation.name.asc())
        .all()
    )
    return orgs


def get_adopted_plans(with_org_list=True):
    adopted_plans = DevelopmentPlan.query.filter(
        DevelopmentPlan.adopted_date.isnot(None)
    ).all()
    orgs_with_adopted_plan = [
        organisation for plan in adopted_plans for organisation in plan.organisations
    ]
    if with_org_list:
        return adopted_plans, orgs_with_adopted_plan
    return adopted_plans


def combine_feature_collections(feature_collections):
    combined_features = []

    for fc in feature_collections:
        combined_features.extend(fc["features"])

    combined_fc = {"type": "FeatureCollection", "features": combined_features}

    return combined_fc


def plan_count():
    return DevelopmentPlan.query.count()


def adopted_plan_count():
    return DevelopmentPlan.query.filter(
        DevelopmentPlan.adopted_date.isnot(None)
    ).count()


def local_plan_count():
    return DevelopmentPlan.query.filter(
        DevelopmentPlan.development_plan_type == "local-plan"
    ).count()


def adopted_local_plan_count():
    return (
        DevelopmentPlan.query.filter(
            DevelopmentPlan.development_plan_type == "local-plan"
        )
        .filter(DevelopmentPlan.adopted_date.isnot(None))
        .count()
    )


def get_adopted_local_plans():
    return (
        DevelopmentPlan.query.filter(
            DevelopmentPlan.development_plan_type == "local-plan"
        )
        .filter(DevelopmentPlan.adopted_date.isnot(None))
        .all()
    )


def get_plans_with_geography(count=False):
    query = DevelopmentPlan.query.filter(DevelopmentPlan.geography.has())
    if count:
        return query.count()
    return query.all()
