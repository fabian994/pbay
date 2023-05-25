from django.shortcuts import render
from utils import infoProductoUser

# Create your views here.
def pedidos(request):
    sesion = request.session['usuario']
    correo = request.session['correo']
    contra = request.session['contra']
    response = infoProductoUser(correo,contra)
    context ={"htmlinfo":  response}
    return render(request, "pedidos.html",context)

def productos(request):
    return render(request, "productos.html")
def details(request):
    return render(request, "Product_Details.html")

def auction(request):
    return render(request, "Auction_Details.html")

def compras(request):
    return render(request, "compras_Principal.html")

