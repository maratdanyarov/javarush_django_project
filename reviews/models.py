from django.conf import settings
from django.db import models

from products.models import Product

User = settings.AUTH_USER_MODEL


# Create your models here.
class Review(models.Model):
    """Product review model with rating (1-5) and text."""

    product = models.ForeignKey(
        Product, related_name="reviews", on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["product", "user"]

    def __str__(self):
        return f"Review by {self.user} for {self.product.name}: {self.rating}/5"
