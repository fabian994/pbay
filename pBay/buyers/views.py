from django.shortcuts import render

# Create your views here.
def pedidos(request):
    return render(request, "pedidos.html")

def productos(request):
    return render(request, "productos.html")

