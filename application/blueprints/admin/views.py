from flask import Blueprint, render_template

from application.models import DevelopmentPlanEvent, DevelopmentPlanType, DocumentType

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
def index():
    return render_template("admin/index.html")


@admin_bp.route("/events")
def events():
    evts = DevelopmentPlanEvent.query.all()
    return render_template("admin/events.html", events=evts)


@admin_bp.route("/document-types")
def document_types():
    document_types = DocumentType.query.all()
    return render_template("admin/document-types.html", document_types=document_types)


@admin_bp.route("/plan-types")
def plan_types():
    plan_types = DevelopmentPlanType.query.all()
    return render_template("admin/plan-types.html", plan_types=plan_types)
