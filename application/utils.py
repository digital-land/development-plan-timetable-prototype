from sqlalchemy import Date, cast, null, or_

from application.models import Organisation


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
        Organisation.query.filter(Organisation.organisation.contains("local-authority"))
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
