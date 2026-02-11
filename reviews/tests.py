"""Tests for reviews app."""

import pytest

from django.urls import reverse

from reviews.models import Review


@pytest.mark.django_db
class TestReviewModel:
    """Tests for Review model."""

    def test_review_creation(self, user, product):
        """Test review can be created."""
        review = Review.objects.create(
            product=product,
            user=user,
            rating=5,
            text='Excellent product!'
        )
        assert review.rating == 5
        assert review.text == 'Excellent product!'
        assert review.product == product
        assert review.user == user

    def test_review_str(self, user, product):
        """Test review string representation."""
        review = Review.objects.create(
            product=product,
            user=user,
            rating=4,
            text='Good'
        )
        assert str(review) == f'Review by {user} for {product.name}: 4/5'

    def test_review_unique_constraint(self, user, product):
        """Test user can only review a product once."""
        Review.objects.create(
            product=product,
            user=user,
            rating=5,
            text='First review'
        )

        with pytest.raises(Exception):  # IntegrityError
            Review.objects.create(
                product=product,
                user=user,
                rating=4,
                text='Second review'
            )


@pytest.mark.django_db
class TestReviewCreateView:
    """Tests for review creation view."""

    def test_review_requires_login(self, client, product):
        """Test review creation requires authentication."""
        response = client.post(
            reverse('review_create', kwargs={'slug': product.slug}),
            {'rating': 5, 'text': 'Great!'}
        )
        assert response.status_code == 302  # Redirect to login

    def test_review_requires_purchase(self, client, user, product):
        """Test user must have purchased product to review."""
        client.force_login(user)
        response = client.post(
            reverse('review_create', kwargs={'slug': product.slug}),
            {'rating': 5, 'text': 'Great!'}
        )
        # Should redirect with error message
        assert response.status_code == 302
        assert not Review.objects.filter(product=product, user=user).exists()

    def test_review_success_after_purchase(self, client, user, product, order):
        """Test user can review after purchasing."""
        client.force_login(user)
        response = client.post(
            reverse('review_create', kwargs={'slug': product.slug}),
            {'rating': 5, 'text': 'Great product!'}
        )
        assert response.status_code == 302
        assert Review.objects.filter(product=product, user=user).exists()

    def test_duplicate_review_prevented(self, client, user, product, order, review):
        """Test user cannot review same product twice."""
        client.force_login(user)
        response = client.post(
            reverse('review_create', kwargs={'slug': product.slug}),
            {'rating': 4, 'text': 'Another review'}
        )
        assert response.status_code == 302
        # Should still only have one review
        assert Review.objects.filter(product=product, user=user).count() == 1


@pytest.mark.django_db
class TestReviewAPI:
    """Tests for Review API."""

    def test_get_product_reviews(self, api_client, product, review):
        """Test getting reviews for a product."""
        response = api_client.get(f'/api/products/{product.id}/reviews/')
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['rating'] == review.rating

    def test_create_review_requires_auth(self, api_client, product):
        """Test review creation requires authentication."""
        response = api_client.post(f'/api/products/{product.id}/reviews/', {
            'rating': 5,
            'text': 'Great!'
        })
        assert response.status_code == 401

    def test_create_review_requires_purchase(self, authenticated_client, product):
        """Test review creation requires purchase."""
        response = authenticated_client.post(f'/api/products/{product.id}/reviews/', {
            'rating': 5,
            'text': 'Great!'
        })
        assert response.status_code == 403

    def test_create_review_success(self, authenticated_client, product, order):
        """Test successful review creation via API."""
        response = authenticated_client.post(f'/api/products/{product.id}/reviews/', {
            'rating': 5,
            'text': 'Excellent!'
        })
        assert response.status_code == 201
        assert response.data['rating'] == 5
