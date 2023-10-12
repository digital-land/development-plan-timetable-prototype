import codecs
import csv
import logging
import sys
from contextlib import closing
from pathlib import Path

import requests
from flask.cli import AppGroup

from application.models import (
    DevelopmentPlan,
    DevelopmentPlanDocument,
    DevelopmentPlanEvent,
    DevelopmentPlanEventType,
    DevelopmentPlanType,
    Organisation,
)

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


@data_cli.command("load")
def load_data():
    from application.extensions import db

    for table_name in ordered_tables:
        table = db.metadata.tables[table_name]
        logger.info(f"loading data for table: {table.name}")

        if table.name == "organisation":
            logger.info("organisation table is loaded from datasette")
            _load_orgs(db, table)
            continue
        elif table_name == "development_plan_event":
            data_file_name = (
                f"{table.name.replace('event', 'timetable').replace('_', '-')}.csv"
            )
            data_file_path = f"{Path(__file__).parent.parent}/data/{data_file_name}"
        else:
            data_file_name = f"{table.name.replace('_', '-')}.csv"
            data_file_path = f"{Path(__file__).parent.parent}/data/{data_file_name}"
        try:
            with open(data_file_path) as data:
                reader = csv.DictReader(data)
                for row in reader:
                    copy = _get_insert_copy(row, table.name)
                    if table.name in [
                        "development_plan",
                        "development_plan_document",
                        "development_plan_event",
                    ]:
                        orgs_str = copy.pop("organisations")
                        if orgs_str is not None:
                            orgs = orgs_str.split(";")
                        else:
                            orgs = []
                        if table.name == "development_plan":
                            obj = DevelopmentPlan(**copy)
                        elif table.name == "development_plan_document":
                            obj = DevelopmentPlanDocument(**copy)
                        else:
                            obj = DevelopmentPlanEvent(**copy)

                        db.session.add(obj)
                        db.session.commit()

                        for org in orgs:
                            organisation = Organisation.query.get(org)
                            if organisation is not None:
                                obj.organisations.append(organisation)
                                db.session.add(organisation)
                                db.session.commit()
                    else:
                        insert = table.insert().values(**copy)
                        db.session.execute(insert)
                        db.session.commit()
        except Exception as e:
            logger.info(f"error loading data for table: {table.name}")
            logger.error(e)
            db.session.rollback()


@data_cli.command("drop")
def drop_data():
    from application.extensions import db

    for table in reversed(db.metadata.sorted_tables):
        delete = table.delete()
        try:
            db.session.execute(delete)
            db.session.commit()
        except Exception as e:
            logger.error(e)


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


@data_cli.command("migrate-event-types")
def migrate_event_types():
    from application.extensions import db

    url = "https://dluhc-datasets.planning-data.dev/dataset/development-plan-event.csv"

    references = set([])

    with closing(requests.get(url, stream=True)) as r:
        reader = csv.DictReader(
            codecs.iterdecode(r.iter_lines(), encoding="utf-8"), delimiter=","
        )

        for row in reader:
            reference = row["reference"]
            event_type = DevelopmentPlanEventType.query.get(reference)
            if event_type is None:
                print("adding event type", reference, row["name"])
                event_type = DevelopmentPlanEventType(
                    reference=reference,
                    name=row["name"],
                    notes=row["notes"],
                )
            else:
                event_type.name = row["name"]
                event_type.notes = row["notes"]

            db.session.add(event_type)
            db.session.commit()
            references.add(reference)


@data_cli.command("remove-old-event-types")
def remove_old_event_types():
    from application.extensions import db

    url = "https://dluhc-datasets.planning-data.dev/dataset/development-plan-event.csv"

    references = set([])

    with closing(requests.get(url, stream=True)) as r:
        reader = csv.DictReader(
            codecs.iterdecode(r.iter_lines(), encoding="utf-8"), delimiter=","
        )
        for row in reader:
            references.add(row["reference"])

    event_types = DevelopmentPlanEventType.query.all()
    for event_type in event_types:
        if event_type.reference not in references:
            print("deleting event type", event_type.reference)
            db.session.delete(event_type)
            db.session.commit()


@data_cli.command("migrate-plan-types")
def migrate_plan_types():
    from application.extensions import db

    url = "https://dluhc-datasets.planning-data.dev/dataset/development-plan-type.csv"

    with closing(requests.get(url, stream=True)) as r:
        reader = csv.DictReader(
            codecs.iterdecode(r.iter_lines(), encoding="utf-8"), delimiter=","
        )

        for row in reader:
            reference = row["reference"]
            plan_type = DevelopmentPlanType.query.get(reference)
            if plan_type is None:
                print("adding plan type", reference, row["name"])
                plan_type = DevelopmentPlanType(reference=reference, name=row["name"])

            db.session.add(plan_type)
            db.session.commit()


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
