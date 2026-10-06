from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('proveedores/', views.ProveedorListView.as_view(), name='proveedores'),
    path('clientes/', views.ClienteListView.as_view(), name='clientes'),
    path('colores/', views.ColorListView.as_view(), name='colores'),
    path('catalogo-ropa/', views.RopaListView.as_view(), name='catalogo_ropa'),
    path('productos/', views.RopaListView.as_view(), name='productos'),
    path('productos/agregar/', views.RopaCreateView.as_view(), name='ropa-agregar'),
    path('productos/<int:pk>/inventario/', views.actualizar_inventario, name='producto-inventario'),
    path('ventas/', views.venta_lista, name='ventas'),
    path('ventas/nueva/', views.registrar_venta, name='venta-nueva'),
    path('ventas/<int:pk>/', views.venta_detalle, name='venta-detalle'),
]
