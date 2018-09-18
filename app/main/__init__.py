from flask import Blueprint

bp_main = Blueprint('main', '__name__', template_folder='app/main/templates')

from . import routes