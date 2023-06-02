from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signUp, name="signup"),
    path("miCuenta/", views.miCuenta, name="miCuenta"),
    path("addDirection/", views.addDirection, name ='addDirection'),
]