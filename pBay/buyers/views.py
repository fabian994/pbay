from django.shortcuts import render
from utils import infoProductoUser, getdirection, switchMainDirection, searchCat, addCart, getWish, search, getRecomendations, productFiltering
from utils import infoProductos, addWish, getArrayNames, sendemail
from .form import *
from loginSignup.views import *
from django.http import JsonResponse
from django.http import HttpResponse
import random
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pytz
from datetime import datetime, timedelta
#sendemail('Mailtest', 'si te llego?', ['a01769961@tec.mx'])

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

def details(request):
    id = request.GET.get('id')
    response = infoProductos(id)
    context = {"infoDet":response}
    return render(request, "Product_Details.html", context)

def auction(request):
    user = request.session.get("usuario")
    if user == "NoExist" or user == None:
        return redirect('home')
    
    id = request.GET.get('id')
    response = infoProductos(id)
    bid_Form = bidForm()
    
    print('ouut post')
    if request.method=='POST':
        print('in post')
        bid_Form = bidForm(request.POST)
        if bid_Form.is_valid():
            data = bid_Form.cleaned_data
            print(data)
            cBidRef = firestore_connection("liveAuctions").document(id).get()
            cbid = cBidRef.to_dict().get('bid')
            if data['newBid'] > cbid:
                dateToday = datetime.now() + timedelta(days=0)
                dateToday = dateToday.replace(tzinfo=pytz.UTC)
                print('today ', dateToday)
                print('aucten, ', response[0][12])
                if dateToday < response[0][12]:
                    auctData = {'bid': data['newBid'], 'cBidder_id': user['localId']}

                    ref = firestore_connection("liveAuctions").document(id)
                    ref.update(auctData)
                    messages.success(request, "Oferta Aceptada")
                else:
                    messages.error(request, "Oferta fuera de tiempo")
            else:
                messages.error(request, "Oferta Rechazada")

    print('response----')
    print(response[0])
    print(response[0][11])
    print('dateend ',response[0][12])
    ref = firestore_connection("liveAuctions").document(id).get()
    cbid = ref.to_dict().get('bid')
    #print(cbid)
    context = {"infoDet":response, 'bidForm': bid_Form, 'cBid':cbid}
    return render(request, "Auction_Details.html", context)

def compras(request):
    sesion = request.session['usuario']
    if sesion == "NoExist":
        return redirect('home')
    context = {'products': getRecomendations()}

    db = firestore.client()
    datos_firestore = db.collection('products').where('PromoStatus', '==', True).get()
    random_docs = datos_firestore

    textos_unicos = set()

    for doc in random_docs:
        print('-doc-')
        print('list status: ', doc.to_dict().get('listStatus'))
        print('delete status: ',doc.to_dict().get('delete'))
        if (doc.to_dict().get('delete') != True) and (doc.to_dict().get('listStatus') != False):
            print("Agrege texto")
            texto3 = doc.to_dict().get('prodName')
            print(texto3)
            if (texto3) :
                    textos_unicos.add(texto3)
        continue



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
            boolean = request.POST.get('type')
            if boolean == 'true':
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
    sesion = request.session.get('usuario')
    if request.method == 'POST':
        selected_option = request.POST.get('item')
        print(selected_option)
        
        if addCart(selected_option, sesion):
            return JsonResponse({"response": True})
        else:
            return JsonResponse({"response": False})
    return HttpResponse(status=200)

def notifySeller(request):
    sesion = request.session.get('usuario')
    if request.method == 'POST':
        selected_option = request.POST.get('item')
        print(selected_option)
        prod = firestore_connection("products").document(selected_option).get()
        prodName = prod.to_dict().get('prodName')
        selleruid = prod.to_dict().get('seller_id')
        print('into getting mail')
        sellerMail = firestore_connection("users").document(selleruid).get()
        sellMail = sellerMail.to_dict().get('userMail')
        print(sellMail)

        sendemail('Interes de Usuario', 'un usuario muestra interes en el articulo ' + prodName
                  , [sellMail])
        
    return HttpResponse(status=200)

def addWishList(request):
    sesion = request.session.get('usuario')
    if request.method == 'POST':
        selected_option = request.POST.get('wish')
        array_name = request.POST.get('arrayName')
        if addWish(selected_option, sesion, array_name):
            return JsonResponse({"response": True})
        else:
            return JsonResponse({"response": False})
    return HttpResponse(status=200)

def fetch_array_names(request):
    user = request.session.get('usuario')
    array_names = getArrayNames(user)
    return JsonResponse({'arrayNames': array_names})

def createNewArray(request):
    sesion = request.session.get('usuario')
    if request.method == 'POST':
        selected_option = request.POST.get('wish')
        array_name = request.POST.get('arrayName')
        if addWish(selected_option, sesion, array_name):
            return JsonResponse({"response": True})
        else:
            return JsonResponse({"response": False})
    return HttpResponse(status=200)

def search_products(request):
    sesion = request.session['usuario']
    if sesion == "NoExist":
        return redirect('home')
    
    search_name = request.GET.get('search')
    context = {'products': search(search_name)}

    return render(request, "compras_Busqueda.html", context)

