from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class FamilyGroup(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=12, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_groups")

    def members_qs(self):
        return Profile.objects.filter(group=self)

    def role_of(self, user):
        return "Admin" if self.owner_id == user.id else "Member"

    def __str__(self):
        return self.name

class ProfileManager(models.Manager):
    def get(self, *args, **kwargs):

        try:
            return super().get(*args, **kwargs)
        except self.model.DoesNotExist:
            user = kwargs.get("user")
            if isinstance(user, User):
                return self.create(user=user)
            raise


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    group = models.ForeignKey(FamilyGroup, on_delete=models.SET_NULL, null=True, blank=True)
    nickname = models.CharField(max_length=50, blank=True, default="") 
    is_admin = models.BooleanField(default=False)

    objects = ProfileManager()

    def __str__(self):
        return self.nickname or self.user.username

class Category(models.Model):
    group = models.ForeignKey(
        FamilyGroup,
        on_delete=models.CASCADE,
        related_name="categories",
    )
    name = models.CharField(max_length=100)
 
    budget_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.name} ({self.group.name})"
class Goal(models.Model):
    group = models.ForeignKey(
        FamilyGroup,
        on_delete=models.CASCADE,
        related_name="goals",
    )
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.group.name})"


