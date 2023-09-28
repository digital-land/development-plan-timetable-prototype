from urllib.parse import quote_plus, urlencode

from flask import Blueprint, redirect, session, url_for

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/login")
def login():
    from application.extensions import oauth

    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("auth.callback", _external=True)
    )


@auth.route("/callback", methods=["GET", "POST"])
def callback():
    from application.extensions import oauth

    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect(url_for("base.index"))


@auth.route("/logout")
def logout():
    from flask import current_app

    session.clear()
    auth0_domain = current_app.config.get("AUTH0_DOMAIN")
    auth0_client_id = current_app.config.get("AUTH0_CLIENT_ID")
    url = f"https://{auth0_domain}/v2/logout?"
    index = url_for("base.index", _external=True)
    query_str = urlencode(
        {
            "returnTo": index,
            "client_id": auth0_client_id,
        },
        quote_via=quote_plus,
    )
    return redirect(f"{url}{query_str}")
