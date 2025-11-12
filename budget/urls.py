from django.urls import path
from .views import SignupView, home, dashboard

urlpatterns = [
    path("", home, name="budget_home"),
    path("signup/", SignupView.as_view(), name="budget_signup"),
    path("dashboard/", dashboard, name="budget_dashboard"),
]
