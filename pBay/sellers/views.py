from django.shortcuts import render
from utils import infoProductoUser
from .form import *
# Create your views here.


def historial_ventas(request):
    return render(request, "historial_ventas.html")


def historial_pagos_detalle(request):
    return render(request, "historial_pagos_detalle.html")

def detalles_producto(request):
    sesion = request.session['usuario']
    #producto a categoria
    
    if request.method == 'POST':
        form = Orden(request.POST)
        form2 = Filter(request.POST)
        if form2.is_valid():
            selected_option2 = form2.cleaned_data['Filtering']
            if selected_option2 == 'nada':
               response = infoProductoUser(sesion, 0)
            elif selected_option2 == 'subasta':
               response = infoProductoUser(sesion, 1) 
            else:
                response = infoProductoUser(sesion, 2) 
        
        
        if form.is_valid():
            # Acceder al valor seleccionado del campo de selección
            selected_option = form.cleaned_data['Sorting']
            # Nuevos a viejos
            if selected_option=='descendente':
                response =  response[::-1]

    else:
        response = infoProductoUser(sesion,0) 
        form = Orden()
        form2 = Filter()
    context ={"htmlinfo":  response}
    context['form1'] = form
    context['form2'] = form2
    
    return render(request, "Product_Details_Seller.html")



def historial_pagos(request):
    return render(request, "Payment_Details_Seller.html")

def subastas(request):
    return render(request, "subastas.html")

def add_product(request):
    return render(request, "add_product.html")

