from decimal import Decimal

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import F
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.contrib import messages
from .forms import RopaForm, VentaForm, VentaItemFormSet
from .models import Cliente, DetalleVenta, Proveedor, Ropa, Venta, Color, Inventario


ROL_ALMACENISTA = 'Almacenista'
ROL_CAJERO = 'Cajero'


def es_administrador(user):
    return user.is_authenticated and (
        user.is_superuser
        or user.is_staff
        or user.groups.filter(name='Administrador').exists()
    )


def puede_actualizar_inventario(user):
    return es_administrador(user) or (
        user.is_authenticated and user.groups.filter(name=ROL_ALMACENISTA).exists()
    )


def puede_vender(user):
    return es_administrador(user) or (
        user.is_authenticated and user.groups.filter(name=ROL_CAJERO).exists()
    )


@login_required
def home(request):
    context = {
        'num_proveedores': Proveedor.objects.all().count(),
    }
    return render(request, 'home.html', context=context)


class ProveedorListView(LoginRequiredMixin, generic.ListView):
    model = Proveedor
    template_name = 'proveedor_list.html'


class ClienteListView(LoginRequiredMixin, generic.ListView):
    model = Cliente
    template_name = 'cliente_list.html'
    queryset = Cliente.objects.order_by('nombre')


class ColorListView(LoginRequiredMixin, generic.ListView):
    model = Color
    template_name = 'color_list.html'
    queryset = Color.objects.order_by('descripcion')


class RopaListView(LoginRequiredMixin, generic.ListView):
    model = Ropa
    template_name = 'ropa_list.html'
    context_object_name = 'ropas'

    def get_queryset(self):
        return Ropa.objects.annotate(
            total_inventario=Coalesce(Sum('inventarios__unidades'), 0)
        ).select_related('proveedor')


class RopaCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = Ropa
    form_class = RopaForm
    template_name = 'ropa_form.html'
    success_url = reverse_lazy('productos')

    def test_func(self):
        return es_administrador(self.request.user)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Solo los administradores pueden agregar ropa.')
        return super().handle_no_permission()

    def form_valid(self, form):
        messages.success(self.request, 'La prenda se agregó correctamente.')
        return super().form_valid(form)


@login_required
@user_passes_test(puede_actualizar_inventario)
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


def obtener_publico_general():
    cliente, _ = Cliente.objects.get_or_create(nombre='Público general')
    return cliente


@login_required
@user_passes_test(puede_vender)
def registrar_venta(request):
    publico_general = obtener_publico_general()
    clientes = Cliente.objects.order_by('nombre')
    inventarios = Inventario.objects.filter(unidades__gt=0).select_related('ropa', 'color')

    venta_form = VentaForm(
        request.POST or None,
        clientes=clientes,
        initial={'cliente': publico_general.pk},
    )
    item_formset = VentaItemFormSet(
        request.POST or None,
        form_kwargs={'inventarios': inventarios},
    )

    if request.method == 'POST' and venta_form.is_valid() and item_formset.is_valid():
        lineas = [
            (form.cleaned_data['inventario'], form.cleaned_data['cantidad'])
            for form in item_formset
            if form.cleaned_data.get('inventario')
        ]
        if not lineas:
            item_formset._non_form_errors = item_formset.error_class(
                ['Agrega al menos un producto a la venta.']
            )
        else:
            try:
                with transaction.atomic():
                    inventario_ids = [inventario.pk for inventario, _ in lineas]
                    inventarios_bloqueados = {
                        inventario.pk: inventario
                        for inventario in Inventario.objects.select_for_update().select_related(
                            'ropa', 'color'
                        ).filter(pk__in=inventario_ids)
                    }
                    total = Decimal('0.00')
                    for inventario, cantidad in lineas:
                        bloqueado = inventarios_bloqueados.get(inventario.pk)
                        if bloqueado is None or bloqueado.unidades < cantidad:
                            raise ValueError(
                                f'No hay suficientes unidades disponibles de {inventario}.'
                            )
                        total += bloqueado.ropa.precio * cantidad

                    venta = Venta.objects.create(
                        cliente=venta_form.cleaned_data['cliente'],
                        total=total,
                    )
                    for inventario, cantidad in lineas:
                        bloqueado = inventarios_bloqueados[inventario.pk]
                        DetalleVenta.objects.create(
                            venta=venta,
                            inventario=bloqueado,
                            cantidad=cantidad,
                            precio_unitario=bloqueado.ropa.precio,
                        )
                        Inventario.objects.filter(pk=bloqueado.pk).update(
                            unidades=F('unidades') - cantidad
                        )
            except ValueError as error:
                item_formset._non_form_errors = item_formset.error_class([str(error)])
            else:
                messages.success(request, f'Venta #{venta.pk} registrada correctamente.')
                return redirect('venta-detalle', pk=venta.pk)

    return render(
        request,
        'venta_form.html',
        {'form': venta_form, 'formset': item_formset},
    )


@login_required
@user_passes_test(lambda user: es_administrador(user) or (
    user.is_authenticated and user.groups.filter(name=ROL_CAJERO).exists()
))
def venta_lista(request):
    ventas = Venta.objects.select_related('cliente').order_by('-fecha')
    return render(request, 'venta_list.html', {'ventas': ventas})


@login_required
@user_passes_test(lambda user: es_administrador(user) or (
    user.is_authenticated and user.groups.filter(name=ROL_CAJERO).exists()
))
def venta_detalle(request, pk):
    venta = get_object_or_404(
        Venta.objects.select_related('cliente').prefetch_related(
            'detalles__inventario__ropa',
            'detalles__inventario__color',
        ),
        pk=pk,
    )
    return render(request, 'venta_detail.html', {'venta': venta})