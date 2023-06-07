from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signUp, name="signup"),
    path("miCuenta/", views.miCuenta, name="miCuenta"),
    path("addDirection/", views.addDirection, name ='addDirection'),
    path("addList/", views.addList, name ='addList'),
    path("miLista", views.MiLista, name ='miLista'),
    path("logo/", views.logo, name ='logo'),
]