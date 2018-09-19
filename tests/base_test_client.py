from flask_testing import TestCase
from app.extensions import db
from app.app import create_app as create_application
from app.user.models.user import Role
from app.user.models.app_permission import AppPermission
from app.user.models.app_group import AppGroup

# Common setup, teardown and utility methods to be re-used with each test module
# Subclasses flask_testings TestCase, which is itself a subclass of unittest.TestCase
class FlaskTestClient(TestCase):
    """"""
    render_templates = True  # Default render templates to True

    def create_app(self):
        self.app = create_application('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        return self.app

    def setUp(self):
        db.create_all()
        AppPermission.initialize_app_permissions()
        Role.initialize_roles()
        AppGroup.initialize_app_groups()
        self.client = self.app.test_client(use_cookies=False)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
