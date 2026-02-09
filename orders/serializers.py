from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.ReadOnlyField(source="user.username")
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "full_name",
            "phone",
            "city",
            "address",
            "total_price",
            "status",
            "status_display",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "total_price", "created_at", "updated_at"]
