from flask import _app_ctx_stack, _request_ctx_stack, g
from sqlalchemy.orm import configure_mappers
from sqlalchemy_continuum import make_versioned
from sqlalchemy_continuum.plugins import FlaskPlugin, PropertyModTrackerPlugin


def fetch_current_user_id():
    """Fetch the current user id value for version logging and auditing"""
    try:
        return g.current_user.id
    except AttributeError:
        return


make_versioned(plugins=[FlaskPlugin(current_user_id_factory=fetch_current_user_id), PropertyModTrackerPlugin()])

from . import user, role, app_permission, app_group, source_data
from .fhir import address, codesets, email_address, organization, patient, phone_number

configure_mappers()
