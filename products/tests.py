"""Tests for products app."""

import pytest
from decimal import Decimal

from django.urls import reverse

from products.models import Category, Product


@pytest.mark.django_db
class TestCategoryModel:
    """Tests for Category model."""

    def test_category_creation(self):
        """Test category can be created."""
        category = Category.objects.create(name='Hops', slug='hops')
        assert category.name == 'Hops'
        assert category.slug == 'hops'
        assert str(category) == 'Hops'

    def test_category_auto_slug(self):
        """Test category auto-generates slug from name."""
        category = Category.objects.create(name='Test Category')
        assert category.slug == 'test-category'

    def test_nested_category(self):
        """Test nested categories."""
        parent = Category.objects.create(name='Parent', slug='parent')
        child = Category.objects.create(name='Child', slug='child', parent=parent)
        assert child.parent == parent


@pytest.mark.django_db
class TestProductModel:
    """Tests for Product model."""

    def test_product_creation(self, category):
        """Test product can be created."""
        product = Product.objects.create(
            name='Test Hops',
            slug='test-hops',
            category=category,
            description='Test description',
            price=Decimal('15.99'),
            stock=50,
            is_active=True
        )
        assert product.name == 'Test Hops'
        assert product.price == Decimal('15.99')
        assert product.stock == 50
        assert str(product) == 'Test Hops'

    def test_product_auto_slug(self, category):
        """Test product auto-generates slug from name."""
        product = Product.objects.create(
            name='Auto Slug Product',
            category=category,
            description='Test',
            price=Decimal('10.00'),
            stock=10
        )
        assert product.slug == 'auto-slug-product'

    def test_product_average_rating(self, product, user):
        """Test product average rating calculation."""
        from reviews.models import Review
        Review.objects.create(product=product, user=user, rating=4, text='Good')
        assert product.average_rating == 4.0


@pytest.mark.django_db
class TestProductListView:
    """Tests for ProductListView."""

    def test_product_list_view(self, client, product):
        """Test product list page loads."""
        response = client.get(reverse('products'))
        assert response.status_code == 200
        assert 'products' in response.context

    def test_product_list_with_category_filter(self, client, product, category):
        """Test product list filters by category."""
        response = client.get(reverse('products'), {'category': category.slug})
        assert response.status_code == 200

    def test_product_list_sorting(self, client, product):
        """Test product list sorting."""
        response = client.get(reverse('products'), {'sort': 'price'})
        assert response.status_code == 200

    def test_product_list_search(self, client, product):
        """Test product list search."""
        response = client.get(reverse('products'), {'search': 'Test'})
        assert response.status_code == 200


@pytest.mark.django_db
class TestProductDetailView:
    """Tests for ProductDetailView."""

    def test_product_detail_view(self, client, product):
        """Test product detail page loads."""
        response = client.get(reverse('product_detail', kwargs={'slug': product.slug}))
        assert response.status_code == 200
        assert response.context['product'] == product

    def test_product_detail_404(self, client):
        """Test product detail returns 404 for non-existent product."""
        response = client.get(reverse('product_detail', kwargs={'slug': 'non-existent'}))
        assert response.status_code == 404


@pytest.mark.django_db
class TestProductAPI:
    """Tests for Product API."""

    def test_product_list_api(self, api_client, product):
        """Test product list API endpoint."""
        response = api_client.get('/api/products/')
        assert response.status_code == 200
        assert len(response.data['results']) >= 1

    def test_product_detail_api(self, api_client, product):
        """Test product detail API endpoint."""
        response = api_client.get(f'/api/products/{product.id}/')
        assert response.status_code == 200
        assert response.data['name'] == product.name

    def test_product_search_api(self, api_client, product):
        """Test product search API."""
        response = api_client.get('/api/products/', {'search': 'Test'})
        assert response.status_code == 200

    def test_product_filter_by_category_api(self, api_client, product, category):
        """Test product filter by category API."""
        response = api_client.get('/api/products/', {'category': category.id})
        assert response.status_code == 200
