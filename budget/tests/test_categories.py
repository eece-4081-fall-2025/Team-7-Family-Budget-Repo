from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from budget.models import Profile, FamilyGroup, Category
from budget import services

User = get_user_model()


class TestCategories(TestCase):
    def setUp(self):
        self.owner_user = User.objects.create_user(
            username="owner", password="pass123"
        )
        self.other_user = User.objects.create_user(
            username="other", password="pass123"
        )

        self.owner_profile = Profile.objects.create(
            user=self.owner_user,
            nickname="Owner",
            income=0,
            expenses=0,
        )
        self.other_profile = Profile.objects.create(
            user=self.other_user,
            nickname="Member",
            income=0,
            expenses=0,
        )

        self.group = FamilyGroup.objects.create(
            name="Fam",
            code="F123",
            owner=self.owner_user,
        )

        services.attach_profile_to_group(self.owner_profile, self.group)
        services.attach_profile_to_group(self.other_profile, self.group)

        self.url = reverse("category_manage")

    def test_owner_can_view_categories_page(self):
        self.client.force_login(self.owner_user)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Spending Categories", resp.content)

    def test_owner_can_add_category(self):
        self.client.force_login(self.owner_user)
        resp = self.client.post(self.url, {"name": "Groceries"}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(
            Category.objects.filter(group=self.group, name="Groceries").exists()
        )
        self.assertIn(b"Groceries", resp.content)

    def test_non_owner_cannot_manage_categories(self):
        self.client.force_login(self.other_user)
        resp = self.client.get(self.url)
        self.assertNotEqual(resp.status_code, 200)
