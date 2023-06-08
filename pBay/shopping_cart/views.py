from django.shortcuts import render
from utils import firestore_connection, storeProductImages, getCart
from loginSignup.views import *
from django.core.files.storage import default_storage

# Create your views here.

def carrito(request):
    user = request.session.get("usuario")

    if user == "NoExist" or user == None:
        return redirect('home')
    
    response = getCart(user)
    context = {"htmlinfo":  response}


    return render(request, "carrito.html", context)