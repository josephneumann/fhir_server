# from flask import g
# from sqlalchemy_continuum import make_versioned
# from sqlalchemy_continuum.plugins import FlaskPlugin, PropertyModTrackerPlugin

#
# def fetch_current_user_id():
#     """Fetch the current user id value for version logging and auditing"""
#     try:
#         return g.current_user.id
#     except AttributeError:
#         return
#
#
# make_versioned(plugins=[FlaskPlugin(current_user_id_factory=fetch_current_user_id), PropertyModTrackerPlugin()])

from . import codesets, address, email_address, organization, phone_number, patient
