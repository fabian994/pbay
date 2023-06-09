from utils import PayDetails
from django.shortcuts import render
from .form import *
from .models import *
from utils import sells_history, productFiltering
from utils import cancel_auction
from utils import payment_detail_by_month
from utils import infoventas
from utils import firestore_connection, storeProductImages
from utils import deleteVenta
from datetime import date
from datetime import datetime, timedelta
from loginSignup.views import *
from django.core.files.storage import default_storage
import pytz
from utils import getimage
# Create your views here.


def historial_ventas(request):

    user = request.session.get("usuario")

    if user == "NoExist" or user == None:
        return redirect('home')

    context = {"sells": sells_history(user.get("localId"))}

    return render(request, "historial_ventas.html", context)


def cancelar_subasta(request):
    user = request.session.get("usuario")

    if user == "NoExist" or user == None:
        return redirect('home')

    if request.method == "POST":
        cancel_auction(request.POST.get("product"))

    return redirect('historial_ventas')


def historial_pagos_detalle(request, month, year):

    user = request.session.get("usuario")

    if user == "NoExist" or user == None:
        return redirect('home')

    months = {
        '01': 'Enero',
        '02': 'Febrero',
        '03': 'Marzo',
        '04': 'Abril',
        '05': 'Mayo',
        '06': 'Junio',
        '07': 'Julio',
        '08': 'Agosto',
        '09': 'Septiembre',
        '10': 'Octubre',
        '11': 'Noviembre',
        '12': 'Diciembre'
    }

    if months.get(month) == None or not year.isdigit():
        return redirect('historial_pagos')

    payments = payment_detail_by_month(user.get("localId"), month, year)
    total = sum([float(payment.get("price")) for payment in payments])
    status = "Entregado"

    for payment in payments:
        if payment.get("status") == "Pendiente":
            status = "Pendiente"
            break

    context = {"payments": payments, "total": total,
               "date": f"{months.get(month)} {year}",
               "status": status}

    return render(request, "historial_pagos_detalle.html", context)


def detalles_producto(request):
    sesion = request.session['usuario']
    if sesion == "NoExist":
        return redirect('home')
    response = []
    sesion = request.session['usuario']

    if request.method == 'POST':
        response = []
        form = Filter(request.POST)
        if form.is_valid():
            selected_option2 = form.cleaned_data['Filtering']
            if selected_option2 == 'nada':
                response = infoventas(sesion, 0)
            elif selected_option2 == 'subasta':
                response = infoventas(sesion, 1)
            else:
                response = infoventas(sesion, 2)
    else:
        response = infoventas(sesion, 0)
        form = Filter()
    # deleteFunction = Delete(request.POST)
    # idToDelete = deleteFunction.cleaned_data['idDoc']
    # responseDelete = deleteFunction.cleaned_data['idDoc']
    # context['delete'] = deleteFunction
    print("Metodo ", request)
    context = {"htmlinfo":  response}
    context['form'] = form
    return render(request, "Product_Details_Seller.html", context)

def productos(request):
    session = request.session['usuario']
    if session == "NoExist":
        return redirect('home')
    else:
        if request.method == 'POST':
            form = Orden(request.POST)
            form2 = Filter(request.POST)
            if form2.is_valid():
                selected_option2 = form2.cleaned_data['Filtering']
                if selected_option2 == 'nada':
                    response = productFiltering(session, 0)
                elif selected_option2 == 'subasta':
                    response = productFiltering(session, 1) 
                else:
                    response = productFiltering(session, 2) 
            if form.is_valid():
                # Acceder al valor seleccionado del campo de selección
                selected_option = form.cleaned_data['Sorting']
                # Nuevos a viejos
                if selected_option=='descendente':
                    response =  response[::-1]
        else:
            response = productFiltering(session,0) 
            form = Orden()
            form2 = Filter()
        
        user_id = session['localId']
        #response = productList(user_id)
        context = {"htmlinfo":  response}
        context['form1'] = form
        context['form2'] = form2
        print(context)
        return render(request, "productos.html", context)


def ventas_detalle(request, context):
    user = request.session.get("usuario")
    context = {"trans": PayDetails(user.get("localId"))}
    return render(request, "historial_ventas_detalle.html", context)

def historial_ventas_detalle(request,id_sale):
    sale = firestore_connection('transactions').document(id_sale).get()
    sale = sale.to_dict() 
    print(sale)
    product = firestore_connection('products').document(sale['id_prod']).get()
    product = product.to_dict() 

    imageref = getimage(sale['id_prod'],product['mainImg'])


    context = {'sell':sale,'image': imageref, 'productname':product['prodName'],
               'saleId':id_sale}
    return render(request, 'historial_ventas_detalle.html', context) 

def delete_producto(request):
    if request.method == 'POST':
        response = []
        print("Entra v2")
        idDoc = request.POST['idDoc']
        print("IdDoc: ", idDoc)
        deleteVenta(idDoc)
        request.method = 'GET'
        return detalles_producto(request)


def historial_pagos(request):
    user = request.session.get("usuario")
    context = {"sells": PayDetails(user.get("localId"))}
    return render(request, "Payment_Details_Seller.html")


def add_product(request):
    user = request.session.get("usuario")
    if user == "NoExist" or user == None:
        return redirect('home')

    if request.method == "POST":
        reg_form = productCreate(request.POST, request.FILES)
        context = {
            "title": "Registro producto",
            "form": reg_form
        }
        # data = reg_form.cleaned_data
        print('enter post')
        print(reg_form.is_valid())
        print(reg_form.errors)
        if reg_form.is_valid():
            print('form is valid')
            data = reg_form.cleaned_data

            cat = str(data['category'])
            subcat1 = str(data['subCategory1'])
            subcat2 = str(data['subCategory2'])
            print('data: ', data)
            # print('main img: ', type(mig))
            # print('cat: ', cat)
            # print('subcat1: ', type(subcat1))
            # print('subcat2: ', subcat2)
            prodImgs = request.FILES
            # Product Data Dictionary
            # print('dic images : ', prodImgs)
            # print('main image name : ', prodImgs['mainImage'].name)
            imgList = []
            for img in prodImgs:
                if img == prodImgs['mainImage']:
                    pass
                imgList.append(prodImgs[img].name)

            # print(imgList)

            data['publishDate'] = datetime.combine(
                data['publishDate'], datetime.min.time())
            if data['condition'] == 'false': data['condition'] = False
            else: data['condition'] = True

            if data['promote'] == 'false': data['promote'] = False
            else: data['promote'] = True

            if data['vendType'] == 'false': data['vendType'] = False
            else: data['vendType'] = True

            prodData = {'Brand': data['brand'], 'Condition': data['condition'], 'Model': data['model'], 'PromoStatus': data['promote'],
                        'prodName': data['title'], 'prodDesc': data['about'], 'pubDate': data['publishDate'], 'saleType': data['vendType'],
                        'category':cat, 'subCategory1':subcat1, 'seller_id': user['localId'], 
                        'SubCategory2':subcat2, 'mainImg': prodImgs['mainImage'].name, 'images':imgList}
            saleType = data['vendType']
            print(saleType)
            try:
                ref = firestore_connection('products').add(prodData) # Add product data to product collection, creates autoid

                prod_id = str(ref[1].id)
                print('obj id: ', prod_id)
                # print('img: ',prodImgs)
                for img in prodImgs:
                    #print('img: ',prodImgs[img])
                    #print('name img: ',prodImgs[img].name)
                    file_save = default_storage.save(prodImgs[img].name, prodImgs[img])#Saves file to local storage with default_storage
                    #print('saved img')
                    #print(officialID.name)
                    storeProductImages(ref[1].id, prodImgs[img].name)#Calls function in utils.py
                    #print('stored to firebase')
                    default_storage.delete(prodImgs[img].name)#Deletes file from local storage
                
                #return render(request, "add_product.html", context)
                print("Product added to the DataBase")
                messages.success(request, "Producto añadido correctamente")
                if saleType == 'false':
                    print('to redirect')
                    return redirect('add_direct_sale_prod', prod_id = prod_id)
                elif saleType == 'true':
                    print('to redirect')
                    return redirect('add_prod_auctions', prod_id = prod_id)
            except Exception as e:
                    print(e)
                    messages.error(request, "Error al añadir producto")
        else:
            print(reg_form.errors)
            return render(request, "add_product.html", context)
    
    print('mo post')
    reg_form = productCreate()
    context = {
        "title": "Registro producto",
        "form": reg_form
    }

    return render(request, "add_product.html", context)


def add_productDirSale(request, prod_id):
    print(prod_id)
    print('out post')
    if request.method == "POST":
        prod = firestore_connection("products").document(prod_id).get()
        product = prod.to_dict()
        print('enter post')
        dir_saleForm = productDirectSale(request.POST)
        promo_form = productPromote(request.POST)
        context = {
            "title": "Registro producto",
            "form_sale": dir_saleForm,
            "form_promo": promo_form,
            "prod_id": prod_id
        }
        print(dir_saleForm.is_valid())
        print(dir_saleForm.errors)
        # data = reg_form.cleaned_data
        if dir_saleForm.is_valid() and promo_form.is_valid():
            data = dir_saleForm.cleaned_data
            promo_dur = promo_form.cleaned_data
            print('dir sale data:', data)
            print('duration :', promo_dur['PromoDuration'])
            print(product['pubDate'])
            promoEnd = product['pubDate'] + \
                timedelta(days=int(promo_dur['PromoDuration']))
            data['RemovalDate'] = datetime.combine(
                data['RemovalDate'], datetime.min.time())
            data['RemovalDate'] = data['RemovalDate'].replace(tzinfo=pytz.UTC)
            print(data['RemovalDate'])
            print(promoEnd)

            if promoEnd < data['RemovalDate']:
                if product['pubDate'] < data['RemovalDate']:

                    prod_data = {
                        'Stock': data['inventory'], 'Price': data['cost'], 'shippingFee': data['shippingFee'],
                        'retireDate': data['RemovalDate'], 'promoDateEnd': promoEnd
                    }
                    ref = firestore_connection("products").document(prod_id)
                    ref.update(prod_data)
                    return redirect("compras")
            else:
                dir_saleForm = productDirectSale()
                promo_form = productPromote()
                context = {
                    "title": "Registro producto",
                    "form_sale": dir_saleForm,
                    "form_promo": promo_form,
                    "prod": product,
                }
                return render(request, "add_product_directSale.html", context)
        elif dir_saleForm.is_valid():
            data = dir_saleForm.cleaned_data
            print(data)
            print('dir sale data:', data)
            print(product['pubDate'])
            data['RemovalDate'] = datetime.combine(
                data['RemovalDate'], datetime.min.time())
            data['RemovalDate'] = data['RemovalDate'].replace(tzinfo=pytz.UTC)
            print(data['RemovalDate'])

            if product['pubDate'] < data['RemovalDate']:

                prod_data = {
                    'Stock': data['inventory'], 'Price': data['cost'], 'shippingFee': data['shippingFee'],
                    'retireDate': data['RemovalDate'],
                }
                ref = firestore_connection("products").document(prod_id)
                ref.update(prod_data)
                return redirect("compras")
            else:
                dir_saleForm = productDirectSale()
                promo_form = productPromote()
                context = {
                    "title": "Registro producto",
                    "form_sale": dir_saleForm,
                    "form_promo": promo_form,
                    "prod": product,
                }
                return render(request, "add_product_directSale.html", context)
            
        else:
            return render(request, "add_product_directSale.html", context)


    prod = firestore_connection("products").document(prod_id).get()
    product = prod.to_dict()
    print(product)
    dir_saleForm = productDirectSale()
    promo_form = productPromote()
    context = {
        "title": "Registro producto",
        "form_sale": dir_saleForm,
        "form_promo": promo_form,
        "prod": product,
    }
    return render(request, "add_product_directSale.html", context)

def add_product_Auction(request, prod_id):
    prod = firestore_connection("products").document(prod_id).get()
    product = prod.to_dict()
    print(product)

    if request.method == "POST":
        print('enter post')
        auctionForm = productAuction(request.POST)
        promo_form = productPromote(request.POST)
        context = {
            "title": "Registro producto",
            "form_auction": auctionForm,
            "form_promo": promo_form,
            "prod_id": prod_id
        }
        print(auctionForm.is_valid())
        print(auctionForm.errors)
        print(promo_form.is_valid())
        #data = reg_form.cleaned_data
        if auctionForm.is_valid() and promo_form.is_valid():
            data = auctionForm.cleaned_data
            promo_dur = promo_form.cleaned_data
            print('dir sale data:',data)
            print('duration :',promo_dur['PromoDuration'])
            print(product['pubDate'])
            promoEnd = product['pubDate'] + timedelta(days=int(promo_dur['PromoDuration']))
            data['duration'] = product['pubDate'] + timedelta(days=int(data['duration']))
            # data['duration'] = data['duration'].replace(tzinfo=pytz.UTC)
            print(data['duration'])
            print(promoEnd)


            if promoEnd > data['duration']:
                
                prod_data = {
                    'auctionDateEnd': data['duration'], 'initialOffer': data['initialOffer'],
                    'shippingFee': data['shippingFee'], 
                    'minimumOffer': data['minimumOffer'], 'promoDateEnd': promoEnd
                }
                ref = firestore_connection("products").document(prod_id)
                ref.update(prod_data)
                return redirect("compras")
            else:
                auctionForm = productAuction()
                promo_form = productPromote()
                context = {
                    "title": "Registro producto",
                    "form_auction": auctionForm,
                    "form_promo": promo_form,
                    "prod": product,
                }
                return render(request, "add_product_Auction.html", context)
        elif auctionForm.is_valid():
            data = auctionForm.cleaned_data
            print('dir sale data:',data)
            print(product['pubDate'])
            data['duration'] = product['pubDate'] + timedelta(days=int(data['duration']))
            # data['duration'] = data['duration'].replace(tzinfo=pytz.UTC)
            print(data['duration'])
            prod_data = {
                'auctionDateEnd': data['duration'], 'initialOffer': data['initialOffer'],
                'shippingFee': data['shippingFee'], 
                'minimumOffer': data['minimumOffer'], 'promoDateEnd': promoEnd
            }
            print('subi')
            ref = firestore_connection("products").document(prod_id)
            ref.update(prod_data)
            return redirect("compras")
        else:
            return render(request, "add_product_Auction.html", context)

    auctionForm = productAuction()
    promo_form = productPromote()
    context = {
        "title": "Registro producto",
        "form_auction": auctionForm,
        "form_promo": promo_form,
        "prod": product,
    }
    return render(request, "add_product_Auction.html", context)




def modify_product(request,prod_id):
    print("Enter modify product : ",prod_id)
    #prod_id="Fd0Tjz7UX2Sq58HT3pwS"
    prod = firestore_connection("products").document(prod_id).get()
    print(prod)
    print(request)
    product = prod.to_dict()
    user = request.session.get("usuario")
    if user == "NoExist" or user == None:
        return redirect('home')
    if request.method == "POST":
        reg_form = productModify(request.POST, request.FILES)
        context = {
            "title": "Registro producto",
            "form": reg_form
        }
        # data = reg_form.cleaned_data
        print('enter post')
        print(reg_form.is_valid())
        print(reg_form.errors)
        if reg_form.is_valid():
            print('form is valid')
            data = reg_form.cleaned_data

            cat = str(data['category'])
            subcat1 = str(data['subCategory1'])
            subcat2 = str(data['subCategory2'])
            print('data: ', data)
            prodImgs = request.FILES
            imgList = []
            for img in prodImgs:
                if img == prodImgs['mainImage']:
                    pass
                imgList.append(prodImgs[img].name)
                
            data['publishDate'] = datetime.combine(
                data['publishDate'], datetime.min.time())
            
            if data['condition'] == 'false': data['condition'] = False
            else: data['condition'] = True

            if data['promote'] == 'false': data['promote'] = False
            else: data['promote'] = True

            if data['vendType'] == 'false': data['vendType'] = False
            else: data['vendType'] = True

            prodData = {'Brand': data['brand'], 'Condition': data['condition'], 'Model': data['model'], 'PromoStatus': data['promote'],
                        'prodName': data['title'], 'prodDesc': data['about'], 'pubDate': data['publishDate'], 'saleType': data['vendType'],
                        'category':cat, 'subCategory1':subcat1, 'seller_id': user['localId'], 
                        'SubCategory2':subcat2, 'mainImg': prodImgs['mainImage'].name, 'images':imgList}
            saleType = data['vendType']
            print(saleType)
            ref = firestore_connection("products").document(prod_id)
            ref.update(prodData)
            
            saleType = product['saleType']
            
            if saleType == False:
                print('to redirect')
                return redirect('add_direct_sale_prod', prod_id = prod_id)
            elif saleType == True:
                print('to redirect')
                return redirect('add_prod_auctions', prod_id = prod_id)
        else:
            print(reg_form.errors)
            return render(request, "modify_product.html", context)
    
    print('mo post')
    reg_form = productModify()
    context = {
        "title": "Registro producto",
        "form": reg_form
    }
    return render(request, "modify_product.html", context)

def load_subcategories1(request):
    Cat_id = request.GET.get('cat')
    print(Cat_id)
    SubCategories = SubCategory1.objects.filter(
        Cat_id=Cat_id).order_by('Subcategoria1')
    return render(request, "SubCategory1_dropdown.html", {'SubCategories': SubCategories})


def load_subcategories2(request):
    SubCat_id = request.GET.get('subcat')
    print(SubCat_id)
    SubCategories2 = SubCategory2.objects.filter(
        SubCat1_id=SubCat_id).order_by('Subcategoria2')
    return render(request, "SubCategory2_dropdown.html", {'SubCategories2': SubCategories2})
