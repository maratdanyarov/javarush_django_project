from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    # Просмотр корзины
    path('cart/', views.CartView.as_view(), name='cart'),

    # Добавление товара в корзину
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),

    # Удаление товара из корзины
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),

    # Обновление количества товара
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),

    # Очистка корзины
    path('cart/clear/', views.cart_clear, name='cart_clear'),

    path('checkout/', views.OrderCreateView.as_view(), name='checkout'),
]
