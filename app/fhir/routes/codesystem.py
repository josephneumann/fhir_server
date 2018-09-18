from app.fhir import bp_fhir
from app.auth.authentication import token_auth
from app.user.errors import *
from app.main.utils.rate_limit import rate_limit
from app.main.utils.etag import etag
from app.fhir.models.codesets import CodeSystem
from flask import url_for


@bp_fhir.route('fhir/CodeSystem/<string:resource_id>', methods=['GET'])
@token_auth.login_required
@rate_limit(limit=5, period=15)
@etag
def get_codesystem(resource_id):
    """
    Return a FHIR CodeSystem resource as JSON.
    """
    codesystem = CodeSystem.query.filter(CodeSystem.resource_id == resource_id).first_or_404()
    data = codesystem.dump_fhir_json()
    response = jsonify(data)
    response.headers['Location'] = url_for('fhir.get_codesystem', resource_id=codesystem.resource_id)
    response.status_code = 200
    return response


@bp_fhir.route('fhir/CodeSystem', methods=['GET'])
@token_auth.login_required
@rate_limit(limit=5, period=15)
@etag
def get_codesystems():
    """
    Return FHIR CodeSystem routes as JSON.
    """
    return jsonify('Coming Soon!')
