from django.urls import path

from . import views

urlpatterns = [
    path("pedidos/", views.pedidos, name="pedidos"),
    path("details/", views.details, name="details"),
    path("auction/", views.auction, name="auction"),
]