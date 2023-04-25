from flask import Blueprint, render_template

from application.models import DevelopmentPlan

base = Blueprint("base", __name__)


@base.route("/")
def index():
    development_plans = DevelopmentPlan.query.limit(8)
    return render_template("index.html", development_plans=development_plans)
