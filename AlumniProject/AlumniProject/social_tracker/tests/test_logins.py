from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


"""
Test cases for login. Again, Django test function from
manage.py creates a mock database so any data put
into the database during tests is not permanent
and is not put into our actual database.
"""


class LoginTests(TestCase):
    def setUp(self):
        User.objects.create_user(username="J", email="user@sd.edu", password="pw0")

    def test_login_success(self):
        response = self.client.post(
            reverse("login"), {"email": "user@sd.edu", "password": "pw0"}
        )
        self.assertEqual(response.status_code, 200)

    def test_bad_pass(self):
        response = self.client.post(
            reverse("login"), {"email": "user@sd.edu", "password": "not"}
        )
        self.assertEqual(response.status_code, 401)

    def test_bad_user(self):
        response = self.client.post(
            reverse("login"), {"email": "bad@sd.edu", "password": "pw0"}
        )
        self.assertEqual(response.status_code, 401)

    def test_bad_both(self):
        response = self.client.post(
            reverse("login"), {"email": "bad@sd.edu", "password": "not"}
        )
        self.assertEqual(response.status_code, 401)

    def test_home_logged_in(self):
        self.client.post(reverse("login"), {"email": "user@sd.edu", "password": "pw0"})
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_home_not_logged_in(self):
        response = self.client.get(reverse("home"))
        self.assertRedirects(response, reverse("login") + "?next=" + reverse("home"))
