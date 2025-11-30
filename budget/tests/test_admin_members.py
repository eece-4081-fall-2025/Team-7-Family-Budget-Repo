from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from budget.models import FamilyGroup, Profile


class TestAdminManageMembers(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pw12345")
        self.other = User.objects.create_user(username="other", password="pw12345")

        self.owner_profile = Profile.objects.create(user=self.owner)
        self.other_profile = Profile.objects.create(user=self.other)

        self.group = FamilyGroup.objects.create(
            name="Fam",
            code="ABC123",
            owner=self.owner,
        )
        self.owner_profile.group = self.group
        self.owner_profile.save()

        self.manage_url = reverse("group_manage_members")

    def test_owner_can_add_member_by_username(self):
        self.client.login(username="owner", password="pw12345")
        resp = self.client.post(
            self.manage_url,
            {"action": "add", "username": "other"},
            follow=True,
        )
        self.other_profile.refresh_from_db()
        self.assertEqual(self.other_profile.group, self.group)
        self.assertEqual(resp.status_code, 200)

    def test_owner_can_remove_member(self):
        self.other_profile.group = self.group
        self.other_profile.save()

        self.client.login(username="owner", password="pw12345")
        remove_url = reverse("group_remove_member", args=[self.other_profile.pk])
        resp = self.client.post(remove_url, follow=True)

        self.other_profile.refresh_from_db()
        self.assertIsNone(self.other_profile.group)
        self.assertEqual(resp.status_code, 200)
