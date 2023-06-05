from utils import PayDetails
from django.shortcuts import render
from .form import *
from utils import sells_history
from utils import payment_detail_by_month
from utils import infoventas
from loginSignup.views import *

# Create your views here.


def historial_ventas(request):

    user = request.session.get("usuario")

    if user == "NoExist" or user == None:
        return redirect('home')

    context = {"sells": sells_history(user.get("localId"))}

    return render(request, "historial_ventas.html", context)


def historial_pagos_detalle(request, month, year):

    user = request.session.get("usuario")

    if user == "NoExist" or user == None:
        return redirect('home')

    months = {
        '01': 'Enero',
        '02': 'Febrero',
        '03': 'Marzo',
        '04': 'Abril',
        '05': 'Mayo',
        '06': 'Junio',
        '07': 'Julio',
        '08': 'Agosto',
        '09': 'Septiembre',
        '10': 'Octubre',
        '11': 'Noviembre',
        '12': 'Diciembre'
    }

    if months.get(month) == None or not year.isdigit():
        return redirect('historial_pagos')

    payments = payment_detail_by_month(user.get("localId"), month, year)
    total = sum([float(payment.get("price")) for payment in payments])
    status = "Entregado"

    for payment in payments:
        if payment.get("status") == "Pendiente":
            status = "Pendiente"
            break

    context = {"payments": payments, "total": total,
               "date": f"{months.get(month)} {year}",
               "status": status}

    return render(request, "historial_pagos_detalle.html", context)


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
