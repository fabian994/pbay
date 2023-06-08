from django.urls import path

from . import views

urlpatterns = [
    path('carrito',
         views.carrito, name='carrito'),
    path('delete_event/<str:id>',
          views.delete_event, name='delete-event'),
    path('increase_event/<str:id>/<int:amount>',
          views.increase_event, name='increase-event'),
    path('decrease_event/<str:id>/<int:amount>',
          views.decrease_event, name='decrease-event'),
]
