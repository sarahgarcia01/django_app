from django.views.generic import ListView
from .models import Product

class ProductListView(ListView):
    model = Product
    template_name = 'website/index.html'
    context_object_name = 'products'

