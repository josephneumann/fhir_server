from flask import jsonify, url_for
from app.auth import bp_auth
from app.main.utils.etag import etag


@bp_auth.route('/', methods=['GET'])
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
