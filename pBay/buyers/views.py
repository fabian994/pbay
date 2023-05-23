from django.shortcuts import render

# Create your views here.
def pedidos(request):
    return render(request, "pedidos.html")

def details(request):
    return render(request, "Product_Details.html")

