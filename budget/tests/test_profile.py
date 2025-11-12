from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class TestProfile(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="drake", password="testpass123")

    def test_profile_edit_requires_login(self):
        url = reverse("profile_edit")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/accounts/login/"))

    def test_profile_edit_page_loads(self):
        self.client.login(username="drake", password="testpass123")
        url = reverse("profile_edit")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Update Profile", resp.content)

    def test_profile_update_saves_values(self):
        self.client.login(username="drake", password="testpass123")
        url = reverse("profile_edit")
        resp = self.client.post(url, {"income": "5000.00", "expenses": "1200.00"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, "/dashboard/")
        from budget.models import Profile

        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.income, Decimal("5000.00"))
        self.assertEqual(profile.expenses, Decimal("1200.00"))
