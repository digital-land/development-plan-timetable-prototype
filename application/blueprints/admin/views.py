from flask import Blueprint, jsonify, render_template, request

from application.blueprints.admin.forms import DocumentTypeForm, EventForm, PlanTypeForm
from application.extensions import db
from application.models import DevelopmentPlanEvent, DevelopmentPlanType, DocumentType
from application.utils import kebab_case

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
def index():
    return render_template("admin/index.html")


@admin_bp.route("/events")
def events():
    evts = DevelopmentPlanEvent.query.all()
    return render_template("admin/events.html", events=evts)


@admin_bp.route("/events/add")
def add_event():
    form = EventForm()

    if form.validate_on_submit():
        pass

    return render_template("admin/add-record.html", register_name="event", form=form)


@admin_bp.route("/events/add-ajax", methods=["POST"])
def ajax_add_event():
    data = request.json
    # create reference if not provided
    if "reference" not in data.keys() or data["reference"] is None:
        data["reference"] = kebab_case(data["name"])

    if "description" not in data.keys() or data["description"] is None:
        data["description"] = ""

    evt = DevelopmentPlanEvent(
        name=data["name"], reference=data["reference"], notes=data["description"]
    )

    db.session.add(evt)
    db.session.commit()
    result = {"status": "success", "record": evt.to_dict()}
    return jsonify(result)


@admin_bp.route("/document-types")
def document_types():
    document_types = DocumentType.query.all()
    return render_template("admin/document-types.html", document_types=document_types)


@admin_bp.route("/document-types/add")
def add_document_type():
    form = DocumentTypeForm()

    if form.validate_on_submit():
        pass

    return render_template(
        "admin/add-record.html", register_name="document_type", form=form
    )


@admin_bp.route("/plan-types")
def plan_types():
    plan_types = DevelopmentPlanType.query.all()
    return render_template("admin/plan-types.html", plan_types=plan_types)


@admin_bp.route("/plan-types/add")
def add_plan_type():
    form = PlanTypeForm()

    if form.validate_on_submit():
        pass

    return render_template(
        "admin/add-record.html", register_name="plan_type", form=form
    )