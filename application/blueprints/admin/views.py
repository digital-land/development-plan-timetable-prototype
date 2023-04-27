from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from application.blueprints.admin.forms import DocumentTypeForm, EventForm, PlanTypeForm
from application.extensions import db
from application.models import (
    DevelopmentPlanEventType,
    DevelopmentPlanType,
    DocumentType,
)
from application.utils import kebab_case

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
def index():
    return render_template("admin/index.html")


@admin_bp.route("/events")
def events():
    evts = DevelopmentPlanEventType.query.all()
    return render_template("admin/events.html", events=evts)


@admin_bp.route("/events/add", methods=["GET", "POST"])
def add_event():
    form = EventForm()

    if form.validate_on_submit():
        name = form.name.data
        reference = name.replace(" ", "-").lower()
        if DevelopmentPlanEventType.query.get(reference) is not None:
            flash(
                f"Event type {name} with reference: {reference} already exists", "error"
            )
            return render_template(
                "admin/add-record.html", register_name="event", form=form
            )
        event = DevelopmentPlanEventType()
        event.reference = reference
        event.name = name
        event.description = form.description.data
        return redirect(url_for("admin.events"))

    return render_template("admin/add-record.html", register_name="event", form=form)


@admin_bp.route("/events/add-ajax", methods=["POST"])
def ajax_add_event():
    data = request.json
    # create reference if not provided
    if "reference" not in data.keys() or data["reference"] is None:
        data["reference"] = kebab_case(data["name"])

    if "description" not in data.keys() or data["description"] is None:
        data["description"] = ""

    evt = DevelopmentPlanEventType(
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


@admin_bp.route("/document-types/add", methods=["GET", "POST"])
def add_document_type():
    form = DocumentTypeForm()

    if form.validate_on_submit():
        name = form.name.data
        reference = name.replace(" ", "-").lower()
        if DocumentType.query.get(reference) is not None:
            flash(f"Document type {name} {reference} already exists", "error")
            return render_template(
                "admin/add-record.html", register_name="document_type", form=form
            )
        document_type = DocumentType()
        document_type.reference = reference
        document_type.name = form.name.data
        document_type.description = form.description.data

        db.session.add(document_type)
        db.session.commit()
        return redirect(url_for("admin.document_types"))

    return render_template(
        "admin/add-record.html", register_name="document_type", form=form
    )


@admin_bp.route("/plan-types")
def plan_types():
    plan_types = DevelopmentPlanType.query.all()
    return render_template("admin/plan-types.html", plan_types=plan_types)


@admin_bp.route("/plan-types/add", methods=["GET", "POST"])
def add_plan_type():
    form = PlanTypeForm()

    if form.validate_on_submit():
        name = form.name.data
        reference = name.replace(" ", "-").lower()
        if DevelopmentPlanType.query.get(reference) is not None:
            flash(
                f"Plan type {name} with reference: {reference} already exists", "error"
            )
            return render_template(
                "admin/add-record.html", register_name="plan_type", form=form
            )
        plan_type = DevelopmentPlanType()
        plan_type.reference = reference
        plan_type.name = name
        plan_type.description = form.description.data
        db.session.add(plan_type)
        db.session.commit()
        return redirect(url_for("admin.plan_types"))

    return render_template(
        "admin/add-record.html", register_name="plan_type", form=form
    )
