from django.shortcuts import render

# Create your views here.
def pedidos(request):
    return render(request, "pedidos.html")

def productos(request):
    return render(request, "productos.html")
def details(request):
    return render(request, "Product_Details.html")

def auction(request):
    return render(request, "Auction_Details.html")

