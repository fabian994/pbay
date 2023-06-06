from django.urls import path
from . import views 


urlpatterns = [
    path("pedidos/", views.pedidos, name="pedidos"),
    path("productos/", views.productos, name="productos"),
    path("details/", views.details, name="details"),
    path("auction/", views.auction, name="auction"),
    path("compras/", views.compras, name="compras"),
    path("busqueda/", views.busqueda, name="busqueda"),
    path('backend/', views.obtener_elementos, name='backend'),
    path('selctdirection/', views.selctdirection, name='selctdirection'),
    path('searchByCategory', views.searchByCategory, name='searchByCategory'),
    path('addCarrito/', views.addCarrito, name='addCarrito'),
]