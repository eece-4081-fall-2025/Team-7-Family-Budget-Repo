from typing import Iterable, Dict, Any
from django.contrib.auth import get_user_model
from .models import Profile, FamilyGroup

User = get_user_model()


def get_profile(user: User) -> Profile:
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


def can_join_or_create_group(profile: Profile) -> bool:
    return profile.group_id is None


def attach_profile_to_group(profile: Profile, group: FamilyGroup) -> Profile:
    profile.group = group
    profile.save()
    return profile


def detach_profile_from_group(profile: Profile) -> Profile:
    profile.group = None
    profile.save()
    return profile


def iter_group_members(group: FamilyGroup) -> Iterable[User]:
    return group.members_qs()


def member_dto(user: User, group: FamilyGroup) -> Dict[str, Any]:
    profile = getattr(user, "profile", None)
    income = getattr(profile, "income", 0) if profile else 0
    expenses = getattr(profile, "expenses", 0) if profile else 0
    return {
        "username": user.username,
        "role": group.role_of(user),
        "income": income,
        "expenses": expenses,
    }


def build_members_list(group: FamilyGroup) -> Iterable[Dict[str, Any]]:
    users = iter_group_members(group)
    return [member_dto(u, group) for u in users]
