from flask import Blueprint

bp_errors = Blueprint('errors', '__name__')

from . import routes
