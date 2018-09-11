from flask import Blueprint

api_bp = Blueprint('api_v1', __name__)
from . import resources, index, request_hooks, errors
