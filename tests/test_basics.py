# from flask import current_app
# from flask_testing import TestCase
# from unkani_app import create_app as create_application
# from unkani_app import sa
#
#
# class BasicsTestCase(TestCase):
#     def create_app(self):
#         unkani_app = create_application('testing')
#         return unkani_app
#
#     def setUp(self):
#         sa.drop_all()
#         sa.create_all()
#
#     def tearDown(self):
#         sa.session.remove()
#         sa.drop_all()
#         sa.create_all()
#
#     def test_app_exists(self):
#         self.assertFalse(current_app is None)
#
#     def test_app_is_testing(self):
#         self.assertTrue(current_app.config['TESTING'])
