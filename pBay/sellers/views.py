from django.shortcuts import render

# Create your views here.


def historial_ventas(request):
    return render(request, "historial_ventas.html")


def historial_pagos_detalle(request):
    return render(request, "historial_pagos_detalle.html")

def detalles_producto(request):
    return render(request, "Product_Details_Seller.html")


def historial_pagos(request):
    return render(request, "Payment_Details_Seller.html")
