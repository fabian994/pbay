from django.urls import path

from . import views

urlpatterns = [
    path('mis_ventas/historial_ventas',
         views.historial_ventas, name='historial_ventas'),
    path('mis_ventas/detalles_producto',
         views.detalles_producto, name='detalles_producto'),
    path('mis_ventas/historial_pagos',
         views.historial_pagos, name='historial_pagos'),
    path('mis_ventas/historial_pagos/detalle',
         views.historial_pagos_detalle, name='historial_pagos'),
    path('mis_ventas/anadir_producto',
         views.add_product, name='add_product'),
    path('mis_ventas/subastas',
         views.subastas, name='subastas')
]
