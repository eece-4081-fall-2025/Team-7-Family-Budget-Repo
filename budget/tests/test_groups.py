from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from budget.models import FamilyGroup, Profile

User = get_user_model()


class TestGroups(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            password="testpass123",
        )

        self.group = FamilyGroup.objects.create(
            name="Watters",
            code="W123",
            owner=self.owner,
        )

        self.user = User.objects.create_user(
            username="joiner",
            password="testpass123",
        )
        self.profile = Profile.objects.create(user=self.user)

    def test_join_requires_login(self):
        resp = self.client.post(
            reverse("group_join"),
            {"code": "W123"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_join_by_code_attaches_profile(self):
        self.client.login(username="joiner", password="testpass123")
        resp = self.client.post(
            reverse("group_join"),
            {"code": "W123"},
            follow=True,
        )
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.group, self.group)
        self.assertContains(resp, "Watters")

    def test_members_list_shows_all_group_users(self):
        self.profile.group = self.group
        self.profile.save()

        owner_profile, _ = Profile.objects.get_or_create(user=self.owner)
        owner_profile.group = self.group
        owner_profile.save()

        self.client.login(username="owner", password="testpass123")
        resp = self.client.get(reverse("group_members"))

        self.assertContains(resp, "owner")
        self.assertContains(resp, "joiner")
