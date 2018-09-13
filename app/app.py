# -*- coding: utf-8 -*-
"""The app module, containing the app factory function"""
import os
from flask import Flask
from flask_sslify import SSLify
from sqlalchemy import or_, and_, any_
from config import config
from app.extensions import db, login_manager, ma, redis, principal, session, migrate
from app import api_v1, commands

from app.models.user import User, UserAPI
from app.models.role import Role
from app.models.fhir.patient import Patient
from app.models.app_permission import AppPermission, role_app_permission
from app.models.fhir.address import Address, AddressAPI
from app.models.fhir.email_address import EmailAddress, EmailAddressAPI
from app.models.app_group import AppGroup, user_app_group
from app.models.fhir.phone_number import PhoneNumber, PhoneNumberAPI
from app.models.fhir.organization import Organization
from app.models.source_data import SourceData
from app.models.fhir.codesets import CodeSystem, ValueSet


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
    return app


def register_extensions(app):
    """Register Flask extensions"""

    app.config.update(SESSION_REDIS=redis)
    migrate.init_app(app, db)
    db.init_app(app)
    login_manager.session_protection = 'strong'
    # login_manager.login_view = 'auth.login'
    login_manager.login_message = 'You must log in to view this page.'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)
    principal.init_app(app)
    ma.init_app(app)
    if app.config.get('SERVER_SESSION'):
        session.init_app(app)
    if not app.config['SSL_DISABLE']:  # pragma: no cover
        sslify = SSLify(app)
    return None


def register_blueprints(app):
    """Register Flask Blueprints"""
    app.register_blueprint(api_v1.api_bp, url_prefix='/api/v1')
    return None


def register_shell_context(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects"""
        return dict(app=app, db=db, PhoneNumber=PhoneNumber, User=User, Role=Role, AppPermission=AppPermission,
                    Patient=Patient, Address=Address, EmailAddress=EmailAddress, AppGroup=AppGroup, UserAPI=UserAPI,
                    user_app_group=user_app_group, EmailAddressAPI=EmailAddressAPI, PhoneNumberAPI=PhoneNumberAPI,
                    role_app_permission=role_app_permission, AddressAPI=AddressAPI, Organization=Organization,
                    SourceData=SourceData, CodeSystem=CodeSystem, ValueSet=ValueSet,
                    or_=or_, and_=and_, any_=any_)

    app.shell_context_processor(shell_context)
    return None


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.deploy)
    app.cli.add_command(commands.drop_all)
    app.cli.add_command(commands.gunicorn)
    app.cli.add_command(commands.patients)
    return None
