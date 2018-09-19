import time
from tests.base_test_client import FlaskTestClient
from app.user.models.user import User, Role, load_user
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
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_last_password_is_saved(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        u.password = 'dog'
        self.assertTrue(u.verify_password('dog'))
        self.assertTrue(u.verify_last_password('cat'))

    def test_users_created_in_db(self):
        u = User()
        db.session.add(u)
        db.session.commit()
        userlist = User.query.all()
        self.assertEqual(len(userlist), 1)

    def test_valid_confirmation_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        u1 = User(password='cat')
        u2 = User(password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))

    def test_valid_reset_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(u.reset_password(token, 'dog'))  # Test token value matches userid
        self.assertTrue(u.verify_password('dog'))  # Test new password is dog

    def test_invalid_reset_token(self):
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
        u = User(username='testuser')
        db.session.add(u)
        db.session.commit()
        u2 = load_user("1")
        self.assertEqual(u.username, u2.username)
        self.assertEqual(u.id, u2.id)

    def test_randomize_user(self):
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
        Role.initialize_roles()
        admin_role = Role.query.filter_by(name='Admin').first()
        super_admin_role = Role.query.filter_by(name='Super Admin').first()
        user_role = Role.query.filter_by(name='User').first()
        self.assertTrue(admin_role is not None)
        self.assertTrue(super_admin_role is not None)
        self.assertTrue(user_role is not None)

    def test_init_role_assign(self):
        u = User(username=user_dict.get('username'), role_id=1)
        db.session.add(u)
        self.assertIsInstance(u.role, Role)
        self.assertEqual(u.role.id, 1)
        db.session.delete(u)

        bad_id = Role.query.order_by(Role.id.desc()).first().id + 1
        u = User(username=user_dict.get('username'), role_id=bad_id)
        db.session.add(u)
        self.assertIs(u.role, Role.query.filter_by(default=True).first())
        self.assertNotEqual(u.role.id, bad_id)