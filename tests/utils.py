from flask_testing import TestCase
from app.extensions import db
from app.app import create_app as create_application
from app.user.models.user import User, Role
from app.user.models.app_permission import AppPermission

# Default user information for testing authentication
user_dict = dict(email="JOHN.DOE@EXAMPLE.COM",
                 username="JOHN.DOE",
                 password="testpw",
                 first_name="JOHN",
                 last_name="DOE",
                 confirmed=True)


# Common setup, teardown and utility methods to be re-used with each test module
# Subclasses flask_testings TestCase, which is itself a subclass of unittest.TestCase
class BaseClientTestCase(TestCase):
    # Default render templates to True
    render_templates = True

    def create_app(self):
        self.app = create_application('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        return self.app

    def setUp(self):
        db.drop_all()
        db.create_all()
        AppPermission.initialize_app_permissions()
        Role.initialize_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.create_all()

    def create_test_user(self, username=user_dict.get("username"),
                         email=user_dict.get("email"),
                         password=user_dict.get("password"),
                         confirmed=user_dict.get("confirmed"),
                         first_name=user_dict.get("first_name"),
                         last_name=user_dict.get("last_name"),
                         ):
        u = User(username=username, email=email, password=password, confirmed=confirmed, first_name=first_name,
                 last_name=last_name)
        db.session.add(u)
        db.session.commit()

    def get_test_user(self, username=user_dict.get("username")):
        return User.query.filter_by(_username=username.upper()).first()
