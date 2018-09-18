from flask import Blueprint

bp_user = Blueprint('user', '__main__')

from . import routes