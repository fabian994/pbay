from django.shortcuts import render

# Create your views here.

def carrito(request):
    return render(request, "carrito.html")