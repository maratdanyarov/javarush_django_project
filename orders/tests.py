"""Tests for orders app."""

import pytest
from decimal import Decimal

from django.urls import reverse

from orders.models import Order, OrderItem
from orders.cart import Cart


@pytest.mark.django_db
class TestOrderModel:
    """Tests for Order model."""

    def test_order_creation(self, user):
        """Test order can be created."""
        order = Order.objects.create(
            user=user,
            full_name='Test User',
            phone='1234567890',
            city='Test City',
            address='123 Test St',
            total_price=Decimal('50.00'),
            status='pending'
        )
        assert order.user == user
        assert order.status == 'pending'
        assert str(order) == f'Order #{order.id} by {user}'

    def test_order_status_choices(self, user):
        """Test order status choices."""
        order = Order.objects.create(
            user=user,
            full_name='Test',
            total_price=Decimal('10.00')
        )
        assert order.status == 'pending'

        order.status = 'paid'
        order.save()
        assert order.is_paid is True

    def test_order_is_paid_property(self, user):
        """Test order is_paid property."""
        order = Order.objects.create(
            user=user,
            full_name='Test',
            total_price=Decimal('10.00'),
            status='paid'
        )
        assert order.is_paid is True

        order.status = 'pending'
        order.save()
        assert order.is_paid is False


@pytest.mark.django_db
class TestOrderItemModel:
    """Tests for OrderItem model."""

    def test_order_item_creation(self, order, product):
        """Test order item can be created."""
        item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=2,
            price=product.price
        )
        assert item.quantity == 2
        assert item.price == product.price
        assert str(item) == f'{product.name} x 2'


@pytest.mark.django_db
class TestCart:
    """Tests for Cart session functionality."""

    def test_cart_add_product(self, client, product):
        """Test adding product to cart."""
        session = client.session
        cart = Cart(client)

        result = cart.add(product, quantity=1)
        assert result['status'] == 'success'

    def test_cart_add_exceeds_stock(self, client, product):
        """Test adding more than stock available."""
        cart = Cart(client)

        result = cart.add(product, quantity=1000)
        assert result['status'] == 'error'
        assert 'stock' in result['message'].lower()

    def test_cart_remove_product(self, client, product):
        """Test removing product from cart."""
        cart = Cart(client)
        cart.add(product, quantity=1)
        cart.remove(product)

        assert len(cart) == 0

    def test_cart_update_quantity(self, client, product):
        """Test updating cart item quantity."""
        cart = Cart(client)
        cart.add(product, quantity=1)

        result = cart.update(product, quantity=3)
        assert result['status'] == 'success'

    def test_cart_clear(self, client, product):
        """Test clearing cart."""
        cart = Cart(client)
        cart.add(product, quantity=2)
        cart.clear()

        assert len(cart) == 0

    def test_cart_total_price(self, client, product):
        """Test cart total price calculation."""
        cart = Cart(client)
        cart.add(product, quantity=2)

        expected_total = product.price * 2
        assert cart.get_total_price() == expected_total


@pytest.mark.django_db
class TestCartViews:
    """Tests for cart views."""

    def test_cart_view(self, client):
        """Test cart page loads."""
        response = client.get(reverse('orders:cart'))
        assert response.status_code == 200

    def test_cart_add_view(self, client, product):
        """Test adding to cart via AJAX."""
        response = client.post(
            reverse('orders:cart_add', kwargs={'product_id': product.id}),
            {'quantity': 1}
        )
        assert response.status_code == 200
        assert response.json()['status'] == 'success'

    def test_cart_add_out_of_stock(self, client, product_out_of_stock):
        """Test adding out of stock product."""
        response = client.post(
            reverse('orders:cart_add', kwargs={'product_id': product_out_of_stock.id}),
            {'quantity': 1}
        )
        assert response.status_code == 200
        assert response.json()['status'] == 'error'


@pytest.mark.django_db
class TestCheckout:
    """Tests for checkout functionality."""

    def test_checkout_requires_login(self, client):
        """Test checkout requires authentication."""
        response = client.get(reverse('orders:checkout'))
        assert response.status_code == 302  # Redirect to login

    def test_checkout_view(self, client, user, product):
        """Test checkout page loads for authenticated user."""
        client.force_login(user)

        # Add item to cart first
        client.post(
            reverse('orders:cart_add', kwargs={'product_id': product.id}),
            {'quantity': 1}
        )

        response = client.get(reverse('orders:checkout'))
        assert response.status_code == 200

    def test_checkout_empty_cart_redirect(self, client, user):
        """Test checkout redirects if cart is empty."""
        client.force_login(user)
        response = client.get(reverse('orders:checkout'))
        assert response.status_code == 302  # Redirect to cart


@pytest.mark.django_db
class TestOrderAPI:
    """Tests for Order API."""

    def test_order_list_requires_auth(self, api_client):
        """Test order list requires authentication."""
        response = api_client.get('/api/orders/')
        assert response.status_code == 401

    def test_order_list_authenticated(self, authenticated_client, order):
        """Test authenticated user can list their orders."""
        response = authenticated_client.get('/api/orders/')
        assert response.status_code == 200

    def test_order_detail_authenticated(self, authenticated_client, order):
        """Test authenticated user can view their order."""
        response = authenticated_client.get(f'/api/orders/{order.id}/')
        assert response.status_code == 200
        assert response.data['id'] == order.id


@pytest.mark.django_db
class TestCartAPI:
    """Tests for Cart API."""

    def test_cart_get(self, api_client):
        """Test getting cart contents."""
        response = api_client.get('/api/cart/')
        assert response.status_code == 200
        assert 'items' in response.data

    def test_cart_add_api(self, api_client, product):
        """Test adding item to cart via API."""
        response = api_client.post('/api/cart/', {
            'product_id': product.id,
            'quantity': 1
        })
        assert response.status_code == 200

    def test_cart_delete_api(self, api_client, product):
        """Test clearing cart via API."""
        response = api_client.delete('/api/cart/')
        assert response.status_code == 200
