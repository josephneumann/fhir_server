from flask import Response, g, jsonify, url_for
from app.main import bp_main
from app.main.utils.etag import etag


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


@bp_main.route('/', methods=['GET'])
@etag
def index():
    response = jsonify(
        {
            'resources':
                {'FHIR-STU3':
                     {'CodeSystem': url_for('fhir.get_codesystems', _external=True),
                      'ValueSet': url_for('fhir.get_valuesets', _external=True),
                      'Patient': url_for('fhir.patient_search', _external=True)},
                 'custom':
                     {'User': url_for('user.get_users', _external=True)}
                 },
            'authentication': url_for('auth.new_token', _external=True)
        }
    )
    response.status_code = 200
    return response
