from django.contrib import admin

from .models import Review


# Register your models here.
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('product', 'user', 'rating')
    search_fields = ('product__name', 'user__username', 'comment')
