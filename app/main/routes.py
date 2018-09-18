from flask import Response, g
from app.main import bp_main


@bp_main.before_app_request
def before_request():  # pragma: no cover
    pass


@bp_main.after_app_request
def apply_default_response_headers(response):
    response.headers['Content-Type'] = 'application/models+json'
    response.headers['Charset'] = 'UTF-8'
    if getattr(g, 'api_auth', False):
        Response.delete_cookie(response, 'session')
    return response
