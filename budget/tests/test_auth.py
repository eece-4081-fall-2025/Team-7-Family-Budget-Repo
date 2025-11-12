from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class TestAuth(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="drake", password="testpass123")

    def test_login_page_loads(self):
        url = reverse("login")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Log in", resp.content)

    def test_login_success_redirects_home(self):
        url = reverse("login")
        resp = self.client.post(url, {"username": "drake", "password": "testpass123"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, "/")

    def test_logout_and_protected_view_requires_login(self):
        self.client.login(username="drake", password="testpass123")
        self.client.logout()
        resp = self.client.get(reverse("budget_dashboard"))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/accounts/login/"))
