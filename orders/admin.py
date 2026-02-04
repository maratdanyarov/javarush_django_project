from django.contrib import admin
from django.db.models import Sum

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_price", "created_at", "is_paid")
    list_filter = ("is_paid", "created_at")
    inlines = [OrderItemInline]

    def changelist_view(self, request, extra_context=None):
        aggregate_data = Order.objects.aggregate(total=Sum('total_price'))
        extra_context = extra_context or {}
        extra_context['total_revenue'] = aggregate_data['total']
        return super().changelist_view(request, extra_context=extra_context)
