from decimal import Decimal
from .models import Profile, FamilyGroup


def get_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


def can_join_or_create_group(profile):
    return profile.group is None


def attach_profile_to_group(profile, group):
    profile.group = group
    profile.save(update_fields=["group"])


def member_dto(profile, group):
    user = profile.user
    income = profile.income if profile.income is not None else Decimal("0")
    expenses = profile.expenses if profile.expenses is not None else Decimal("0")
    display_name = profile.nickname or user.username
    return {
        "username": user.username,
        "display_name": display_name,
        "role": group.role_of(user),
        "income": income,
        "expenses": expenses,
    }


def build_members_list(group):
    profiles = Profile.objects.filter(group=group).select_related("user").order_by(
        "user__username"
    )
    return [member_dto(p, group) for p in profiles]
