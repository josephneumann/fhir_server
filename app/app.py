# -*- coding: utf-8 -*-
"""The app module, containing the app factory function"""
import os
from flask import Flask, sessions
from flask_sslify import SSLify
from sqlalchemy import or_, and_, any_
from sqlalchemy.orm import configure_mappers

from config import config
from app.extensions import db, ma, principal, migrate, bcrypt
from app import auth, errors, fhir, main, user, commands
from app.fhir import models as fhirmodels
from app.user import models as usermodels
from app.main import models as mainmodels


def create_app(config_name=None):
    """Wrapper function to run application factory"""
    if not config_name:
        config_name = os.getenv('FLASK_CONFIG') or 'default'
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config[config_name])
    register_extensions(app)
    register_blueprints(app)
    register_shell_context(app)
    register_commands(app)

    configure_mappers()
    return app


def register_extensions(app):
    """Register Flask extensions"""

    migrate.init_app(app, db, directory='migrations')
    db.init_app(app)
    principal.init_app(app)
    ma.init_app(app)
    if not app.config['SSL_DISABLE']:  # pragma: no cover
        sslify = SSLify(app)
    bcrypt.init_app(app)
    return None


def register_blueprints(app):
    """Register Flask Blueprints"""
    app.register_blueprint(main.bp_main, url_prefix='/api/v1/')
    app.register_blueprint(auth.bp_auth, url_prefix='/api/v1/')
    app.register_blueprint(errors.bp_errors, url_prefix='/api/v1/')
    app.register_blueprint(fhir.bp_fhir, url_prefix='/api/v1/')
    app.register_blueprint(user.bp_user, url_prefix='/api/v1/')
    return None


def register_shell_context(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects"""
        return dict(app=app,
                    db=db,
                    User=usermodels.user.User,
                    Role=usermodels.role.Role,
                    AppGroup=usermodels.app_group.AppGroup,
                    AppPermission=usermodels.app_permission.AppPermission,
                    role_app_permission=usermodels.app_permission.role_app_permission,
                    user_app_group=usermodels.app_group.user_app_group,
                    Patient=fhirmodels.patient.Patient,
                    Address=fhirmodels.address.Address,
                    PhoneNumber=fhirmodels.phone_number.PhoneNumber,
                    EmailAddress=fhirmodels.email_address.EmailAddress,
                    Organization=fhirmodels.organization.Organization,
                    SourceData=mainmodels.source_data.SourceData,
                    CodeSystem=fhirmodels.codesets.CodeSystem,
                    ValueSet=fhirmodels.codesets.ValueSet,
                    or_=or_,
                    and_=and_,
                    any_=any_)

    app.shell_context_processor(shell_context)
    return None


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.deploy)
    app.cli.add_command(commands.gunicorn)
    app.cli.add_command(commands.patients)
    app.cli.add_command(commands.synthea)
    app.cli.add_command(commands.drop_all)
    return None


class CustomSessionInterface(sessions.SecureCookieSessionInterface):
    """Disable default cookie generation."""

    def should_set_cookie(self, *args, **kwargs):
        return False

    """Prevent creating session from API requests."""

    def save_session(self, *args, **kwargs):
        if g.get('api_auth'):
            return
        return super(CustomSessionInterface, self).save_session(*args, **kwargs)
