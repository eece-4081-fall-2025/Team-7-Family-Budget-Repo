from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class FamilyGroup(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=32, unique=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_groups"
    )

    def __str__(self):
        return self.name

    def members_qs(self):
        return (
            User.objects.filter(profile__group=self)
            .select_related("profile")
            .order_by("username")
        )

    def role_of(self, user):
        if self.owner_id == getattr(user, "id", None):
            return "Admin"
        return "Member"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    group = models.ForeignKey(
        FamilyGroup, null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"Profile({self.user.username})"
