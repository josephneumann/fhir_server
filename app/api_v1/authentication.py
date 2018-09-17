from flask import g, jsonify, url_for, current_app, session
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from flask_principal import identity_changed, Identity, identity_loaded, UserNeed, RoleNeed
from app.extensions import db
from app.models.user import User
from app.models.fhir.email_address import EmailAddress
from app.models.role import Role
from app.security import AppPermissionNeed
from app.api_v1 import api_bp
from app.api_v1.errors.exceptions import *

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()
multi_auth = MultiAuth(basic_auth, token_auth)


@basic_auth.verify_password
def verify_password(email, password):
    if not email:
        raise BasicAuthError("HTTP Basic-auth failed on condition: No email address provided.")
    user = db.session.query(User).join(EmailAddress).filter(EmailAddress.active == True).filter(
        EmailAddress.email == str(email).upper().strip()).first()
    if user is None:
        raise BasicAuthError("HTTP Basic-auth failed on condition: No user matching the provided email found.")
    if not user.verify_password(password):
        return False
    if not user.confirmed:
        raise BasicAuthError("HTTP Basic-auth failed on condition: User account is unconfirmed")
    if not user.active:
        raise BasicAuthError("HTTP Basic-auth failed on condition: User account is inactive")
    setattr(g, 'current_user', user)
    setattr(g, 'api_auth', True)  # Set a flag in request g to indicate this is an API request
    identity_changed.send(current_app._get_current_object(),
                          identity=Identity(user.id))
    return True


@basic_auth.error_handler
def auth_error():
    """Handles circumstances where the function decorated with basic_auth.verify_password
    returns a False boolean.  Functionally means password was invalid."""
    raise BasicAuthError("HTTP Basic-auth failed on condition: password could not be verified.")


@token_auth.verify_token
def verify_token(token):
    """Token verification callback.  Sets user identity and permissions for request."""
    # Check is token exists
    if not token:
        return False
    # Extract user from valid token
    user, expired = User.verify_api_auth_token(token)
    # Check if user is returned from token
    if user is None:
        raise TokenAuthError("Token is invalid.")
    # Token must not be expired
    if expired:
        raise TokenExpiredError("User authentication token expired.")
    # User must be confirmed
    if not user.confirmed:
        raise TokenAuthError("User account is unconfirmed.")
    # Set global request context g.current_user variable which is used in API routes
    # Since sessions are not used in RESTapi, there should not be any authentication info stored in session with
    # flask-login's login_user function
    setattr(g, 'current_user', user)
    setattr(g, 'api_auth', True)  # Set a flag in request g to indicate this is an API request
    identity_changed.send(current_app._get_current_object(),
                          identity=Identity(user.id))
    return True


@token_auth.error_handler
def token_error():
    """Handles circumstances where the function decorated with token_auth.verify_password
    returns a False boolean.  Functionally means token was invalid."""
    raise TokenAuthError('Invalid token provided for authentication')


@api_bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def new_token():
    """
    Request a user token.
    This endpoint requires basic auth with email and password
    for a confirmed account
    This endpoint returns a Timed JSON Web Signature token
    """
    token = g.current_user.generate_api_auth_token()
    return jsonify({'token': token})


@api_bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    g.current_user.revoke_token()
    db.session.commit()


@identity_loaded.connect
def on_identity_loaded(sender, identity):
    # Set the identity user object
    if getattr(g, 'current_user', None):
        identity.user = g.current_user
    else:
        identity.user = None
    # Add the UserNeed to the identity
    if hasattr(identity.user, 'id'):
        identity.provides.add(UserNeed(identity.user.id))
    # Update the identity with the roles that the user provides
    if hasattr(identity.user, 'role_id'):
        role = Role.query.join(User).filter(User.id == identity.user.id).first()
        identity.provides.add(RoleNeed(role.name))
        app_permissions = role.app_permissions
        for perm in app_permissions:
            identity.provides.add(AppPermissionNeed(str(perm.name)))
