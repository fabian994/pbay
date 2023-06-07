from django.shortcuts import render
from utils import firestore_connection, storeProductImages
from loginSignup.views import *
from django.core.files.storage import default_storage

# Create your views here.

def carrito(request):
    user = request.session.get("usuario")

    if user == "NoExist" or user == None:
        return redirect('home')

    return render(request, "carrito.html")