from functools import wraps

from flask import current_app, request, session, url_for
from werkzeug.utils import redirect


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session and current_app.config.get("AUTHENTICATION_ON", False):
            return redirect(url_for("auth.login", redirect_url=request.path))
        return f(*args, **kwargs)

    return decorated


def get_current_user():
    if session and session.get("user") is not None:
        return session.get("user").get("userinfo").get("nickname")
    else:
        return None
