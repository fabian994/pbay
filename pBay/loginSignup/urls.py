from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("home/", views.home, name="home"),
    path("log/", views.log, name="log"),
    path("signup/", views.signUp, name="signup"),
]