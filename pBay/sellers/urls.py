from django.urls import path

from . import views


urlpatterns = [
    path('mis_ventas/historial_ventas',
         views.historial_ventas, name='historial_ventas'),
    path('mis_ventas/detalles_producto', #RIch
         views.detalles_producto, name='detalles_producto'),
    path('mis_ventas/historial_pagos', #Rich 
         views.historial_pagos, name='historial_pagos'),
    path('mis_ventas/historial_pagos/<str:month>/<str:year>',
         views.historial_pagos_detalle, name='historial_pagos_detalle'),
    path('mis_ventas/anadir_producto',
         views.add_product, name='add_product'),
     path("mis_ventas/anadir_producto/venta_directa/<str:prod_id>", 
          views.add_productDirSale, name = "add_direct_sale_prod"),
    path('mis_ventas/subastas',
         views.subastas, name='subastas'),

     path('ajax/load-Subcategory1/', views.load_subcategories1, name='ajax_load_Subcategories1'), # AJAX
     path('ajax/load-Subcategory2/', views.load_subcategories2, name='ajax_load_Subcategories2'), # AJAX
]
