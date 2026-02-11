from django.urls import path

from .views import (
    HomeView,
    GuidesRecipesView,
    ProductDetailView,
    ProductListView,
    CommunityView,
    ResourcesView,
    ContactView,
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('products/', ProductListView.as_view(), name='products'),                
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),  
    path('guides-recipes/', GuidesRecipesView.as_view(), name='guides_recipes'),
    path('community/', CommunityView.as_view(), name='community'),
    path('resources/', ResourcesView.as_view(), name='resources'),

    path('contact/', ContactView.as_view(), name='contact'),
]
