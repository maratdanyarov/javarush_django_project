from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import RegisterForm


# Create your views here.
class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')