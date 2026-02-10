from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import ProfileView, RegisterView, ProfileUpdateView, PasswordChangeView

app_name = 'users'

urlpatterns = [
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile_update"),
    path("profile/password/", PasswordChangeView.as_view(), name="password_change"),
]
