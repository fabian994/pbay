from django.urls import path
from . import views 


urlpatterns = [
    path("pedidos/", views.pedidos, name="pedidos"),
    path("productos/", views.productos, name="productos"),
    path("details/", views.details, name="details"),
    path("auction/", views.auction, name="auction"),
    path("compras/", views.compras, name="compras"),
    path("busqueda/", views.busqueda, name="busqueda"),
    path('obtener_elementos/', views.obtener_elementos, name='obtener_elementos'),
    path('getWishList/', views.getWishList, name='getWishList'),
    path('selctdirection/', views.selctdirection, name='selctdirection'),
    path('searchByCategory', views.searchByCategory, name='searchByCategory'),
    path('addCarrito/', views.addCarrito, name='addCarrito'),
    path('selectlist/', views.addCarrito, name='selectlist'),
]