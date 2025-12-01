
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from budget.models import Profile, FamilyGroup

User = get_user_model()


class TestPermissions(TestCase):


    def setUp(self):

        self.owner = User.objects.create_user(username="owner", password="pw12345")
        self.member = User.objects.create_user(username="member", password="pw12345")

        self.owner_profile = Profile.objects.get(user=self.owner)
        self.member_profile = Profile.objects.get(user=self.member)

        self.group = FamilyGroup.objects.create(
            name="Fam",
            code="F123",
            owner=self.owner,
        )

        self.owner_profile.group = self.group
        self.owner_profile.save()

        self.member_profile.group = self.group
        self.member_profile.save()

        
        self.manage_members_url = reverse("group_manage_members")
        self.category_manage_url = reverse("category_manage")
        self.goal_manage_url = reverse("goal_manage")

    def test_owner_can_promote_member_to_admin(self):
      
        self.client.force_login(self.owner)
        self.assertFalse(
            getattr(self.member_profile, "is_admin", False),
            "Member should not be admin before promotion.",
        )

        resp = self.client.post(
            self.manage_members_url,
            {"action": "promote", "member_profile_id": self.member_profile.id},
            follow=True,
        )

        self.assertEqual(resp.status_code, 200)

        self.member_profile.refresh_from_db()
        self.assertTrue(
            getattr(self.member_profile, "is_admin", False),
            "Member should be admin after owner promotes them.",
        )

    def test_owner_can_demote_admin_to_member(self):
      
        setattr(self.member_profile, "is_admin", True)
        self.member_profile.save()

        self.client.force_login(self.owner)

        resp = self.client.post(
            self.manage_members_url,
            {"action": "demote", "member_profile_id": self.member_profile.id},
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)

        self.member_profile.refresh_from_db()
        self.assertFalse(
            getattr(self.member_profile, "is_admin", False),
            "Member should not be admin after owner demotes them.",
        )

    def test_non_owner_cannot_change_permissions(self):
       
        self.client.force_login(self.member)

        resp = self.client.post(
            self.manage_members_url,
            {"action": "promote", "member_profile_id": self.member_profile.id},
            follow=True,
        )


        self.member_profile.refresh_from_db()
        self.assertFalse(
            getattr(self.member_profile, "is_admin", False),
            "Non-owner should not be able to change permissions.",
        )

    def test_admin_can_manage_categories(self):

        setattr(self.member_profile, "is_admin", True)
        self.member_profile.group = self.group
        self.member_profile.save()

        self.client.force_login(self.member)
        resp = self.client.get(self.category_manage_url)
        self.assertEqual(
            resp.status_code,
            200,
            "Admin should be able to access category_manage page.",
        )

    def test_non_admin_member_cannot_manage_categories(self):
        
        self.client.force_login(self.member)
        resp = self.client.get(self.category_manage_url)

       
        self.assertNotEqual(
            resp.status_code,
            200,
            "Non-admin member should NOT be able to access category_manage page.",
        )

    def test_admin_can_manage_goals(self):
       
        setattr(self.member_profile, "is_admin", True)
        self.member_profile.group = self.group
        self.member_profile.save()

        self.client.force_login(self.member)
        resp = self.client.get(self.goal_manage_url)
        self.assertEqual(
            resp.status_code,
            200,
            "Admin should be able to access goal_manage page.",
        )

    def test_non_admin_member_cannot_manage_goals(self):
       
        self.client.force_login(self.member)
        resp = self.client.get(self.goal_manage_url)

        self.assertNotEqual(
            resp.status_code,
            200,
            "Non-admin member should NOT be able to access goal_manage page.",
        )
