from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from budget.models import Profile, FamilyGroup


class TestCategories(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(
            username="owner",
            password="pass12345",
        )
        self.owner_profile = Profile.objects.create(
            user=self.owner,
            nickname="Owner",
            income=0,
            expenses=0,
        )
        self.group = FamilyGroup.objects.create(
            name="Fam",
            code="F123",
            owner=self.owner_profile,
        )
        self.owner_profile.group = self.group
        self.owner_profile.save()
        self.url = reverse("category_manage")

    def test_owner_can_view_categories_page(self):
        self.client.login(username="owner", password="pass12345")
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Spending Categories")

    def test_owner_can_add_category(self):
        self.client.login(username="owner", password="pass12345")
        resp = self.client.post(
            self.url,
            {"name": "Groceries"},
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Groceries")

    def test_non_owner_cannot_manage_categories(self):
        User = get_user_model()
        member = User.objects.create_user(
            username="member",
            password="pass12345",
        )
        member_profile = Profile.objects.create(
            user=member,
            nickname="Member",
            income=0,
            expenses=0,
            group=self.group,
        )
        self.client.login(username="member", password="pass12345")
        resp = self.client.get(self.url)
        self.assertNotEqual(resp.status_code, 200)
