from flask import Blueprint, redirect, render_template, request, url_for

from application.models import Organisation

organisation_bp = Blueprint("organisation", __name__, url_prefix="/organisation")


@organisation_bp.route("/")
def organisations():
    if "organisation" in request.args:
        lpa = request.args.get("organisation")
        print(lpa)
        return redirect(
            url_for("organisation.organisation", reference=f"local-authority-eng:{lpa}")
        )

    return render_template("organisation/index.html")


@organisation_bp.route("/<string:reference>")
def organisation(reference):
    organisation = Organisation.query.get(reference)
    return render_template("organisation/organisation.html", organisation=organisation)
