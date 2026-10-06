from django.contrib import admin
from .models import Cliente, Color, DetalleVenta, Proveedor, Ropa, Venta


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'correo')
    search_fields = ('nombre', 'correo')


@admin.register(Ropa)
class RopaAdmin(admin.ModelAdmin):
    list_display = ('modelo', 'tipo', 'talla', 'marca', 'precio', 'proveedor')
    list_filter = ('tipo', 'talla', 'proveedor')
    search_fields = ('modelo', 'marca', 'descripcion')


admin.site.register(Color)
admin.site.register(Cliente)


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha', 'total')
    list_filter = ('fecha',)
    search_fields = ('cliente__nombre',)
    readonly_fields = ('fecha', 'total')


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('venta', 'inventario', 'cantidad', 'precio_unitario')
    list_filter = ('inventario__ropa', 'inventario__color')
