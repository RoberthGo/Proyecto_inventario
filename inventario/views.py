from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.contrib import messages
from .models import Proveedor, Ropa, Color, Inventario


def home(request):
    context = {
        'num_proveedores': Proveedor.objects.all().count(),
    }
    return render(request, 'home.html', context=context)


class ProveedorListView(generic.ListView):
    model = Proveedor
    template_name = 'proveedor_list.html'


class RopaListView(generic.ListView):
    model = Ropa
    template_name = 'ropa_list.html'
    context_object_name = 'ropas'

    def get_queryset(self):
        return Ropa.objects.annotate(
            total_inventario=Coalesce(Sum('inventarios__unidades'), 0)
        ).select_related('proveedor')


def actualizar_inventario(request, pk):
    ropa = get_object_or_404(Ropa, pk=pk)
    colores = Color.objects.all()

    if request.method == 'POST':
        for color in colores:
            campo = f"unidades_{color.id}"
            if campo in request.POST:
                try:
                    valor = int(request.POST.get(campo, 0))
                    valor = max(0, valor)
                except ValueError:
                    valor = 0

                Inventario.objects.update_or_create(
                    ropa=ropa,
                    color=color,
                    defaults={'unidades': valor}
                )
        messages.success(request, f"Inventario de {ropa.modelo} actualizado correctamente.")
        return redirect('productos')

    inventario_actual = {inv.color_id: inv.unidades for inv in ropa.inventarios.all()}
    filas_colores = []
    for color in colores:
        filas_colores.append({
            'color': color,
            'unidades': inventario_actual.get(color.id, 0)
        })

    context = {
        'ropa': ropa,
        'filas_colores': filas_colores,
    }
    return render(request, 'ropa_inventario.html', context)