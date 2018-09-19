import time
from tests.base_test_client import FlaskTestClient
from app.user.models.user import User, Role, load_user
from app.user.models.app_group import AppGroup
from app.auth.security import app_group_dict
from app.extensions import db

user_dict = dict(email="JOHN.DOE@EXAMPLE.COM",
                 username="JOHN.DOE",
                 password="testpw",
                 first_name="JOHN",
                 last_name="DOE",
                 confirmed=True)


def create_test_user(username=user_dict.get("username"),
                     email=user_dict.get("email"),
                     password=user_dict.get("password"),
                     confirmed=user_dict.get("confirmed"),
                     first_name=user_dict.get("first_name"),
                     last_name=user_dict.get("last_name"),
                     ):
    u = User(username=username, password=password, confirmed=confirmed, first_name=first_name,
             last_name=last_name)
    db.session.add(u)
    return u


class UserModelTestCase(FlaskTestClient):

    def test_password_setter(self):
        """Test password hash is populated"""
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_password_verification(self):
        """Test password hash verification with known password"""
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        """Test password is stored as salted hash with userid as salt source"""
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_last_password_is_saved(self):
        """Test that old password is stored and can be verified on password change"""
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        u.password = 'dog'
        self.assertTrue(u.verify_password('dog'))
        self.assertTrue(u.verify_last_password('cat'))

    def test_users_created_in_db(self):
        """When we add a user, does it actually exist in the database?"""
        u = User()
        db.session.add(u)
        db.session.commit()
        userlist = User.query.all()
        self.assertEqual(len(userlist), 1)

    def test_valid_confirmation_token(self):
        """Check that confirmation token processes in the User model"""
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        """
        Test an invalid confirmation token, confirm it cannot be used to confirm
        the wrong user
        """
        u1 = User(password='cat')
        u2 = User(password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):
        """Test expired confirmation token, confirm it cannot be used to confirm user"""
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))

    def test_valid_reset_token(self):
        """Test a valid password reset token is accepted"""
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(u.reset_password(token, 'dog'))  # Test token value matches userid
        self.assertTrue(u.verify_password('dog'))  # Test new password is dog

    def test_invalid_reset_token(self):
        """Test that an invalid password reset token is not accepted"""
        u1 = User(password='cat')
        u2 = User(password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_reset_token()
        none_token = None
        self.assertFalse(u2.reset_password(token, 'horse'))
        self.assertFalse(u2.reset_password(none_token, 'horse'))
        self.assertTrue(u2.verify_password('dog'))

    def test_load_user(self):
        """Test userloader returns a user record"""
        u = User(username='testuser')
        db.session.add(u)
        db.session.commit()
        u2 = load_user(u.id)
        self.assertIs(u, u2)

    def test_randomize_user(self):
        """Test creation of random user records"""
        user = User()
        user.randomize_user()
        db.session.add(user)
        self.assertTrue(user is not None)
        self.assertTrue(user.email is not None)
        self.assertTrue(user.phone_number.number is not None)
        self.assertTrue(user.first_name is not None)
        self.assertTrue(user.last_name is not None)
        self.assertTrue(user.dob is not None)
        self.assertTrue(user.active)
        self.assertFalse(user.confirmed)
        self.assertEqual(user.role.name, 'User')

    def test_initialize_roles_staticmethod(self):
        """Confirm roles are initialized"""
        Role.initialize_roles()
        admin_role = Role.query.filter_by(name='Admin').first()
        super_admin_role = Role.query.filter_by(name='Super Admin').first()
        user_role = Role.query.filter_by(name='User').first()
        self.assertTrue(admin_role is not None)
        self.assertTrue(super_admin_role is not None)
        self.assertTrue(user_role is not None)

    def test_init_role_assign_integer(self):
        """
        Test assigning role on User initialization
        --Allow for integer role_id on init
        """
        u = User(username=user_dict.get('username'), role=1)
        db.session.add(u)
        self.assertIsInstance(u.role, Role)
        self.assertEqual(u.role.id, 1, 'Role id integer not processed during User init')
        db.session.delete(u)

        bad_id = Role.query.order_by(Role.id.desc()).first().id + 1
        u = User(username=user_dict.get('username'), role=bad_id)
        db.session.add(u)
        self.assertIs(u.role, Role.query.filter_by(default=True).first(), 'Default role not assigned to User')
        self.assertNotEqual(u.role.id, bad_id, 'Default role not assigned to User')

    def test_init_role_assign_role_object(self):
        """
        Test assigning role on User initialization
        --Allow for passing SQLAlchemy Role object on init
        """
        role = Role.query.filter_by(default=False).first()
        u = User(username=user_dict.get('username'), role=role)
        db.session.add(u)
        self.assertIs(u.role, role, 'Could not assign Role object to User during init')

    def test_init_role_assign_default(self):
        """
        Test assigning role on User initialization
        --Confirm default Role is assigned
        """
        u = User(username=user_dict.get('username'), role=None)
        db.session.add(u)
        self.assertIs(u.role, Role.query.filter_by(default=True).first(), 'Default role not assigned')

    def test_initialize_app_groups_staticmethod(self):
        """
        Test AppGroup.initialize_app_groups() to ensure app_group records
        are created as expected
        """
        # Note: AppGroup initialization completed in SetUp
        ag_names = {x.name for x in AppGroup.query.all()}
        self.assertIsNotNone(ag_names, 'ApGroups not initialized')
        expected_names = {x for x in app_group_dict}
        self.assertEqual(ag_names, expected_names, 'AppGroups created do not match expected')
        
    def test_init_appgroup_assign_integer(self):
        """
        Test assigning app_groups on User initialization
        --Allow for integer app_group.id on init
        """
        u = User(username=user_dict.get('username'), app_group=1)
        db.session.add(u)
        self.assertIsInstance(u.app_groups[0], AppGroup)
        self.assertEqual(u.app_groups[0].id, 1, 'AppGroup id integer not processed during User init')
        db.session.delete(u)

        bad_id = AppGroup.query.order_by(AppGroup.id.desc()).first().id + 1
        u = User(username=user_dict.get('username'), app_group=bad_id)
        db.session.add(u)
        self.assertIs(u.app_groups[0], AppGroup.query.filter_by(default=True).first(), 'Default app-group not assigned to User')
        self.assertNotEqual(u.app_groups[0].id, bad_id, 'Default app-group not assigned to User')

    def test_init_appgroup_assign_object(self):
        """
        Test assigning app_groups on User initialization
        --Allow for passing SQLAlchemy AppGroup object on init
        """
        appgroup = AppGroup.query.filter_by(default=False).first()
        u = User(username=user_dict.get('username'), app_group=appgroup)
        db.session.add(u)
        self.assertIs(u.app_groups[0], appgroup, 'Could not assign AppGroup object to User during init')

    def test_init_appgroup_assign_default(self):
        """
        Test assigning app_groups on User initialization
        --Confirm default AppGroup is assigned
        """
        u = User(username=user_dict.get('username'), app_group=None)
        db.session.add(u)
        self.assertIs(u.app_groups[0], AppGroup.query.filter_by(default=True).first(), 'Default appgroup not assigned')