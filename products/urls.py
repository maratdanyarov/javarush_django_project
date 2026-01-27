from django.urls import path
from .views import HomeView, ProductListView, ProductDetailView, GuidesRecipesView



urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('products/', ProductListView.as_view(), name='products'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('guides-recipes/', GuidesRecipesView.as_view(), name='guides_recipes'),
]