from django.shortcuts import render
from utils import infoProductoUser, getdirection, switchMainDirection, searchCat, addCart, getWish, search, getRecomendations, productFiltering
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
    session = request.session['usuario']
    if session == "NoExist":
        return redirect('home')
    else:
        if request.method == 'POST':
            form = Orden(request.POST)
            form2 = Filter(request.POST)
            if form2.is_valid():
                selected_option2 = form2.cleaned_data['Filtering']
                if selected_option2 == 'nada':
                    response = productFiltering(session, 0)
                elif selected_option2 == 'subasta':
                    response = productFiltering(session, 1) 
                else:
                    response = productFiltering(session, 2) 
            if form.is_valid():
                # Acceder al valor seleccionado del campo de selección
                selected_option = form.cleaned_data['Sorting']
                # Nuevos a viejos
                if selected_option=='descendente':
                    response =  response[::-1]
        else:
            response = productFiltering(session,0) 
            form = Orden()
            form2 = Filter()
        
        user_id = session['localId']
        #response = productList(user_id)
        context = {"htmlinfo":  response}
        context['form1'] = form
        context['form2'] = form2
        print(context)
        return render(request, "productos.html", context)

def details(request):
    id = request.GET.get('id')
    response = infoProductos(id)
    context = {"infoDet":response}
    return render(request, "Product_Details.html", context)

def auction(request):
    return render(request, "Auction_Details.html")

def compras(request):
    sesion = request.session['usuario']
    if sesion == "NoExist":
        return redirect('home')
    context = {'products': getRecomendations()}

    db = firestore.client()
    datos_firestore = db.collection('products').get()

    textos_unicos = set()

    for doc in datos_firestore:
        texto = doc.to_dict().get('category')
        texto2 = doc.to_dict().get('Brand')
        texto3 = doc.to_dict().get('prodName')
        if (texto and texto2 and texto3) :
            textos_unicos.add(texto)
            textos_unicos.add(texto2)
            textos_unicos.add(texto3)


    # textos = [doc.to_dict().get('prodName') for doc in datos_firestore]
    # textos2 = [doc.to_dict().get('Brand') for doc in datos_firestore]
    # textos3 = [doc.to_dict().get('category') for doc in datos_firestore]
    # twoTxt = textos + textos2 + textos3

    with open('buyers/static/scripts/suggestions.js', 'w') as archivo_js:
        archivo_js.write('let suggestions = [\n')
        for texto in textos_unicos:
            archivo_js.write(f'  "{texto}",\n')
        archivo_js.write('];')


    return render(request, "compras_Principal.html", context)

def busqueda(request):
    sesion = request.session['usuario']
    if sesion == "NoExist":
        return redirect('home')
    response = []
    sesion = request.session['usuario']

    response = infoProductos(0)
    context = {"infoprod":  response}
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
        return JsonResponse(elementos, safe=False)
        
def searchByCategory (request):
    sesion = request.session['usuario']
    if sesion == "NoExist":
        return redirect('home')
    
    category = request.GET.get('categoria')
    subcategory1 = request.GET.get('subcategoria')
    subcategory2 = request.GET.get('subcategoria2')
    
    
    products = searchCat(category, subcategory1, subcategory2)
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

