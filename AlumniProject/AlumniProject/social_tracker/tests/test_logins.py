from django.test import TestCase
from django.urls import reverse
from social_tracker.models import User


"""
Test cases for logins. Again, Django test function from manage.py creates
a mock database so any data put into the database during tests is not permanent
and is not put into our actual database.
"""
class LoginTests(TestCase):
    def setUp(self):
        User.objects.create_user(username="John User", email="user@sandiego.edu", password="passw0rd")

    def test_login_success(self):
        response = self.client.post(reverse("login"), {"email":"user@sandiego.edu", "password": "passw0rd"})
        self.assertEqual(response.status_code, 200)

    def test_bad_pass(self):
        response = self.client.post(reverse("login"), {"email":"user@sandiego.edu", "password":"notmypass"})
        self.assertEqual(response.status_code, 401)

    def test_bad_user(self):
        response = self.client.post(reverse("login"), {"email":"bad@sandiego.edu", "password":"passw0rd"})
        self.assertEqual(response.status_code, 401)

    def test_bad_both(self):
        response = self.client.post(reverse("login"), {"email":"bad@sandiego.edu", "password":"notmypass"})
        self.assertEqual(response.status_code, 401)