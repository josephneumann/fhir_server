from flask import Blueprint

bp_fhir = Blueprint('fhir', '__name__', template_folder='app/fhir/templates')

from . import routes
