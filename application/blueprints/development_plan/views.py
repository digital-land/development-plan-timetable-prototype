import csv
import glob
import io
import json
import os
import shutil
import time
import zipfile
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import geopandas
from flask import (
    Blueprint,
    Response,
    abort,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.utils import secure_filename

from application.blueprints.development_plan.forms import (
    DocumentForm,
    EventForm,
    PlanForm,
)
from application.extensions import db
from application.models import (
    DevelopmentPlan,
    DevelopmentPlanDocument,
    DevelopmentPlanEvent,
    DevelopmentPlanEventType,
    DevelopmentPlanGeography,
    DevelopmentPlanType,
    DocumentType,
    Organisation,
)

development_plan = Blueprint(
    "development_plan", __name__, url_prefix="/development-plan"
)


@development_plan.route("/<string:reference>")
def plan(reference):
    development_plan = DevelopmentPlan.query.get(reference)
    return render_template("plan/plan.html", development_plan=development_plan)


@development_plan.route("/<string:reference>/edit", methods=["GET", "POST"])
def edit(reference):
    plan = DevelopmentPlan.query.get(reference)

    organisation__string = ";".join([org.organisation for org in plan.organisations])
    del plan.organisations

    form = PlanForm(obj=plan)

    if not form.organisations.data:
        form.organisations.data = organisation__string

    form.organisations.choices = _get_organisation_choices()
    form.development_plan_type.choices = _get_plan_type_choices()

    if form.validate_on_submit():
        plan = _populate_plan(form, plan)
        db.session.add(plan)
        db.session.commit()
        return redirect(url_for("development_plan.plan", reference=plan.reference))

    return render_template("plan/edit.html", development_plan=plan, form=form)


@development_plan.route("/add", methods=["GET", "POST"])
def new():
    # check if creating record for a given LPA
    # requests.get...

    form = PlanForm()
    form.organisations.choices = [(" ", " ")] + _get_organisation_choices()
    form.development_plan_type.choices = _get_plan_type_choices()

    if request.method == "GET" and request.args.get("organisation"):
        org = Organisation.query.get(request.args.get("organisation"))
        form.organisations.data = org.organisation

    if form.validate_on_submit():
        plan = _populate_plan(form, DevelopmentPlan())
        plan.reference = form.name.data.lower().replace(" ", "-")
        if DevelopmentPlan.query.get(plan.reference) is not None:
            plan.reference = (
                f"{plan.reference}-{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}"
            )
        plan.adopted_date = f"{form.adopted_date_year.data}-{form.adopted_date_month.data}-{form.adopted_date_day.data}"
        db.session.add(plan)
        db.session.commit()
        return redirect(
            url_for("development_plan.add_geography", reference=plan.reference)
        )

    return render_template("plan/new.html", form=form)


@development_plan.route("/<string:reference>/geography/add", methods=["GET", "POST"])
def add_geography(reference):
    plan = DevelopmentPlan.query.get(reference)

    if request.method == "POST":
        geography_provided = request.form.get("geography-provided")
        if geography_provided == "yes":
            for org in plan.organisations:
                g = (
                    DevelopmentPlanGeography.query.filter()
                    .filter_by(prefix=org.prefix, reference=org.statistical_geography)
                    .one_or_none()
                )
                if g is None:
                    g = DevelopmentPlanGeography(
                        prefix=org.prefix,
                        reference=org.statistical_geography,
                        geojson=org.geojson,
                        geometry=org.geometry,
                        point=org.point,
                    )
                    plan.geographies.append(g)
            db.session.add(plan)
            db.session.commit()
            return redirect(url_for("development_plan.plan", reference=plan.reference))
        else:
            if "fileUpload" in request.files:
                file = request.files["fileUpload"]
                reference = (
                    request.form["designated-plan-area"].replace(" ", "-").lower()
                )
                if file and allowed_file(file.filename):
                    with TemporaryDirectory() as tempdir:
                        filename = secure_filename(file.filename)
                        shapefile_path = os.path.join(tempdir, filename)
                        file.save(shapefile_path)
                        gdf = geopandas.read_file(shapefile_path)
                        geojson = gdf.to_crs(epsg="4326").to_json()
                        g = DevelopmentPlanGeography(
                            prefix="designated‑plan‑area",
                            reference=reference,
                            geojson=json.loads(geojson),
                        )
                        plan.geographies.append(g)
                        db.session.add(plan)
                        db.session.commit()

                return redirect(
                    url_for("development_plan.plan", reference=plan.reference)
                )

    geographies = {}
    for org in plan.organisations:
        if org.geometry is not None:
            geographies[org.organisation] = org
        else:
            geographies[org.organisation] = None

    return render_template(
        "plan/choose-geography.html", development_plan=plan, geographies=geographies
    )


@development_plan.route("/<string:reference>/timetable/add", methods=["GET", "POST"])
def add_event(reference):
    plan = DevelopmentPlan.query.get(reference)

    form = EventForm()
    form.organisations.choices = [(" ", " ")] + _get_organisation_choices()
    form.development_plan_event.choices = _get_event_choices()

    if form.validate_on_submit():
        event = DevelopmentPlanEvent()
        ref = f"{plan.reference}-{form.development_plan_event.data.lower().replace(' ', '-')}"

        t = DevelopmentPlanEvent.query.get(ref)
        if t is not None:
            ref = f"{ref}-{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}"
        event.reference = ref
        event.event_date = f"{form.event_date_year.data}-{form.event_date_month.data}-{form.event_date_day.data}"
        organisation_str = form.organisations.data
        del form.organisations
        development_plan_event_ref = form.development_plan_event.data
        del form.development_plan_event
        event.development_plan_event_type_reference = development_plan_event_ref
        form.populate_obj(event)
        _set_organisations(event, organisation_str)

        plan.timetable.append(event)
        db.session.add(plan)
        db.session.commit()
        return redirect(url_for("development_plan.plan", reference=reference))

    return render_template("plan/add-event.html", development_plan=plan, form=form)


@development_plan.route(
    "/<string:reference>/timetable/<string:event_reference>/edit",
    methods=["GET", "POST"],
)
def edit_event(reference, event_reference):
    plan = DevelopmentPlan.query.get(reference)
    event = DevelopmentPlanEvent.query.filter(
        DevelopmentPlanEvent.development_plan_reference == reference,
        DevelopmentPlanEvent.reference == event_reference,
    ).one_or_none()
    event_type = DevelopmentPlanEvent.query.get(event.development_plan_event)

    if event is None:
        return abort(404)

    organisation__string = ";".join([org.organisation for org in event.organisations])
    del event.organisations

    form = EventForm(obj=event)

    # set to current orgs if no data provided in form
    if not form.organisations.data:
        form.organisations.data = organisation__string

    form.organisations.choices = _get_organisation_choices()
    form.development_plan_event.choices = _get_event_choices()

    if form.validate_on_submit():
        organisation_str = form.organisations.data
        del form.organisations
        event.event_date = f"{form.event_date_year.data}-{form.event_date_month.data}-{form.event_date_day.data}"
        _set_organisations(event, organisation_str)
        db.session.add(event)
        db.session.commit()
        return redirect(url_for("development_plan.plan", reference=reference))

    return render_template(
        "plan/edit-event.html",
        development_plan=plan,
        form=form,
        event=event,
        event_type=event_type,
    )


@development_plan.get("/<string:reference>/timetable/<string:event_reference>/delete")
def delete_event(reference, event_reference):
    event = DevelopmentPlanEvent.query.filter(
        DevelopmentPlanEvent.development_plan_reference == reference,
        DevelopmentPlanEvent.reference == event_reference,
    ).one_or_none()

    if event is None:
        return abort(404)
    event.end_date = datetime.today()
    db.session.add(event)
    db.session.commit()
    return redirect(url_for("development_plan.plan", reference=reference))


@development_plan.route("/<string:reference>/document/add", methods=["GET", "POST"])
def add_document(reference):
    plan = DevelopmentPlan.query.get(reference)

    form = DocumentForm()
    form.organisations.choices = [(" ", " ")] + _get_organisation_choices()
    form.document_type.choices = _get_document_type_choices()

    if form.validate_on_submit():
        ref = f"{form.name.data.lower().replace(' ', '-')}"
        document = DevelopmentPlanDocument.query.get(ref)
        if document is not None:
            ref = f"{ref}-{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}"
        else:
            document = DevelopmentPlanDocument()

        document.reference = ref

        organisations_str = form.organisations.data
        del form.organisations
        form.populate_obj(document)
        _set_organisations(document, organisations_str)

        plan.documents.append(document)
        db.session.add(plan)
        db.session.commit()
        return redirect(url_for("development_plan.plan", reference=reference))

    return render_template("plan/add-document.html", development_plan=plan, form=form)


@development_plan.get("/<string:reference>/document/<string:document_reference>/edit")
def edit_document(reference, document_reference):
    plan = DevelopmentPlan.query.get(reference)
    document = DevelopmentPlanDocument.query.get(document_reference)
    if document is None or plan is None:
        return abort(404)

    form = DocumentForm()
    form.organisations.choices = [(" ", " ")] + _get_organisation_choices()
    form.document_type.choices = _get_document_type_choices()

    # populate with existing values from document record
    form.name.data = document.name
    form.document_url.data = document.document_url
    form.documentation_url.data = document.documentation_url
    form.description.data = document.description
    form.document_type.data = document.document_type
    form.notes.data = document.notes
    selected_orgs = [org.organisation for org in document.organisations]
    form.organisations.data = ";".join(selected_orgs)

    if form.validate_on_submit():
        # handle form submit
        pass

    return render_template(
        "plan/add-document.html", development_plan=plan, form=form, document=document
    )


@development_plan.get("/<string:reference>/document/<string:document_reference>/delete")
def delete_document(reference, document_reference):
    document = DevelopmentPlanDocument.query.get(document_reference)
    if document is None:
        return abort(404)
    document.end_date = datetime.today()
    db.session.add(document)
    db.session.commit()
    return redirect(url_for("development_plan.plan", reference=reference))


@development_plan.route("/download", methods=["GET"])
def download():
    tempdir = _export_data()
    zipname = "development-plan-data.zip"
    files = glob.glob(f"{tempdir.name}/*.csv")
    file_handle = io.BytesIO()
    with zipfile.ZipFile(file_handle, "w") as zip:
        for file in files:
            p = Path(file)
            info = zipfile.ZipInfo(p.name)
            info.date_time = time.localtime(time.time())[:6]
            info.compress_type = zipfile.ZIP_DEFLATED
            with open(p, "rb") as fd:
                zip.writestr(info, fd.read())
    file_handle.seek(0)
    shutil.rmtree(tempdir.name)

    return Response(
        file_handle.getvalue(),
        mimetype="application/zip",
        headers={"Content-Disposition": f"attachment;filename={zipname}"},
    )


def _export_data():
    download_file_map = {
        "development-plan-type.csv": DevelopmentPlanType,
        "development-plan-event.csv": DevelopmentPlanEventType,
        "development-plan.csv": DevelopmentPlan,
        "development-plan-document.csv": DevelopmentPlanDocument,
        "development-plan-timetable.csv": DevelopmentPlanEvent,
        "document-type.csv": DocumentType,
    }

    tempdir = TemporaryDirectory()

    path = Path(tempdir.name)

    for file, model in download_file_map.items():
        csv_path = path / file
        with open(csv_path, "w") as f:
            fieldnames = [col.name.replace("_", "-") for col in model.__table__.columns]
            fieldnames = [f.replace("-reference", "") for f in fieldnames]
            if model in [
                DevelopmentPlan,
                DevelopmentPlanDocument,
                DevelopmentPlanEvent,
            ]:
                fieldnames.append("organisations")
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for d in model.query.all():
                writer.writerow(d.as_dict())
    return tempdir


def _populate_plan(form, plan):
    organisations = form.organisations.data
    del form.organisations

    period_start = form.period_start_date.data
    period_end = form.period_end_date.data

    if period_start:
        plan.period_start_date = int(period_start)
    else:
        plan.period_start_date = None

    if period_end:
        plan.period_end_date = int(period_end)
    else:
        plan.period_end_date = None

    del form.period_start_date
    del form.period_end_date

    plan.adopted_date = f"{form.adopted_date_year.data}-{form.adopted_date_month.data}-{form.adopted_date_day.data}"

    del form.adopted_date_year
    del form.adopted_date_month
    del form.adopted_date_day

    form.populate_obj(plan)

    previous_orgs = [organisation.organisation for organisation in plan.organisations]

    if isinstance(organisations, str):
        orgs = organisations.split(";")
        # add any new organisations
        for oid in orgs:
            org = Organisation.query.get(oid)
            plan.organisations.append(org)
            if oid in previous_orgs:
                previous_orgs.remove(oid)
        # remove old organisations
        for oid in previous_orgs:
            org = Organisation.query.get(oid)
            plan.organisations.remove(org)

    elif isinstance(organisations, list):
        for org in organisations:
            organisation = Organisation.query.get(org)
            plan.organisations.append(organisation)

    return plan


def _set_organisations(obj, org_str):
    previous_orgs = [organisation.organisation for organisation in obj.organisations]
    orgs = org_str.split(";")
    # add any new organisations
    for oid in orgs:
        org = Organisation.query.get(oid)
        obj.organisations.append(org)
        if oid in previous_orgs:
            previous_orgs.remove(oid)
    # remove old organisations
    for oid in previous_orgs:
        org = Organisation.query.get(oid)
        obj.organisations.remove(org)


def _get_organisation_choices():
    return [(org.organisation, org.name) for org in Organisation.query.all()]


def _get_plan_type_choices():
    return [
        (plan_type.reference, plan_type.name)
        for plan_type in DevelopmentPlanType.query.all()
    ]


def _get_event_choices():
    return [
        (evt.reference, evt.name)
        for evt in DevelopmentPlanEventType.query.order_by(
            DevelopmentPlanEventType.name
        ).all()
    ]


def _get_document_type_choices():
    return [(doc.reference, doc.name) for doc in DocumentType.query.all()]


def allowed_file(filename):
    from flask import current_app

    ALLOWED_EXTENSIONS = current_app.config["ALLOWED_EXTENSIONS"]
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
