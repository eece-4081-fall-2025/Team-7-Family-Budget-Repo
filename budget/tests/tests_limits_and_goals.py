from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from budget.models import Profile, FamilyGroup, Category, Goal

User = get_user_model()


class TestBudgetLimits(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", password="testpass123"
        )
        self.owner_profile = Profile.objects.create(
            user=self.owner,
            nickname="Boss",
            income=Decimal("5000.00"),
            expenses=Decimal("1000.00"),
        )

        self.group = FamilyGroup.objects.create(
            name="Fam",
            code="F123",
            owner=self.owner,
        )

        self.owner_profile.group = self.group
        self.owner_profile.save()

        self.category = Category.objects.create(
            group=self.group,
            name="Groceries",
        )

        self.client.force_login(self.owner)
        self.manage_url = reverse("category_manage")

    def test_owner_can_set_budget_limit_for_category(self):
        response = self.client.post(
            self.manage_url,
            {
                "category_id": str(self.category.id),
                "limit": "500.00",
            },
            follow=True,
        )

        self.category.refresh_from_db()
        self.assertEqual(self.category.budget_limit, Decimal("500.00"))


class TestGoals(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", password="testpass123"
        )
        self.owner_profile = Profile.objects.create(
            user=self.owner,
            nickname="Boss",
            income=Decimal("5000.00"),
            expenses=Decimal("1000.00"),
        )

        self.other = User.objects.create_user(
            username="other", password="testpass123"
        )
        self.other_profile = Profile.objects.create(
            user=self.other,
            nickname="Member",
            income=Decimal("3000.00"),
            expenses=Decimal("800.00"),
        )

        self.group = FamilyGroup.objects.create(
            name="Fam",
            code="G123",
            owner=self.owner,
        )

        self.owner_profile.group = self.group
        self.owner_profile.save()

        self.other_profile.group = self.group
        self.other_profile.save()

        self.manage_url = reverse("goal_manage")

    def test_owner_can_view_goals_page(self):
        self.client.force_login(self.owner)
        resp = self.client.get(self.manage_url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Shared Goals", resp.content)

    def test_owner_can_create_goal(self):
        self.client.force_login(self.owner)
        self.client.post(
            self.manage_url,
            {
                "name": "Save for vacation",
                "target_amount": "2000.00",
            },
            follow=True,
        )

        self.assertTrue(
            Goal.objects.filter(
                group=self.group,
                name="Save for vacation",
                target_amount=Decimal("2000.00"),
            ).exists()
        )

    def test_non_owner_cannot_manage_goals(self):
        self.client.force_login(self.other)
        resp = self.client.get(self.manage_url)
        self.assertEqual(resp.status_code, 403)
