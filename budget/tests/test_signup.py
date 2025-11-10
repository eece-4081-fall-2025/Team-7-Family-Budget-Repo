from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class TestSignup(TestCase):
    def test_signup_page_loads(self):
        url = reverse("budget_signup")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Create your account", resp.content)

    def test_signup_creates_user_and_redirects(self):
        url = reverse("budget_signup")
        resp = self.client.post(
            url,
            {
                "username": "drake",
                "password1": "a-Strong_pass123",
                "password2": "a-Strong_pass123",
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse("login"))
        self.assertTrue(User.objects.filter(username="drake").exists())

    def test_signup_invalid_data_shows_errors(self):
        url = reverse("budget_signup")
        resp = self.client.post(
            url,
            {
                "username": "x",
                "password1": "abc",
                "password2": "zzz",
            },
        )
        self.assertEqual(resp.status_code, 200)
        form = resp.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("password2", form.errors)
