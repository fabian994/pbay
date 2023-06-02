from utils import sellsHistory, PayDetails
from django.shortcuts import render
from utils import infoventas
from .form import *
from loginSignup.views import *

# Create your views here.


def historial_ventas(request):
    user = request.session.get("usuario")
    context = {"sells": sellsHistory(user.get("localId"))}
    return render(request, "historial_ventas.html", context)


def historial_pagos_detalle(request):
    return render(request, "historial_pagos_detalle.html")


def detalles_producto(request):
    sesion = request.session['usuario']
    if sesion == "NoExist":
        return redirect('home')
    response = []
    sesion = request.session['usuario']

    if request.method == 'POST':
        response = []
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
        response = infoventas(sesion, 0)
        form = Filter()
    context = {"htmlinfo":  response}
    context['form'] = form
    return render(request, "Product_Details_Seller.html", context)


def historial_pagos(request):
    user = request.session.get("usuario")
    context = {"sells": PayDetails(user.get("localId"))}
    return render(request, "Payment_Details_Seller.html")


def subastas(request):
    return render(request, "subastas.html")


def add_product(request):
    return render(request, "add_product.html")

