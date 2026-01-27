from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.http import require_POST

from products.models import Product
from .cart import Cart
from .forms import OrderCreateForm
from .models import OrderItem


# Create your views here.
class CartView(View):
    template_name = 'cart.html'

    def get(self, request):
        cart = Cart(request)

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
            'items_count': cart.get_items_count(),
        }

        return render(request, self.template_name, context)


class OrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart(request)
        if len(cart) == 0:
            return redirect('orders:cart')
        form = OrderCreateForm(request.POST)
        return render(request, 'checkout.html', {'cart': cart, 'form': form})

    def post(self, request):
        cart = Cart(request)
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = cart.get_total_price()
            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                )
                product = item['product']
                product.stock -= item['quantity']
                product.save()

            cart.clear()
            messages.success(request, f'Order #{order.id} created.')
            return render(request, 'order_created.html', {'order': order})

        return render(request, 'checkout.html', {'cart': cart, 'form': form})


@require_POST
def cart_add(request, product_id: int):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    quantity = int(request.POST.get('quantity', 1))

    result = cart.add(product=product, quantity=quantity)

    if result['status'] == 'success':
        messages.success(request, result['message'])
    else:
        messages.error(request, result['message'])

    return JsonResponse({
        'status': result['status'],
        'message': result['message'],
        'cart_items_count': cart.get_items_count(),
        'cart_total': str(cart.get_total_price()),
    })


@require_POST
def cart_remove(request, product_id: int):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    cart.remove(product=product)
    messages.success(request, f'{product.name} removed from cart.')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f'{product.name} removed from cart.',
            'cart_items_count': cart.get_items_count(),
            'cart_total': str(cart.get_total_price()),
        })

    return redirect('orders:cart')


@require_POST
def cart_update(request, product_id: int):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    quantity = int(request.POST.get('quantity', 1))

    result = cart.update(product=product, quantity=quantity)

    if result['status'] == 'success':
        messages.success(request, result['message'])
    else:
        messages.error(request, result['message'])

    return JsonResponse({
        'status': result['status'],
        'message': result['message'],
        'cart_items_count': cart.get_items_count(),
        'cart_total': str(cart.get_total_price()),
        'item_total': str(product.price * quantity) if quantity > 0 else '0',
    })

def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    messages.success(request, 'Cart cleared.')

    return redirect('orders:cart')
