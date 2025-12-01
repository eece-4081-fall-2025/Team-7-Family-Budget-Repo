from decimal import Decimal
from django.contrib.auth import get_user_model
from .models import Profile, FamilyGroup

User = get_user_model()


def get_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


def can_join_or_create_group(profile):
    return profile.group is None


def attach_profile_to_group(profile, group):
    profile.group = group
    profile.save(update_fields=["group"])


def remove_profile_from_group(profile):
    profile.group = None
    profile.save(update_fields=["group"])


def add_user_to_group_by_username(username, group):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return None

    profile = get_profile(user)
    if can_join_or_create_group(profile):
        attach_profile_to_group(profile, group)
    return profile


def member_dto(profile, group):
    user = profile.user
    income = profile.income or Decimal("0")
    expenses = profile.expenses or Decimal("0")
    display_name = profile.nickname or user.username

    return {
        "profile_id": profile.pk,
        "username": user.username,
        "display_name": display_name,
        "role": group.role_of(user),
        "income": income,
        "expenses": expenses,
    }


def build_members_list(group):
    profiles = (
        Profile.objects.filter(group=group)
        .select_related("user")
        .order_by("user__username")
    )
    return [member_dto(p, group) for p in profiles]
