from django.shortcuts import render
from utils import infoProductoUser, getdirection, switchMainDirection, searchCat, addCart, getWish, search
from utils import infoProductos
from .form import *
from loginSignup.views import *
from django.http import JsonResponse

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Create your views here.
def pedidos(request):
    sesion = request.session['usuario']
    if sesion == "NoExist":
        return redirect('home')
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
    response = infoProductos(0)
    context = {"infoDet":response}
    return render(request, "Product_Details.html", context)

def auction(request):
    return render(request, "Auction_Details.html")

def compras(request):
    sesion = request.session['usuario']
    if sesion == "NoExist":
        return redirect('home')
    return render(request, "compras_Principal.html")

def busqueda(request):
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
                response = infoProductos(0)
            elif selected_option2 == 'subasta':
                response = infoProductos(1)
            else:
                response = infoProductos(2)
    else:
        response = infoProductos(0)
        form = Filter()
    context = {"infoprod":  response}
    context['form'] = form
    return render(request, "compras_Busqueda.html", context)

def obtener_elementos(request):
    sesion = request.session['usuario']
    if sesion == "NoExist":
        elementos = []  # Reemplaza esto con la lógica para obtener los elementos dinámicamente
        return JsonResponse(elementos, safe=False)
    else:
        elementos = getdirection(sesion)  # Reemplaza esto con la lógica para obtener los elementos dinámicamente
        elementos.append("Añadir")
        return JsonResponse(elementos, safe=False)

def selctdirection(request):
    if request.method == 'POST':
        selected_option = request.POST.get('selectedOption')
        if (selected_option == "Añadir"):
            return JsonResponse({"response" :True})
        else:
            sesion = request.session['usuario']
            switchMainDirection(selected_option, sesion)
            return JsonResponse({"response" :False})
        
def selectlist(request):
    if request.method == 'POST':
        selected_option = request.POST.get('selectedOption')
        if (selected_option == "Añadir"):
            return JsonResponse({"response" :True})
        else:
            return JsonResponse({"response" :False})

def getWishList(request):
    sesion = request.session['usuario']
    if sesion == "NoExist":
        elementos = []  # Reemplaza esto con la lógica para obtener los elementos dinámicamente
        return JsonResponse(elementos, safe=False)
    else:
        elementos = getWish(sesion)  # Reemplaza esto con la lógica para obtener los elementos dinámicamente
        elementos.append("Añadir")
        print(elementos)
        return JsonResponse(elementos, safe=False)
        
def searchByCategory (request):
    sesion = request.session['usuario']
    if sesion == "NoExist":
        return redirect('home')
    
    category = request.GET.get('categoria')
    subcategory1 = request.GET.get('subcategoria')
    subcategory2 = request.GET.get('subcategoria2')
    
    
    products = searchCat(category, subcategory1, subcategory2)
    print(request)
    return render(request, 'searchByCategory.html', {'products': products})

def addCarrito(request):
    sesion = request.session['usuario']
    if request.method == 'POST':
        selected_option = request.POST.get('item')
        print(selected_option)
        if(addCart(selected_option, sesion)):
            # return JsonResponse({"response" :True})
       
            return JsonResponse({"response" :True})
        else:
            return JsonResponse({"response" :False})

db = firestore.client()

def search_products(request):
    sesion = request.session['usuario']
    if sesion == "NoExist":
        return redirect('home')
    
    search_name = request.GET.get('search')
    context = {'products': search(search_name)}

    return render(request, "compras_Busqueda.html", context)