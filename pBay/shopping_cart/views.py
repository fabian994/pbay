from django.shortcuts import render
from utils import firestore_connection, storeProductImages, getCart, delete_item, increase_item, decrease_item, process_transaction, getdirection, switchMainDirection
from loginSignup.views import *
from django.core.files.storage import default_storage
from .forms import MyForm
from django.http import JsonResponse


# Create your views here.

def empty_cart(request):
    sesion = request.session['usuario']
    if sesion == "NoExist":
        return redirect('home')
    else: return render(request, "empty_cart.html")

def success(request):
    sesion = request.session['usuario']
    if sesion == "NoExist":
        return redirect('home')
    else: return render(request, "success.html")

def carrito(request):
    user = request.session.get("usuario")

    if user == "NoExist" or user == None:
        return redirect('home')
    
    response, prices = getCart(user)

    if response == 0:
        
        return empty_cart(request)

    else:

        context = {
                    "htmlinfo":  response,
                    "prices": prices,
                  }

        return render(request, "carrito.html", context)

def delete_event(request, id):
    user = request.session.get("usuario")

    if user == "NoExist" or user == None:
        return redirect('home')
    
    delete_item(user, id)
    
    return carrito(request)

def increase_event(request, id, amount):
    user = request.session.get("usuario")
    
    if user == "NoExist" or user == None:
        return redirect('home')
    
    increase_item(user, id, amount)
    
    return carrito(request)

def decrease_event(request, id, amount):
    user = request.session.get("usuario")
    
    if user == "NoExist" or user == None:
        return redirect('home')
    

    if(amount == 1):
        delete_event(request, id)
    else: decrease_item(user, id, amount)
    
    return carrito(request)

def transaction(request):
    print('********************ENTRA VIEW.PY***************************')
    print(request)
    user = request.session.get("usuario")
    
    if user == "NoExist" or user == None:
        return redirect('home')
    
    cart_data, prices = getCart(user)

    if request.method=='POST':
        print('method post')
        process_transaction(user, prices)
        return success(request)

    return carrito(request)

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
            boolean = request.POST.get('type')
            if boolean == 'true':
                switchMainDirection(selected_option, sesion)
            
            return JsonResponse({"response" :False})

