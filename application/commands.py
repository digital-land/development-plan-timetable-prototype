import csv
import logging
from pathlib import Path
import sys
from flask.cli import AppGroup

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

data_cli = AppGroup("data")


@data_cli.command("load")
def load_data():
    from application.extensions import db

    for table in db.metadata.sorted_tables:
        logger.info(f"loading data for table: {table.name}")
        data_file_name = f"{table.name.replace('_', '-')}.csv"
        data_file_path = f"{Path(__file__).parent.parent}/data/{data_file_name}"
        try:
            with open(data_file_path) as data:
                reader = csv.DictReader(data)
                for row in reader:
                    copy = _get_insert_copy(row)
                    insert = table.insert().values(**copy)
                    db.session.execute(insert)
            db.session.commit()
        except Exception as e:
            logger.info(f"error loading data for table: {table.name}")
            logger.error(e)


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


def _get_insert_copy(row):
    copy = {}
    for key, value in row.items():
        k = key.replace("-", "_")
        if value:
            copy[k] = value
        else:
            copy[k] = None
    return copy
