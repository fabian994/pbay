from django.shortcuts import render
from utils import infoProductoUser
from .form import *

# Create your views here.
def pedidos(request):
    sesion = request.session['usuario']
    #viejos a nuevos
    
    
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
    return render(request, "pedidos.html", context)
        

def productos(request):
    return render(request, "productos.html")
def details(request):
    return render(request, "Product_Details.html")

def auction(request):
    return render(request, "Auction_Details.html")

def compras(request):
    return render(request, "compras_Principal.html")
    
def busqueda(request):
    return render(request, "compras_Busqueda.html")
