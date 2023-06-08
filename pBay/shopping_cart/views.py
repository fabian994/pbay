from django.shortcuts import render
from utils import firestore_connection, storeProductImages, getCart, delete_item, increase_item, decrease_item
from loginSignup.views import *
from django.core.files.storage import default_storage

# Create your views here.

def carrito(request):
    user = request.session.get("usuario")

    if user == "NoExist" or user == None:
        return redirect('home')
    
    response, prices = getCart(user)
    context = {
                "htmlinfo":  response,
                "prices": prices
              }

    return render(request, "carrito.html", context)

def delete_event(request, id):
    user = request.session.get("usuario")
    delete_item(user, id)
    
    return carrito(request)

def increase_event(request, id, amount):
    user = request.session.get("usuario")
    increase_item(user, id, amount)
    
    return carrito(request)

def decrease_event(request, id, amount):
    user = request.session.get("usuario")

    if(amount == 1):
        delete_event(request, id)
    else: decrease_item(user, id, amount)
    
    return carrito(request)