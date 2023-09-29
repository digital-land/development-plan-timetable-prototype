from flask import Blueprint, current_app, render_template

from application.models import DevelopmentPlan

base = Blueprint("base", __name__)


@base.route("/")
def index():
    limit = current_app.config["MAX_DEVELOPMENT_PLANS"]
    development_plans = DevelopmentPlan.query.limit(limit).all()
    return render_template("index.html", development_plans=development_plans)
