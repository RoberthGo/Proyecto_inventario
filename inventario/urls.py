from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('proveedores/', views.ProveedorListView.as_view(), name='proveedores'),
    path('productos/', views.RopaListView.as_view(), name='productos'),
    path('productos/<int:pk>/inventario/', views.actualizar_inventario, name='producto-inventario'),
]
