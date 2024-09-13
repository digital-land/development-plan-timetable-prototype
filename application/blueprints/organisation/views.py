import csv
import glob
import io
import shutil
import time
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

from flask import (
    Blueprint,
    Response,
    abort,
    redirect,
    render_template,
    request,
    url_for,
)

from application.export import download_file_map, model_map
from application.models import (
    DevelopmentPlan,
    DevelopmentPlanBoundary,
    DevelopmentPlanDocument,
    DevelopmentPlanTimetable,
    Organisation,
)
from application.utils import (
    get_adopted_local_plans,
    get_organisations_expected_to_publish_plan,
    split_orgs_by_adopted_locl_plan,
)

organisation_bp = Blueprint("organisation", __name__, url_prefix="/organisation")


@organisation_bp.route("/")
def organisations():
    if "organisation" in request.args:
        lpa = request.args.get("organisation")
        print(lpa)
        return redirect(
            url_for("organisation.organisation", reference=f"local-authority-eng:{lpa}")
        )

    all_orgs = get_organisations_expected_to_publish_plan()
    adopted_local_plans = get_adopted_local_plans()
    with_adopted_lp, without_adopted_lp = split_orgs_by_adopted_locl_plan(
        adopted_local_plans, all_orgs
    )

    orgs = all_orgs
    if request.args.get("planningAuthorityFilter"):
        if request.args.get("planningAuthorityFilter") == "with":
            orgs = with_adopted_lp
        elif request.args.get("planningAuthorityFilter") == "without":
            org_ids_to_remove = {org.organisation for org in with_adopted_lp}
            orgs = [
                org for org in all_orgs if org.organisation not in org_ids_to_remove
            ]

    return render_template(
        "organisation/index.html",
        organisations_expected_to_publish=all_orgs,
        organisations=orgs,
        adopted_plans=adopted_local_plans,
        orgs_with_adopted_plan=with_adopted_lp,
        planning_authority_filter=request.args.get("planningAuthorityFilter"),
    )


@organisation_bp.route("/<string:reference>")
def organisation(reference):
    organisation = Organisation.query.get(reference)
    if organisation is None:
        return abort(404)
    plans = {}
    for plan in organisation.development_plans:
        plans.setdefault(plan.development_plan_type, []).append(plan)

    return render_template(
        "organisation/organisation.html", organisation=organisation, plans=plans
    )


@organisation_bp.route("/<string:organisation>/download-plans")
def download_plans(organisation):
    tempdir = TemporaryDirectory()
    path = Path(tempdir.name)

    organisation = Organisation.query.get(organisation)

    for file, model in download_file_map.items():
        csv_path = path / file
        with open(csv_path, "w") as f:
            serializer_class = model_map[model]
            fieldnames = list(serializer_class.__fields__.keys())
            fieldnames = [field.replace("_", "-") for field in fieldnames]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            if model == DevelopmentPlan:
                for plan in organisation.development_plans:
                    serializer_class = model_map[model]
                    m = serializer_class.model_validate(plan)
                    data = m.model_dump(by_alias=True)
                    writer.writerow(data)
            elif model == DevelopmentPlanDocument:
                for document in organisation.development_plan_documents:
                    serializer_class = model_map[model]
                    m = serializer_class.model_validate(document)
                    data = m.model_dump(by_alias=True)
                    writer.writerow(data)
            elif model == DevelopmentPlanTimetable:
                for timetable in organisation.development_plan_timetables:
                    serializer_class = model_map[model]
                    m = serializer_class.model_validate(timetable)
                    data = m.model_dump(by_alias=True)
                    writer.writerow(data)
            elif model == DevelopmentPlanBoundary:
                for plan in organisation.development_plans:
                    if plan.development_plan_boundary is not None:
                        boundary = DevelopmentPlanBoundary.query.filter(
                            DevelopmentPlanBoundary.reference
                            == plan.development_plan_boundary
                        ).one_or_none()
                        if boundary is not None:
                            serializer_class = model_map[model]
                            m = serializer_class.model_validate(boundary)
                            data = m.model_dump(by_alias=True)
                            writer.writerow(data)

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
