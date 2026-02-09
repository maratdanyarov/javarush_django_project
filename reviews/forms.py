from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator

from .models import Review


class ReviewForm(forms.ModelForm):
    """Form for creating product reviews."""

    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 5}),
    )
    text = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Write your review here...",
            }
        )
    )

    class Meta:
        model = Review
        fields = ["rating", "text"]
