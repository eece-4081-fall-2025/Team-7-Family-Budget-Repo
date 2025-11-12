from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from budget.models import Profile, FamilyGroup
from decimal import Decimal

User = get_user_model()


class TestGroups(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="pass12345")
        self.bob = User.objects.create_user(username="bob", password="pass12345")
        Profile.objects.get_or_create(user=self.alice)
        Profile.objects.get_or_create(user=self.bob)
        self.group = FamilyGroup.objects.create(name="Watters", code="W123")

    def test_join_requires_login(self):
        resp = self.client.get(reverse("group_join"))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/accounts/login/"))

    def test_join_by_code_attaches_profile(self):
        self.client.login(username="alice", password="pass12345")
        resp = self.client.post(reverse("group_join"), {"code": "W123"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, "/group/members/")
        p = Profile.objects.get(user=self.alice)
        self.assertEqual(p.group, self.group)

    def test_members_list_shows_all_group_users(self):
        self.client.login(username="alice", password="pass12345")
        self.client.post(reverse("group_join"), {"code": "W123"})
        self.client.logout()
        self.client.login(username="bob", password="pass12345")
        self.client.post(reverse("group_join"), {"code": "W123"})
        resp = self.client.get(reverse("group_members"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"alice", resp.content)
        self.assertIn(b"bob", resp.content)
