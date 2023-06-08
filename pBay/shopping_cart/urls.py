from django.urls import path

from . import views

urlpatterns = [
    path('carrito',
         views.carrito, name='carrito'),
    path('delete_event/<str:id>',
          views.delete_event, name='delete-event'),
]
