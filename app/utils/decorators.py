from functools import wraps
from urllib.parse import urlparse, urljoin
from flask import request, abort, redirect, url_for
from flask_login import current_user, login_required


def admin_required(f):
    """
    Decorator requiring the current user to be authenticated and possess
    the 'admin' role. Unauthenticated requests redirect to login;
    unauthorized customer requests are denied with HTTP 403 Forbidden.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def is_safe_url(target: str) -> bool:
    """Verify that a redirect target URL is safe and points to the same host."""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc
