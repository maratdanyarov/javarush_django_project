"""Views для управления корзиной покупок."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.decorators.http import require_POST
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product

from .cart import Cart
from .forms import OrderCreateForm
from .models import Order, OrderItem
from .serializers import OrderSerializer
from .services import send_order_admin_notification, send_order_confirmation_email


class CartView(View):
    """Отображение содержимого корзины."""

    template_name = 'cart.html'

    def get(self, request):
        """
        Отобразить страницу корзины.

        Args:
            request: HTTP запрос

        Returns:
            HttpResponse с отрендеренным шаблоном корзины
        """
        cart = Cart(request)

        # Подготовка данных для шаблона
        cart_items = []
        for item in cart:
            cart_items.append({
                'product': item['product'],
                'quantity': item['quantity'],
                'price': item['price'],
                'total_price': item['total_price'],
            })

        context = {
            'cart_items': cart_items,
            'total_price': cart.get_total_price(),
            'items_count': len(cart),
        }

        return render(request, self.template_name, context)


class OrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart(request)
        if len(cart) == 0:
            return redirect('orders:cart')
        form = OrderCreateForm()
        return render(request, 'checkout.html', {'cart': cart, 'form': form})

    def post(self, request):
        cart = Cart(request)
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():  # Оборачиваем в транзакцию
                    order = form.save(commit=False)
                    order.user = request.user
                    order.total_price = cart.get_total_price()
                    order.save()

                    for item in cart:
                        OrderItem.objects.create(
                            order=order,
                            product=item['product'],
                            price=item['price'],
                            quantity=item['quantity']
                        )
                        # Уменьшаем запас
                        product = item['product']
                        if product.stock < item['quantity']:
                            raise ValueError(f"Not enough stock for {product.name}")
                        product.stock -= item['quantity']
                        product.save()

                    cart.clear()

                    # Send confirmation emails
                    send_order_confirmation_email(order)
                    send_order_admin_notification(order, request)

                    messages.success(request, f'Order #{order.id} created! Confirmation email sent.')
                    return render(request, 'order_created.html', {'order': order})
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
                return redirect('orders:cart')
        return render(request, 'checkout.html', {'cart': cart, 'form': form})


@require_POST
def cart_add(request, product_id: int):
    """
    Добавить товар в корзину (AJAX).

    Args:
        request: HTTP POST запрос
        product_id: ID товара для добавления

    Returns:
        JsonResponse с результатом операции
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    # Получаем количество из POST данных
    quantity = int(request.POST.get('quantity', 1))

    # Добавляем товар в корзину
    result = cart.add(product=product, quantity=quantity)

    if result['status'] == 'success':
        messages.success(request, result['message'])
    else:
        messages.error(request, result['message'])

    # Возвращаем JSON для AJAX запросов
    return JsonResponse({
        'status': result['status'],
        'message': result['message'],
        'cart_items_count': len(cart),
        'cart_total': str(cart.get_total_price()),
    })


@require_POST
def cart_remove(request, product_id: int):
    """
    Удалить товар из корзины.

    Args:
        request: HTTP POST запрос
        product_id: ID товара для удаления

    Returns:
        JsonResponse с результатом или redirect
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    cart.remove(product)
    messages.success(request, f'{product.name} removed from cart')

    # Если это AJAX запрос
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f'{product.name} removed from cart',
            'cart_items_count': len(cart),
            'cart_total': str(cart.get_total_price()),
        })

    # Иначе редирект на страницу корзины
    return redirect('orders:cart')


@require_POST
def cart_update(request, product_id: int):
    """
    Обновить количество товара в корзине.

    Args:
        request: HTTP POST запрос
        product_id: ID товара для обновления

    Returns:
        JsonResponse с результатом
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    # Получаем новое количество
    quantity = int(request.POST.get('quantity', 1))

    # Обновляем количество
    result = cart.update(product=product, quantity=quantity)

    if result['status'] == 'success':
        messages.success(request, result['message'])
    else:
        messages.error(request, result['message'])

    return JsonResponse({
        'status': result['status'],
        'message': result['message'],
        'cart_items_count': len(cart),
        'cart_total': str(cart.get_total_price()),
        'item_total': str(product.price * quantity) if quantity > 0 else '0',
    })

@require_POST
def cart_clear(request):
    """
    Очистить всю корзину.

    Args:
        request: HTTP запрос

    Returns:
        Redirect на страницу корзины
    """
    cart = Cart(request)
    cart.clear()
    messages.success(request, 'Cart cleared')

    return redirect('orders:cart')


class OrderViewSet(viewsets.ModelViewSet):
    """API ViewSet for Order model."""

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartAPIView(APIView):
    """API endpoint for cart management."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Get cart contents."""
        cart = Cart(request)
        items = []
        for item in cart:
            items.append({
                'product_id': item['product'].id,
                'product_name': item['product'].name,
                'quantity': item['quantity'],
                'price': str(item['price']),
                'total_price': str(item['total_price']),
            })
        return Response({
            'items': items,
            'total_price': str(cart.get_total_price()),
            'items_count': len(cart),
        })

    def post(self, request):
        """Add item to cart."""
        cart = Cart(request)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        result = cart.add(product=product, quantity=quantity)
        return Response({
            'status': result['status'],
            'message': result['message'],
            'cart_items_count': len(cart),
            'cart_total': str(cart.get_total_price()),
        })

    def patch(self, request):
        """Update item quantity in cart."""
        cart = Cart(request)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        result = cart.update(product=product, quantity=quantity)
        return Response({
            'status': result['status'],
            'message': result['message'],
            'cart_items_count': len(cart),
            'cart_total': str(cart.get_total_price()),
        })

    def delete(self, request):
        """Remove item from cart or clear cart."""
        cart = Cart(request)
        product_id = request.data.get('product_id')

        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                cart.remove(product)
                return Response({
                    'message': f'{product.name} removed from cart',
                    'cart_items_count': len(cart),
                    'cart_total': str(cart.get_total_price()),
                })
            except Product.DoesNotExist:
                return Response(
                    {'error': 'Product not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            cart.clear()
            return Response({'message': 'Cart cleared'})
