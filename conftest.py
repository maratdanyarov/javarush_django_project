"""Pytest fixtures for all tests."""

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from products.models import Category, Product
from orders.models import Order, OrderItem
from reviews.models import Review

User = get_user_model()


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        phone='1234567890'
    )


@pytest.fixture
def category(db):
    """Create a test category."""
    return Category.objects.create(
        name='Test Category',
        slug='test-category'
    )


@pytest.fixture
def product(db, category):
    """Create a test product."""
    return Product.objects.create(
        name='Test Product',
        slug='test-product',
        category=category,
        description='Test description',
        price=Decimal('19.99'),
        stock=100,
        is_active=True
    )


@pytest.fixture
def product_out_of_stock(db, category):
    """Create an out-of-stock product."""
    return Product.objects.create(
        name='Out of Stock Product',
        slug='out-of-stock',
        category=category,
        description='No stock',
        price=Decimal('9.99'),
        stock=0,
        is_active=True
    )


@pytest.fixture
def order(db, user, product):
    """Create a test order with items."""
    order = Order.objects.create(
        user=user,
        full_name='Test User',
        phone='1234567890',
        city='Test City',
        address='123 Test St',
        total_price=Decimal('19.99'),
        status='paid'  # Paid status allows for reviews
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=product.price
    )
    return order


@pytest.fixture
def review(db, user, product):
    """Create a test review."""
    return Review.objects.create(
        product=product,
        user=user,
        rating=5,
        text='Great product!'
    )


@pytest.fixture
def api_client():
    """Create an API client."""
    return APIClient()


@pytest.fixture
def authenticated_client(db, user):
    """Create an authenticated API client with JWT token."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client
