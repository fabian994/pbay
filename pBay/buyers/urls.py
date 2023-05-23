from django.urls import path

from . import views

urlpatterns = [
    path("pedidos/", views.pedidos, name="pedidos"),
    path("productos/", views.productos, name="productos"),
]