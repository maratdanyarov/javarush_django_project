"""Tests for users app."""

import pytest

from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Tests for User model."""

    def test_user_creation(self):
        """Test user can be created."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            phone='1234567890'
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.phone == '1234567890'
        assert user.check_password('testpass123')

    def test_superuser_creation(self):
        """Test superuser can be created."""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        assert admin.is_superuser
        assert admin.is_staff


@pytest.mark.django_db
class TestRegistration:
    """Tests for user registration."""

    def test_registration_view_loads(self, client):
        """Test registration page loads."""
        response = client.get(reverse('users:register'))
        assert response.status_code == 200

    def test_registration_success(self, client):
        """Test successful user registration."""
        response = client.post(reverse('users:register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpass123!',
            'password2': 'complexpass123!',
            'phone': '9876543210'
        })
        assert response.status_code == 302  # Redirect on success
        assert User.objects.filter(username='newuser').exists()

    def test_registration_password_mismatch(self, client):
        """Test registration fails with password mismatch."""
        response = client.post(reverse('users:register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpass123!',
            'password2': 'differentpass123!',
        })
        assert response.status_code == 200  # Form re-rendered
        assert not User.objects.filter(username='newuser').exists()


@pytest.mark.django_db
class TestLogin:
    """Tests for user login."""

    def test_login_view_loads(self, client):
        """Test login page loads."""
        response = client.get(reverse('users:login'))
        assert response.status_code == 200

    def test_login_success(self, client, user):
        """Test successful login."""
        response = client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        assert response.status_code == 302  # Redirect on success

    def test_login_invalid_credentials(self, client, user):
        """Test login fails with invalid credentials."""
        response = client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        assert response.status_code == 200  # Form re-rendered


@pytest.mark.django_db
class TestProfile:
    """Tests for user profile."""

    def test_profile_requires_login(self, client):
        """Test profile page requires authentication."""
        response = client.get(reverse('users:profile'))
        assert response.status_code == 302  # Redirect to login

    def test_profile_view(self, client, user):
        """Test authenticated user can view profile."""
        client.force_login(user)
        response = client.get(reverse('users:profile'))
        assert response.status_code == 200

    def test_profile_shows_orders(self, client, user, order):
        """Test profile shows user's orders."""
        client.force_login(user)
        response = client.get(reverse('users:profile'))
        assert response.status_code == 200
        assert 'orders' in response.context

    def test_profile_update(self, client, user):
        """Test profile can be updated."""
        client.force_login(user)
        response = client.post(reverse('users:profile_update'), {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'phone': '9999999999'
        })
        assert response.status_code == 302  # Redirect on success

        user.refresh_from_db()
        assert user.first_name == 'Updated'


@pytest.mark.django_db
class TestUserAPI:
    """Tests for User API."""

    def test_register_api(self, api_client):
        """Test user registration API."""
        response = api_client.post('/api/users/register/', {
            'username': 'apiuser',
            'email': 'api@example.com',
            'password': 'apipass123!',
            'password2': 'apipass123!'
        })
        assert response.status_code == 201
        assert User.objects.filter(username='apiuser').exists()

    def test_register_api_password_mismatch(self, api_client):
        """Test API registration fails with password mismatch."""
        response = api_client.post('/api/users/register/', {
            'username': 'apiuser',
            'email': 'api@example.com',
            'password': 'apipass123!',
            'password2': 'differentpass!'
        })
        assert response.status_code == 400

    def test_profile_api_requires_auth(self, api_client):
        """Test profile API requires authentication."""
        response = api_client.get('/api/users/profile/')
        assert response.status_code == 401

    def test_profile_api_authenticated(self, authenticated_client, user):
        """Test authenticated user can view profile via API."""
        response = authenticated_client.get('/api/users/profile/')
        assert response.status_code == 200
        assert response.data['username'] == user.username

    def test_jwt_token_obtain(self, api_client, user):
        """Test JWT token can be obtained."""
        response = api_client.post('/api/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_jwt_token_refresh(self, api_client, user):
        """Test JWT token can be refreshed."""
        # First get tokens
        token_response = api_client.post('/api/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        refresh_token = token_response.data['refresh']

        # Then refresh
        response = api_client.post('/api/token/refresh/', {
            'refresh': refresh_token
        })
        assert response.status_code == 200
        assert 'access' in response.data
