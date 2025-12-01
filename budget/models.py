from django.db import models
from django.contrib.auth.models import User

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

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    group = models.ForeignKey(FamilyGroup, on_delete=models.SET_NULL, null=True, blank=True)
    nickname = models.CharField(max_length=50, blank=True, default="")  # <-- NEW

    def __str__(self):
        return self.nickname or self.user.username

class Category(models.Model):

    group = models.ForeignKey(
        FamilyGroup,
        related_name="categories",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("group", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.group.name})"