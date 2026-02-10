from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, TemplateView
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from orders.models import Order

from .forms import RegisterForm, ProfileUpdateForm
from .serializers import UserRegistrationSerializer, UserSerializer


class RegisterView(CreateView):
    """User registration view."""

    form_class = RegisterForm
    template_name = "register.html"
    success_url = reverse_lazy("users:login")


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view showing account info and order history."""

    template_name = "account.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["orders"] = Order.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )
        context["profile_form"] = ProfileUpdateForm(instance=self.request.user)
        context["password_form"] = PasswordChangeForm(self.request.user)
        return context


class ProfileUpdateView(LoginRequiredMixin, View):
    """View for updating user profile information."""

    def post(self, request):
        form = ProfileUpdateForm(request.POST, instance=self.request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
        else:
            messages.error(request, "Please correct the error below.")
        return redirect("users:profile")


class PasswordChangeView(LoginRequiredMixin, View):
    """View for changing user password."""

    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated successfully")
        else:
            for error in form.errors.values():
                messages.error(request, error)
        return redirect("users:profile")


@require_POST
def logout_view(request):
    logout(request)
    return redirect("home")


# API Views
class RegisterAPIView(generics.CreateAPIView):
    """API endpoint for user registration."""

    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "User registered successfully.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """API endpoint for viewing and updating user profile."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
