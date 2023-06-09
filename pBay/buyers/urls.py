from django.urls import path
from . import views 


urlpatterns = [
    path("pedidos/", views.pedidos, name="pedidos"),
    path("details", views.details, name="details"),
    path("auction", views.auction, name="auction"),
    path("compras/", views.compras, name="compras"),
    path("busqueda/", views.busqueda, name="busqueda"),
    path('obtener_elementos/', views.obtener_elementos, name='obtener_elementos'),
    path('getWishList/', views.getWishList, name='getWishList'),
    path('selctdirection/', views.selctdirection, name='selctdirection'),
    path('searchByCategory', views.searchByCategory, name='searchByCategory'),
    path('addCarrito/', views.addCarrito, name='addCarrito'),
    path('addWishList/', views.addWishList, name='addWishList'),
    path('fetch_array_names/', views.fetch_array_names, name='fetch_array_names'),
    path('createNewArray/', views.createNewArray, name='createNewArray'),
    path('selectlist/', views.addCarrito, name='selectlist'),
    path('search', views.search_products, name='search_products'),
    path('notifySeller/', views.notifySeller, name='notifySeller'),
]