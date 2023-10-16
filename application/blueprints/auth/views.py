from urllib.parse import quote_plus, urlencode

from flask import Blueprint, redirect, request, session, url_for
from is_safe_url import is_safe_url

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/login")
def login():
    from application.extensions import oauth

    session["redirect_url"] = _make_redirect_url_safe(
        request.args.get("redirect_url", "/")
    )
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("auth.callback", _external=True)
    )


@auth.route("/callback", methods=["GET", "POST"])
def callback():
    from application.extensions import oauth

    redirect_url = session.pop("redirect_url", None)
    token = oauth.auth0.authorize_access_token()
    session["user"] = token

    if redirect_url:
        return redirect(redirect_url)
    else:
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


def _make_redirect_url_safe(redirect_url):
    from flask import current_app

    if redirect_url is None:
        return url_for("base.index")
    if not is_safe_url(redirect_url, current_app.config.get("SAFE_URLS", {})):
        return url_for("base.index")
    return redirect_url
