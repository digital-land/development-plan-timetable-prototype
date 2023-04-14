import csv
import logging
import sys
from pathlib import Path

import requests
from flask.cli import AppGroup

from application.models import (
    DevelopmentPlan,
    DevelopmentPlanDocument,
    DevelopmentPlanTimetable,
    Organisation,
)

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

data_cli = AppGroup("data")

ordered_tables = [
    "organisation",
    "development_plan_event",
    "development_plan_type",
    "document_type",
    "development_plan",
    "development_plan_document",
    "development_plan_timetable",
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
                            "development_plan_timetable",
                        ]:
                            orgs = copy.pop("organisation_id", "").split(";")
                            if table.name == "development_plan":
                                obj = DevelopmentPlan(**copy)
                            elif table.name == "development_plan_document":
                                obj = DevelopmentPlanDocument(**copy)
                            else:
                                obj = DevelopmentPlanTimetable(**copy)

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
            table_name in ["development_plan_timetable", "development_plan_document"]
            and k == "development_plan"
        ):
            k = "development_plan_reference"
        if k == "organisation" and table_name != "organisation":
            k = "organisation_id"
        if value:
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
