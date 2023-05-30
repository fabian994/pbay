from django.shortcuts import render
from utils import infoventas
from .form import *
# Create your views here.


def historial_ventas(request):
    return render(request, "historial_ventas.html")


def historial_pagos_detalle(request):
    return render(request, "historial_pagos_detalle.html")

def detalles_producto(request):
    response = []
    
    sesion = request.session['usuario']
    
    if request.method == 'POST':
        response =[]
        form = Filter(request.POST)
        if form.is_valid():
            selected_option2 = form.cleaned_data['Filtering']
            if selected_option2 == 'nada':
               response = infoventas(sesion, 0)
            elif selected_option2 == 'subasta':
               response = infoventas(sesion, 1) 
            else:
                response = infoventas(sesion, 2)
    else:
        response =infoventas(sesion, 0)
        form = Filter()
    context ={"htmlinfo":  response}
    context['form'] = form
    
    return render(request, "Product_Details_Seller.html", context)



def historial_pagos(request):
    return render(request, "Payment_Details_Seller.html")

def subastas(request):
    return render(request, "subastas.html")

def add_product(request):
    return render(request, "add_product.html")

