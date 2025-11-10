from django.urls import path
from .views import SignupView, home

urlpatterns = [
    path("", home, name="budget_home"),
    path("signup/", SignupView.as_view(), name="budget_signup"),
]
