from django.views.generic import TemplateView, ListView, DetailView
from .models import Product, Category

# Create your views here.
class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.filter(is_active=True)[:5]
        return context


class ProductListView(ListView):
    model = Product
    template_name = 'products.html'
    context_object_name = 'products'
    queryset = Product.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product-{slug}.html'
    slug_field = 'slug'
    context_object_name = 'product'

    def get_template_names(self):
        return [f"product-{self.object.slug}.html"]
