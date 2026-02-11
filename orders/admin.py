from django.contrib import admin, messages
from django.db.models import Sum, Count
from django.template.response import TemplateResponse
from django.urls import path

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for Order model with analytics and custom actions."""

    inlines = [OrderItemInline]
    list_display = ("id", "user", "full_name", "total_price", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "full_name", "phone", "city")
    readonly_fields = ("created_at", "updated_at", "total_price")
    list_editable = ("status",)
    date_hierarchy = "created_at"
    change_list_template = "admin/order/order_changelist.html"
    actions = [
        "mark_as_paid",
        "mark_as_shipped",
        "mark_as_delivered",
        "mark_as_cancelled",
    ]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "analytics/",
                self.admin_site.admin_view(self.analytics_view),
                name="orders_analytics",
            ),
        ]
        return custom_urls + urls

    def analytics_view(self, request):
        """Custom admin view for order analytics."""
        # Order statistics by status
        status_stats = (
            Order.objects.values("status")
            .annotate(count=Count("id"), total=Sum("total_price"))
            .order_by("status")
        )

        # Total revenue
        total_revenue = (
            Order.objects.filter(status__in=["paid", "shipped", "delivered"]).aggregate(
                total=Sum("total_price")
            )["total"]
            or 0
        )

        # Orders count
        orders_count = Order.objects.count()

        # Top products by sales
        top_products = (
            OrderItem.objects.values("product__name")
            .annotate(total_quantity=Sum("quantity"), total_revenue=Sum("price"))
            .order_by("-total_quantity")[:10]
        )

        # Recent orders
        recent_orders = Order.objects.select_related("user").order_by("-created_at")[
            :10
        ]

        context = {
            **self.admin_site.each_context(request),
            "title": "Order Analytics",
            "status_stats": status_stats,
            "total_revenue": total_revenue,
            "orders_count": orders_count,
            "top_products": top_products,
            "recent_orders": recent_orders,
        }
        return TemplateResponse(request, "admin/order/analytics.html", context)

    @admin.action(description="Mark selected orders as Paid")
    def mark_as_paid(self, request, queryset):
        updated = queryset.filter(status="pending").update(status="paid")
        self.message_user(
            request, f"{updated} orders marked as paid.", messages.SUCCESS
        )

    @admin.action(description="Mark selected orders as Shipped")
    def mark_as_shipped(self, request, queryset):
        updated = queryset.filter(status="paid").update(status="shipped")
        self.message_user(
            request, f"{updated} orders marked as shipped.", messages.SUCCESS
        )

    @admin.action(description="Mark selected orders as Delivered")
    def mark_as_delivered(self, request, queryset):
        updated = queryset.filter(status="shipped").update(status="delivered")
        self.message_user(
            request, f"{updated} orders marked as delivered.", messages.SUCCESS
        )

    @admin.action(description="Mark selected orders as Cancelled")
    def mark_as_cancelled(self, request, queryset):
        # Only pending orders can be cancelled
        updated = queryset.filter(status="pending").update(status="cancelled")
        self.message_user(
            request, f"{updated} orders marked as cancelled.", messages.SUCCESS
        )
