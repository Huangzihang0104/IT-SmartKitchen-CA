from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class PageTest(TestCase):

    def test_home_page_status_code(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)


class RegisterPageTest(TestCase):

    def test_register_page_loads(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)


class UserModelTest(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

        self.assertEqual(user.username, "testuser")
