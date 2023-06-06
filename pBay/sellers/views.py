from utils import PayDetails
from django.shortcuts import render
from .form import *
from .models import *
from utils import sells_history
from utils import payment_detail_by_month
from utils import infoventas
from utils import firestore_connection, storeProductImages
from loginSignup.views import *
from django.core.files.storage import default_storage

# Create your views here.


def historial_ventas(request):

    user = request.session.get("usuario")

    if user == "NoExist" or user == None:
        return redirect('home')

    context = {"sells": sells_history(user.get("localId"))}

    return render(request, "historial_ventas.html", context)


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
    context = {"htmlinfo":  response}
    context['form'] = form
    return render(request, "Product_Details_Seller.html", context)


def historial_pagos(request):
    user = request.session.get("usuario")
    context = {"sells": PayDetails(user.get("localId"))}
    return render(request, "Payment_Details_Seller.html")


def subastas(request):
    return render(request, "subastas.html")


def add_product(request):
   # user = request.session.get("usuario")

    #if user == "NoExist" or user == None:
    #    return redirect('home')
    if request.method == "POST":
        reg_form = productCreate(request.POST, request.FILES)
        context = {
            "title": "Registro producto",
            "form": reg_form
        }
        #data = reg_form.cleaned_data
        if reg_form.is_valid():
            print(request.POST)
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
            #Product Data Dictionary
            #print('dic images : ', prodImgs)
            #print('main image name : ', prodImgs['mainImage'].name)
            imgList = []
            for img in prodImgs:
                if img == prodImgs['mainImage']:
                    pass
                imgList.append(prodImgs[img].name)

            #print(imgList)
            
            prodData = {'name': data['name'], 'category':cat, 'subCategory1':subcat1, #'seller_id': user, 
                        'SubCategory2':subcat2, 'mainImage': prodImgs['mainImage'].name, 'images':imgList}
            
            
            ref = firestore_connection('products').add(prodData) # Add product data to product collection, creates autoid
            prod_id = str(ref[1].id)
            
            print('img: ',prodImgs)
            for img in prodImgs:
                print('img: ',prodImgs[img])
                print('name img: ',prodImgs[img].name)
                file_save = default_storage.save(prodImgs[img].name, prodImgs[img])#Saves file to local storage with default_storage
                #print('saved img')
                #print(officialID.name)
                storeProductImages(ref[1].id, prodImgs[img].name)#Calls function in utils.py
                #print('stored to firebase')
                default_storage.delete(prodImgs[img].name)#Deletes file from local storage
            
            #return render(request, "add_product.html", context)
            return redirect('add_direct_sale_prod', prod_id = prod_id)
    else:
        reg_form = productCreate()
        context = {
            "title": "Registro producto",
            "form": reg_form
        }

        return render(request, "add_product.html", context)

def add_productDirSale(request, prod_id):
    print(request.method)
    if request.method == "POST":
        print('enter post')
        dir_saleForm = productDirectSale(request.POST)
        context = {
            "title": "Registro producto",
            "form": dir_saleForm,
            "prod_id": prod_id
        }
        print(dir_saleForm.is_valid())
        print(dir_saleForm.errors)
        #data = reg_form.cleaned_data
        if dir_saleForm.is_valid():
            data = dir_saleForm.cleaned_data
            print(data)
            return redirect("subastas")
        else:
            print(dir_saleForm.errors.as_data())
    
    dir_saleForm = productDirectSale()
    context = {
        "title": "Registro producto",
        "form": dir_saleForm,
        "prod_id": prod_id
    }
    return render(request, "add_product_directSale.html", context)

def load_subcategories1(request):
    Cat_id = request.GET.get('cat')
    print(Cat_id)
    SubCategories = SubCategory1.objects.filter(Cat_id = Cat_id).order_by('Subcategoria1')
    return render(request, "SubCategory1_dropdown.html", {'SubCategories': SubCategories})

def load_subcategories2(request):
    SubCat_id = request.GET.get('subcat')
    print(SubCat_id)
    SubCategories2 = SubCategory2.objects.filter(SubCat1_id = SubCat_id).order_by('Subcategoria2')
    return render(request, "SubCategory2_dropdown.html", {'SubCategories2': SubCategories2})
