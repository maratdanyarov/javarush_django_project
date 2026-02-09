from django.urls import path

from .views import ReviewCreateView

urlpatterns = [
    path(
        "product/<slug:slug>/review/", ReviewCreateView.as_view(), name="review_create"
    ),
]
