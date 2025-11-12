from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("", include("budget.urls")),
    path("accounts/logout/", LogoutView.as_view(next_page="/"), name="logout"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
]
