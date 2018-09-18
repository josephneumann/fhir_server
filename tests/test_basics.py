from flask import current_app
from flask_testing import TestCase
from unkani import create_app
from app.extensions import db


class BasicsTestCase(TestCase):
    """Fundamental test cases which confirm app and database are constructed"""

    def create_app(self):
        """Use application factory to build app"""
        app = create_app('testing')
        return app

    def setUp(self):
        """Setup the database"""
        db.create_all()
        pass

    def tearDown(self):
        """Teardown the database"""
        db.session.remove()
        db.drop_all()

    def test_app_exists(self):
        """Assert app is created"""
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        """Assert app is using testing configuration"""
        self.assertTrue(current_app.config['TESTING'])
