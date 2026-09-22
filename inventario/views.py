from django.shortcuts import render
from .models import Proveedor
from django.views import generic

def home(request):
    context = {
        'num_proveedores': Proveedor.objects.all().count(),
    }
    return render(request, 'home.html', context=context)

class ProveedorListView(generic.ListView):
    model = Proveedor
    template_name = 'proveedor_list.html'