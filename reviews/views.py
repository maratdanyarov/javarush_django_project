from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from orders.models import Order
from products.models import Product

from .forms import ReviewForm
from .models import Review


class ReviewCreateView(LoginRequiredMixin, View):
    """View for creating product reviews.

    Only allows users who have purchased the product to create a review.
    Users can only leave one review per product.
    """

    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug)

        existing_review = Review.objects.filter(
            product=product, user=request.user
        ).exists()

        if existing_review:
            messages.error(request, "You have already reviewed this product.")
            return redirect("product_detail", slug=slug)

        has_purchased = Order.objects.filter(
            user=request.user,
            items__product=product,
            status__in=["paid", "shipped", "delivered"],
        ).exists()

        if not has_purchased:
            messages.error(
                request, "You can only leave a review for products you have purchased."
            )
            return redirect("product_detail", slug=slug)

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Your review has been submitted.")
        else:
            messages.error(request, "Please correct errors below.")

        return redirect("product_detail", slug=slug)
