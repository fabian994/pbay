from django.urls import path

from . import views

urlpatterns = [
    path('mis_ventas/historial_ventas',
         views.historial_ventas, name='historial_ventas'),
    path('mis_ventas/historial_pagos/detalle',
         views.historial_pagos_detalle, name='historial_pagos'),
    path('mis_ventas/subastas',
         views.subastas, name='subastas')
]
