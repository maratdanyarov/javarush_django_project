from django.db.models import Q, QuerySet, Count, Avg
from django.views.generic import DetailView, ListView, TemplateView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from orders.models import Order
from reviews.models import Review
from .models import Category, Product
from .serializers import ProductSerializer, ReviewSerializer


class HomeView(TemplateView):
    """Homepage view with featured products."""

    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.filter(is_active=True)[:5]  # 5 активных продуктов для главной
        return context


class ProductListView(ListView):
    """Product listing view with filtering and sorting."""

    model = Product
    template_name = "products.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).annotate(
            review_count=Count("reviews"), avg_rating=Avg("reviews__rating")
        )

        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(name__icontains=search)

        sort = self.request.GET.get("sort", "-created_at")
        valid_sorts = {
            "price": "price",
            "-price": "-price",
            "name": "name",
            "-name": "-name",
            "created_at": "created_at",
            "-created_at": "-created_at",
            "popularity": "-review_count",
            "rating": "-avg_rating",
        }
        if sort in valid_sorts:
            queryset = queryset.order_by(valid_sorts[sort])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["current_category"] = self.request.GET.get("category", "")
        context["current_sort"] = self.request.GET.get("sort", "-created_at")
        context["search_query"] = self.request.GET.get("search", "")
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = "product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        user = self.request.user

        if user.is_authenticated:
            has_reviewed = Review.objects.filter(product=product, user=user).exists()

            has_purchased = Order.objects.filter(
                user=user,
                items__product=product,
                status__in=["paid", "shipped", "delivered"],
            ).exists()

            context["has_reviewed"] = has_reviewed
            context["can_review"] = has_purchased and not has_reviewed
        else:
            context["has_reviewed"] = False
            context["can_review"] = False

        return context


class GuidesRecipesView(TemplateView):
    template_name = 'guides-recipes.html'


class ProductViewSet(viewsets.ModelViewSet):
    """API ViewSet for Product model with reviews support."""

    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    filterset_fields = ["category", "price", "is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "name", "created_at"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["get", "post"], url_path="reviews")
    def reviews(self, request, pk=None):
        """Get or create reviews for a product."""
        product = self.get_object()

        if request.method == "GET":
            reviews = product.reviews.all()
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data)

        elif request.method == "POST":
            if not request.user.is_authenticated:
                return Response(
                    {"error": "Authentication required"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Check if user already reviewed
            if Review.objects.filter(product=product, user=request.user).exists():
                return Response(
                    {"error": "You have already reviewed this product"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            has_purchased = Order.objects.filter(
                user=request.user,
                items__product=product,
                status__in=["paid", "shipped", "delivered"],
            ).exists()

            if not has_purchased:
                return Response(
                    {"error": "You can only review products you have purchased"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = ReviewSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, product=product)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
