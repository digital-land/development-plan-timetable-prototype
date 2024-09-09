import logging
import os
import sys

import requests
from flask.cli import AppGroup

from application.models import Organisation

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

data_cli = AppGroup("data")

ordered_tables = [
    "organisation",
    "development_plan_event_type",
    "development_plan_type",
    "document_type",
    "development_plan",
    "development_plan_document",
    "development_plan_event",
]


@data_cli.command("load-data")
def load_data():
    import subprocess
    import sys
    import tempfile

    from flask import current_app

    # check heroku cli installed
    result = subprocess.run(["which", "heroku"], capture_output=True, text=True)

    if result.returncode == 1:
        logger.error("Heroku CLI is not installed. Please install it and try again.")
        sys.exit(1)

    # check heroku login
    result = subprocess.run(["heroku", "whoami"], capture_output=True, text=True)

    if "Error: not logged in" in result.stderr:
        logger.error("Please login to heroku using 'heroku login' and try again.")
        sys.exit(1)

    logger.info(
        f"Starting load data into {current_app.config['SQLALCHEMY_DATABASE_URI']}"
    )
    if (
        input(
            "Completing process will overwrite your local database. Enter 'y' to continue, or anything else to exit. "
        )
        != "y"
    ):
        logger.info("Exiting without making any changes")
        sys.exit(0)

    with tempfile.TemporaryDirectory() as tempdir:
        path = os.path.join(tempdir, "latest.dump")

        # get the latest dump from heroku
        result = subprocess.run(
            [
                "heroku",
                "pg:backups:download",
                "-a",
                "development-plan-prototype",
                "-o",
                path,
            ]
        )

        if result.returncode != 0:
            logger.error("Error downloading the backup")
            sys.exit(1)

        # restore the dump to the local database
        subprocess.run(
            [
                "pg_restore",
                "--verbose",
                "--clean",
                "--no-acl",
                "--no-owner",
                "-h",
                "localhost",
                "-d",
                "development_plan_timetable",
                path,
            ]
        )
        logger.info(
            "\n\nRestored the dump to the local database using pg_restore. You can ignore warnings from pg_restore."
        )

    logger.info("Data loaded successfully")


def _get_insert_copy(row, table_name):
    copy = {}
    for key, value in row.items():
        k = key.replace("-", "_")
        if (
            table_name in ["development_plan_event", "development_plan_document"]
            and k == "development_plan"
        ):
            k = "development_plan_reference"
        if k == "organisation" and table_name != "organisation":
            k = "organisation_id"
        if value:
            if "reference" in k:
                value = value.lower()
            copy[k] = value
        else:
            copy[k] = None
    return copy


def _load_orgs(db, table):
    url = "https://datasette.planning.data.gov.uk/digital-land/organisation.json?_shape=array"

    orgs = []
    while url:
        resp = requests.get(url)
        try:
            url = resp.links.get("next").get("url")
        except AttributeError:
            url = None

        orgs.extend(resp.json())

    for org in orgs:
        try:
            insert = table.insert().values(_get_insert_copy(org, table.name))
            db.session.execute(insert)
            db.session.commit()
        except Exception as e:
            logger.exception(e)
            logger.exception(f"error loading {table} with data {org}")
            db.session.rollback()


# @data_cli.command("migrate-event-types")
# def migrate_event_types():
#     from application.extensions import db

#     url = "https://dluhc-datasets.planning-data.dev/dataset/development-plan-event.csv"

#     references = set([])

#     with closing(requests.get(url, stream=True)) as r:
#         reader = csv.DictReader(
#             codecs.iterdecode(r.iter_lines(), encoding="utf-8"), delimiter=","
#         )

#         for row in reader:
#             reference = row["reference"]
#             event_type = DevelopmentPlanTimetable.query.get(reference)
#             if event_type is None:
#                 print("adding event type", reference, row["name"])
#                 event_type = DevelopmentPlanTimetable(
#                     reference=reference,
#                     name=row["name"],
#                     notes=row["notes"],
#                 )
#             else:
#                 event_type.name = row["name"]
#                 event_type.notes = row["notes"]

#             db.session.add(event_type)
#             db.session.commit()
#             references.add(reference)


# @data_cli.command("remove-old-event-types")
# def remove_old_event_types():
#     from application.extensions import db

#     url = "https://dluhc-datasets.planning-data.dev/dataset/development-plan-event.csv"

#     references = set([])

#     with closing(requests.get(url, stream=True)) as r:
#         reader = csv.DictReader(
#             codecs.iterdecode(r.iter_lines(), encoding="utf-8"), delimiter=","
#         )
#         for row in reader:
#             references.add(row["reference"])

#     event_types = DevelopmentPlanTimetable.query.all()
#     for event_type in event_types:
#         if event_type.reference not in references:
#             print("deleting event type", event_type.reference)
#             db.session.delete(event_type)
#             db.session.commit()


# @data_cli.command("migrate-plan-types")
# def migrate_plan_types():
#     from application.extensions import db

#     url = "https://dluhc-datasets.planning-data.dev/dataset/development-plan-type.csv"

#     with closing(requests.get(url, stream=True)) as r:
#         reader = csv.DictReader(
#             codecs.iterdecode(r.iter_lines(), encoding="utf-8"), delimiter=","
#         )

#         for row in reader:
#             reference = row["reference"]
#             plan_type = DevelopmentPlanType.query.get(reference)
#             if plan_type is None:
#                 print("adding plan type", reference, row["name"])
#                 plan_type = DevelopmentPlanType(reference=reference, name=row["name"])

#             db.session.add(plan_type)
#             db.session.commit()


@data_cli.command("get-geographies")
def get_geometries():
    from application.extensions import db

    orgs = Organisation.query.all()
    for org in orgs:
        curie = f"statistical-geography:{org.statistical_geography}"
        g = _get_geography(curie)
        if g is not None:
            org.geometry = g["geometry"]
            org.geojson = g["geojson"]
            org.point = g["point"]
            db.session.add(org)
            db.session.commit()


def _get_geography(reference):
    from flask import current_app
    from shapely import wkt

    url = f"{current_app.config['PLANNING_DATA_API_URL']}/entity.json"
    params = {"curie": reference}
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        data = resp.json()
        if len(data["entities"]) == 0:
            return None
        prefix = data["entities"][0].get("prefix")
        reference = data["entities"][0].get("reference")
        point = data["entities"][0].get("point")
        point_obj = wkt.loads(point)
        geojson_url = f"{current_app.config['PLANNING_DATA_API_URL']}/entity.geojson"
        resp = requests.get(geojson_url, params=params)
        if resp.status_code == 200:
            geography = {
                "geojson": resp.json(),
                "geometry": data["entities"][0].get("geometry"),
                "prefix": prefix,
                "reference": reference,
                "point": point,
                "lat": point_obj.y,
                "long": point_obj.x,
            }
        return geography
    return None
