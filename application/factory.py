# -*- coding: utf-8 -*-

from flask import Flask
from flask.cli import load_dotenv

from application.models import *  # noqa

load_dotenv()


def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 10

    register_blueprints(app)
    register_context_processors(app)
    register_templates(app)
    register_filters(app)
    register_globals(app)
    register_extensions(app)
    register_commands(app)

    return app


def register_blueprints(app):
    from application.blueprints.admin.views import admin_bp
    from application.blueprints.auth.views import auth
    from application.blueprints.base.views import base
    from application.blueprints.development_plan.views import development_plan
    from application.blueprints.organisation.views import organisation_bp

    app.register_blueprint(base)
    app.register_blueprint(development_plan)
    app.register_blueprint(organisation_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth)


def register_context_processors(app):
    """
    Add template context variables and functions
    """

    def base_context_processor():
        return {"assetPath": "/static"}

    app.context_processor(base_context_processor)


def register_filters(app):
    from application.filters import get_date_part

    app.add_template_filter(get_date_part, name="date_part")

    from digital_land_frontend.filters import is_list_filter

    app.add_template_filter(is_list_filter, name="is_list")


def register_globals(app):
    from digital_land_frontend.globals import random_int

    app.jinja_env.globals.update(random_int=random_int)


def register_extensions(app):
    from application.extensions import db, migrate, oauth

    db.init_app(app)
    migrate.init_app(app)

    from flask_sslify import SSLify

    sslify = SSLify(app)  # noqa

    oauth.init_app(app)
    oauth.register(
        "auth0",
        client_id=app.config.get("AUTH0_CLIENT_ID"),
        client_secret=app.config.get("AUTH0_CLIENT_SECRET"),
        client_kwargs={
            "scope": "openid profile email",
        },
        server_metadata_url=f'https://{app.config.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
    )


def register_templates(app):
    """
    Register templates from packages
    """
    from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader

    multi_loader = ChoiceLoader(
        [
            app.jinja_loader,
            PrefixLoader(
                {
                    "govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja"),
                    "digital-land-frontend": PackageLoader("digital_land_frontend"),
                }
            ),
        ]
    )
    app.jinja_loader = multi_loader


def register_commands(app):
    from application.commands import data_cli

    app.cli.add_command(data_cli)
