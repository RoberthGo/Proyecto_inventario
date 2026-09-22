from django.contrib import admin
from .models import Color, Proveedor, Ropa, Cliente


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
