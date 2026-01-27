from decimal import Decimal

from django.conf import settings
from typing import Dict
from products.models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)

        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}

        self.cart = cart

    def add(self, product: Product, quantity:int = 1, override_quantity:bool = False) -> Dict[str, str]:
        product_id = str(product.id)

        if quantity > product.stock:
            return {
                'status': 'error',
                'message': f'Available stock {product.stock}. Cannot add {quantity} items.'
            }

        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price),
            }

        if override_quantity:
            new_quantity = quantity
        else:
            new_quantity = self.cart[product_id]['quantity'] + quantity

        if new_quantity > product.stock:
            return {
                'status': 'error',
                'message': f'Cannot add more. Maximum available: {product.stock}.'
            }

        self.cart[product_id]['quantity'] = new_quantity
        self.save()

        return {
            'status': 'success',
            'message': f'{product.name} added to cart.'
        }

    def remove(self, product: Product) -> None:
        product_id = str(product.id)

        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def update(self, product: Product, quantity:int) -> Dict[str, str]:
        if quantity <= 0:
            self.remove(product)
            return {
                'status': 'success',
                'message': 'Item removed from cart.'
            }

        return self.add(product, quantity, override_quantity=True)

    def save(self) -> None:
        self.session.modified = True

    def clear(self) -> None:
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self) -> int:
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self) -> Decimal:
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def get_items_count(self):
        return len(self.cart)
