from django.shortcuts import render, redirect
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import default_storage
from django.contrib import messages
from .form import *
from utils import LogIn_Firebase, signUp_Firebase, firestore_connection, storeOfficialID, infoUser, addDirect, addLista, searchList
from datetime import datetime
from django.http import JsonResponse
import json
import os

# Create your views here.
def home(request):
    form = MiFormulario()
    context = {"form": form, "title": "Login"}
    request.session['usuario'] =  "NoExist"
    if request.method=='POST':
        form = MiFormulario(request.POST)
        context = {"form": form, "title": "Login"}
        if form.is_valid():
            print("Form valid")
            data = form.cleaned_data
            Correo= data["campo1"]
            Contra= data["campo2"]
            result =LogIn_Firebase(Correo, Contra)
            if result == False:
                div_content = 'Error en contraseña o correo'
                context['div_content'] = div_content
                return render(request, 'login.html', context)
            elif result=='NoAuthorized':
                div_content = 'Cuenta no autorizada aun, intentelo mas tarde'
                context['div_content'] = div_content
                return render(request, 'login.html', context)
            else:
                print("True")
                request.session['usuario'] =  result
                userid = request.session['usuario']
                context= {'usuario': result, 'id': userid['localId']}
                return redirect('compras')
        else:
            div_content = 'Error forma invalida, verifica el correo'
            context['div_content'] = div_content
            return render(request, 'login.html', context)
    return render(request, "login.html", context)
    

def miCuenta(request):
    sesion = request.session['usuario']
    if sesion == "NoExist":
        return redirect('home')
    
    user = request.session['usuario']
    info = infoUser(user['localId'])
    context = {}
    context['info']=info
    return render(request, "infoUser.html", context)

def signUp(request):
    print('enter signup')
    form = signUpForm()
    context = {"form": form, "title": "signup"}
    print(request)
    if request.method=='POST':
        print('enter req')
        form = signUpForm(request.POST, request.FILES)
        context = {"form": form, "title": "signup"}
        if form.is_valid():
            print("Form valid")
            data = form.cleaned_data
            mail= data["mail"]
            mail2= data["c_mail"]
            passw= data["password"]
            passw2= data["c_password"]
            if mail != mail2 and passw != passw2:
              context = {"form": form, "title": "signup"}
              return render(request, "signup.html", context)
            result =signUp_Firebase(mail, passw)
            if result == False:
                print("False")
                return render(request, 'signup.html', context)
            else:
                print("True")
                try:
                    uid = result['localId']
                    #idtoken = request.session['uid']
                    print(uid)
                    date = data['birthDate']
                    date_time = date.strftime("%m/%d/%Y")
                    uData = {'name': data['name'], 'lastNames':data['lastNames'],  'birthDate': date_time,
                            'curp': data['curp'], 'oficial_id': uid, 'directions': [data['direction1']],
                            'country': data['country'], 'city': data['city'], 'state': data['state'],
                            'postalCode': data['postalCode'], 'phoneNumber': data['phoneNumber'], 'mail': data['mail'], 'status': True, 'maindirection': data['direction1']}
                    ref = firestore_connection('users')
                    ref.document(uid).set(uData)

                    createCart = firestore_connection('cart')
                    emptyCart = {'items':[]}
                    createCart.document(uid).set(emptyCart)

                    #Uploads file to fireabse
                    #print('attemp to upload img')
                    #print(request.FILES)
                    officialID = request.FILES['official_id']#Gets specific file from reques.FILES
                    #print('get id from request',officialID)
                    file_save = default_storage.save(officialID.name, officialID)#Saves file to local storage with default_storage
                    #print('saved img')
                    #print(officialID.name)
                    storeOfficialID(uid, officialID.name)#Calls function in utils.py
                    #print('stored to firebase')
                    default_storage.delete(officialID.name)#Deletes file from local storage

                    context= {'usuario': result, 'id': result['localId']}
                    return redirect('home')
                    #return render(request, "signup.html", context) Qwerty*1234
                except Exception as e:
                    print('error: ',e)
                    print('failed create')
        print('not valid')
    print('fail')
    return render(request, "signup.html", context)
  
def updateInfo(request):
    print('enter signup')
    form = updateInfoForm()
    context = {"form": form, "title": "signup"}
    print(request)
    if request.method == 'POST':
        print('enter req')
        form = updateInfoForm(request.POST, request.FILES)
        context = {"form": form, "title": "signup"}
        if form.is_valid():
            print("Form valid")
            data = form.cleaned_data
            sesion = request.session['usuario']
            uid = sesion['localId']
            # Obtén el UID del usuario activo desde la sesión
            print("UID es : ", uid)
            user = firestore_connection("users").document(uid).get()
            try:
                # Actualiza los campos específicos del documento existente
                newData = {
                    'name': data['name'],
                    'lastNames': data['lastNames'],
                    'city': data['city'],
                    'state': data['state'],
                    'country': data['country'],
                    'phoneNumber': data['phoneNumber'],
                    'postalCode': data['postalCode']
                }
                ref = firestore_connection('users').document(uid)
                ref.update(newData)
                
                return redirect ('miCuenta')

            except Exception as e:
                print('error: ', e)
                print('failed create')
        print('not valid')
    print('fail')
    return render(request, "updateInfoUser.html", context)

    
def addDirection(request):
    form = directionForm()
    context = {"form": form, "title": "AddDirection"}
    sesion = request.session['usuario']
    if sesion == "NoExist":
        return redirect('home')
    if request.method == 'POST':
        form = directionForm(request.POST)
        context = {"form": form, "title": "AddDirection"}
        if form.is_valid():
            data = form.cleaned_data
            direction = data['campo']
            addDirect(sesion, direction)
            return redirect('compras')
        
    else:      
        return render(request, "addDirection.html", context)
      
def addList (request):
    form = ListForm()
    context = {"form": form, "title": "AddList"}
    sesion = request.session['usuario']
    if sesion == "NoExist":
        return redirect('home')
    if request.method == 'POST':
        form =  ListForm(request.POST)
        context = {"form": form, "title": "AddList"}
        if form.is_valid():
            data = form.cleaned_data
            lista = data['campo']
            addLista(sesion, lista)
            return redirect('compras')
        
    else:      
        return render(request, "addList.html", context)

def MiLista(request):
  sesion = request.session['usuario']
  if sesion == "NoExist":
    return redirect('home')
    
  lista = request.GET.get('lista')
  products = searchList(lista, sesion)
  if products == []:
    context = {
      'products': products,
      'title' : lista,
      "alert" : "No hay Productos en la lista"
    }
  else:
    context = {
      'products': products,
      'title' : lista,
      "alert" : ""
    }
  return render(request, "miLista.html", context)


def logo (request):
  json_data ='''[
  {
    "categoria": "Alimentos y Bebidas",
    "subcategorias": [
      {
        "categoria": "Aceites, Vinagres y Aderezos",
        "subcategorias": [
          {
            "categoria": "Aceites",
            "subcategorias": []
          },
          {
            "categoria": "Aderezos",
            "subcategorias": []
          },
          {
            "categoria": "Crema para Ensalada",
            "subcategorias": []
          },
          {
            "categoria": "Ingredientes Adicionales para Ensaladas",
            "subcategorias": []
          },
          {
            "categoria": "Sprays de Cocina",
            "subcategorias": []
          },
          {
            "categoria": "Vinagres",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Arroz, Frijoles y Pasta",
        "subcategorias": [
          {
            "categoria": "Arroces",
            "subcategorias": []
          },
          {
            "categoria": "Integrales",
            "subcategorias": []
          },
          {
            "categoria": "Frijoles Secos",
            "subcategorias": []
          },
          {
            "categoria": "Pastas y Fideos",
            "subcategorias": []
          },
          {
            "categoria": "Sagos",
            "subcategorias": []
          },
          {
            "categoria": "Cusc\u00fas",
            "subcategorias": []
          },
          {
            "categoria": "Mochi",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Botanas y Dulces",
        "subcategorias": [
          {
            "categoria": "Chocolates",
            "subcategorias": []
          },
          {
            "categoria": "Dulces y Chicles",
            "subcategorias": []
          },
          {
            "categoria": "Frutas Secas y Vegetales Deshidratados",
            "subcategorias": []
          },
          {
            "categoria": "Mezcla para Fiestas",
            "subcategorias": []
          },
          {
            "categoria": "Nueces y Semillas",
            "subcategorias": []
          },
          {
            "categoria": "Palomitas",
            "subcategorias": []
          },
          {
            "categoria": "Papas Fritas",
            "subcategorias": []
          },
          {
            "categoria": "Snacks",
            "subcategorias": []
          },
          {
            "categoria": "Surtidos de Frutos Secos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Caf\u00e9, T\u00e9 y Bebidas",
        "subcategorias": [
          {
            "categoria": "Aguas",
            "subcategorias": []
          },
          {
            "categoria": "Bebidas con Sabor a Fruta",
            "subcategorias": []
          },
          {
            "categoria": "Bebidas Energ\u00e9ticas",
            "subcategorias": []
          },
          {
            "categoria": "Bebidas para Deportistas",
            "subcategorias": []
          },
          {
            "categoria": "Caf\u00e9",
            "subcategorias": []
          },
          {
            "categoria": "Caf\u00e9 Fr\u00edo y T\u00e9 Fr\u00edo",
            "subcategorias": []
          },
          {
            "categoria": "Chocolate Caliente y Malteadas",
            "subcategorias": []
          },
          {
            "categoria": "Crema",
            "subcategorias": []
          },
          {
            "categoria": "Gaseosa de Jengibre y Cerveza",
            "subcategorias": []
          },
          {
            "categoria": "Jarabes y Concentrados para Bebidas",
            "subcategorias": []
          },
          {
            "categoria": "Jugos",
            "subcategorias": []
          },
          {
            "categoria": "Mezclas para Cocktail",
            "subcategorias": []
          },
          {
            "categoria": "Mezclas y Saborizantes de Bebidas",
            "subcategorias": []
          },
          {
            "categoria": "Refrescos con Gas",
            "subcategorias": []
          },
          {
            "categoria": "Sustitutos de Caf\u00e9",
            "subcategorias": []
          },
          {
            "categoria": "T\u00e9",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Cereales y Muesli",
        "subcategorias": [
          {
            "categoria": "Avenas y Gachas",
            "subcategorias": []
          },
          {
            "categoria": "Barritas",
            "subcategorias": []
          },
          {
            "categoria": "Barritas y Granola",
            "subcategorias": []
          },
          {
            "categoria": "Cereales de Alta Fibra",
            "subcategorias": []
          },
          {
            "categoria": "Cereales de Arroz",
            "subcategorias": []
          },
          {
            "categoria": "Cereales de Trigo",
            "subcategorias": []
          },
          {
            "categoria": "Cereales para Ni\u00f1os",
            "subcategorias": []
          },
          {
            "categoria": "Cereales para Tomar en Fr\u00edo",
            "subcategorias": []
          },
          {
            "categoria": "Gachas de Ma\u00edz",
            "subcategorias": []
          },
          {
            "categoria": "Muesli y Cereales Granola",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Cervezas, Vinos y Licores",
        "subcategorias": [
          {
            "categoria": "Bebidas y Cocteles Premezclados",
            "subcategorias": []
          },
          {
            "categoria": "Cervezas",
            "subcategorias": []
          },
          {
            "categoria": "Bebidas Espiritosas",
            "subcategorias": []
          },
          {
            "categoria": "Sakes y Licores de Arroz",
            "subcategorias": []
          },
          {
            "categoria": "Sidras",
            "subcategorias": []
          },
          {
            "categoria": "Vinos",
            "subcategorias": []
          },
          {
            "categoria": "Vinos Espumosos y Champanes",
            "subcategorias": []
          },
          {
            "categoria": "Vinos Fortificados y de Postre",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Comida Enlatada, Envasada o Empaquetada",
        "subcategorias": [
          {
            "categoria": "Caldos",
            "subcategorias": []
          },
          {
            "categoria": "Carnes, Pescados y Mariscos",
            "subcategorias": []
          },
          {
            "categoria": "Comida Encurtida",
            "subcategorias": []
          },
          {
            "categoria": "Comidas y Guarniciones Preparadas",
            "subcategorias": []
          },
          {
            "categoria": "Condimentos Encurtidos",
            "subcategorias": []
          },
          {
            "categoria": "Fruta",
            "subcategorias": []
          },
          {
            "categoria": "Legumbres",
            "subcategorias": []
          },
          {
            "categoria": "Pasta Enlatada",
            "subcategorias": []
          },
          {
            "categoria": "Sopas",
            "subcategorias": []
          },
          {
            "categoria": "Sustitutos de Carne",
            "subcategorias": []
          },
          {
            "categoria": "Verduras",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Comida para Beb\u00e9",
        "subcategorias": [
          {
            "categoria": "Bebidas y Batidos",
            "subcategorias": []
          },
          {
            "categoria": "Cereales y Gachas de Avena",
            "subcategorias": []
          },
          {
            "categoria": "Comidas Preparadas y Acompa\u00f1amientos",
            "subcategorias": []
          },
          {
            "categoria": "F\u00f3rmula",
            "subcategorias": []
          },
          {
            "categoria": "Snacks, Refrigerios y Galletas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Hierbas, Especias y Condimentos",
        "subcategorias": [
          {
            "categoria": "Especias y Condimentos en Polvo",
            "subcategorias": []
          },
          {
            "categoria": "Especias y Hierbas Sin Moler",
            "subcategorias": []
          },
          {
            "categoria": "Pimientas",
            "subcategorias": []
          },
          {
            "categoria": "Sal y Sustitutos",
            "subcategorias": []
          },
          {
            "categoria": "Sasonadores",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Ingredientes para Cerveza y Vino Caseros",
        "subcategorias": [
          {
            "categoria": "Destilaci\u00f3n de Vino",
            "subcategorias": []
          },
          {
            "categoria": "Fabricaci\u00f3n de Cerveza",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Ingredientes para Cocina y Reposter\u00eda",
        "subcategorias": [
          {
            "categoria": "Aceites, Vinagres y Aerosoles de Cocina",
            "subcategorias": []
          },
          {
            "categoria": "Algas Secas y Noris",
            "subcategorias": []
          },
          {
            "categoria": "Espesantes",
            "subcategorias": []
          },
          {
            "categoria": "Frutas Secas y Vegetales Deshidratados",
            "subcategorias": []
          },
          {
            "categoria": "Ingredientes para Reposteria",
            "subcategorias": []
          },
          {
            "categoria": "Leche y Crema de Coco",
            "subcategorias": []
          },
          {
            "categoria": "Levadura Nutritiva",
            "subcategorias": []
          },
          {
            "categoria": "Manteca y Grasa Alimentaria",
            "subcategorias": []
          },
          {
            "categoria": "Pan Molido",
            "subcategorias": []
          },
          {
            "categoria": "Pescados y Mariscos Secos",
            "subcategorias": []
          },
          {
            "categoria": "Sustitutos del Huevo",
            "subcategorias": []
          },
          {
            "categoria": "Vinos para Cocinar",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Mermeladas, Miel y Untables",
        "subcategorias": [
          {
            "categoria": "Chocolate y Avellanas Cubiertas",
            "subcategorias": []
          },
          {
            "categoria": "Chocolates para Untar",
            "subcategorias": []
          },
          {
            "categoria": "Cubierta de Extracto de Levadura",
            "subcategorias": []
          },
          {
            "categoria": "Cubierta de Malvavisco",
            "subcategorias": []
          },
          {
            "categoria": "Fruta para Untar",
            "subcategorias": []
          },
          {
            "categoria": "Mantequilla de Maple",
            "subcategorias": []
          },
          {
            "categoria": "Mantequillas a Base de Frutos Secos",
            "subcategorias": []
          },
          {
            "categoria": "Reques\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Salsas para Untar",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Panader\u00eda",
        "subcategorias": [
          {
            "categoria": "Pan Crujiente",
            "subcategorias": []
          },
          {
            "categoria": "Tortillas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Productos L\u00e1cteos, Huevos y Alternativas a base de Plantas",
        "subcategorias": [
          {
            "categoria": "Crema",
            "subcategorias": []
          },
          {
            "categoria": "Cremas de Caf\u00e9 a base de Plantas",
            "subcategorias": []
          },
          {
            "categoria": "Leche",
            "subcategorias": []
          },
          {
            "categoria": "Leche a base de Plantas",
            "subcategorias": []
          },
          {
            "categoria": "Leche Saborizada",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Salsas",
        "subcategorias": [
          {
            "categoria": "Condimentos",
            "subcategorias": []
          },
          {
            "categoria": "Glaces y Demi-Glaces",
            "subcategorias": []
          },
          {
            "categoria": "Glaseados",
            "subcategorias": []
          },
          {
            "categoria": "Salsas Gravy",
            "subcategorias": []
          },
          {
            "categoria": "Salsas para Cocinar",
            "subcategorias": []
          },
          {
            "categoria": "Salsas Picantes",
            "subcategorias": []
          },
          {
            "categoria": "Wasabi",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Otros",
        "subcategorias": [
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      }
    ]
  },
  {
    "categoria": "Auto",
    "subcategorias": [
      {
        "categoria": "Accesorios para Coche",
        "subcategorias": [
          {
            "categoria": "Accesorios Exteriores",
            "subcategorias": []
          },
          {
            "categoria": "Accesorios para Caja de Pick Up",
            "subcategorias": []
          },
          {
            "categoria": "Adaptadores de entrada",
            "subcategorias": []
          },
          {
            "categoria": "Almacenamiento y Organizaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Aromatizantes",
            "subcategorias": []
          },
          {
            "categoria": "Asistencia en el Camino",
            "subcategorias": []
          },
          {
            "categoria": "Calcoman\u00edas y Emblemas",
            "subcategorias": []
          },
          {
            "categoria": "Carcasas para Llaves",
            "subcategorias": []
          },
          {
            "categoria": "Difusor de Aroma",
            "subcategorias": []
          },
          {
            "categoria": "Estribos y Escalones",
            "subcategorias": []
          },
          {
            "categoria": "Inversores de Corriente",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Interiores",
            "subcategorias": []
          },
          {
            "categoria": "Productos de Invierno",
            "subcategorias": []
          },
          {
            "categoria": "Productos de Tracci\u00f3n y Winches",
            "subcategorias": []
          },
          {
            "categoria": "Protecci\u00f3n Antirrobo",
            "subcategorias": []
          },
          {
            "categoria": "Recipientes para Gasolina",
            "subcategorias": []
          },
          {
            "categoria": "Rejillas y Protectores para Rejillas",
            "subcategorias": []
          },
          {
            "categoria": "Repelentes Automotrices de Plagas",
            "subcategorias": []
          },
          {
            "categoria": "Sistemas y Accesorios de Carga",
            "subcategorias": []
          },
          {
            "categoria": "Soportes, Cubreasientos y Fundas",
            "subcategorias": []
          },
          {
            "categoria": "Tapetes y Alfombras",
            "subcategorias": []
          },
          {
            "categoria": "Term\u00f3metros",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Aceites y Otros Fluidos",
        "subcategorias": [
          {
            "categoria": "Aceites",
            "subcategorias": []
          },
          {
            "categoria": "Aditivos",
            "subcategorias": []
          },
          {
            "categoria": "Anticongelantes para Frenos",
            "subcategorias": []
          },
          {
            "categoria": "Anticongelantes para Radiador",
            "subcategorias": []
          },
          {
            "categoria": "L\u00edquidos para Diracci\u00f3n Asistida",
            "subcategorias": []
          },
          {
            "categoria": "L\u00edquidos de Servicio",
            "subcategorias": []
          },
          {
            "categoria": "Lubricantes",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Cuidado de Coche y Moto",
        "subcategorias": [
          {
            "categoria": "Adhesivos y Selladores",
            "subcategorias": []
          },
          {
            "categoria": "Cuidado del Motor",
            "subcategorias": []
          },
          {
            "categoria": "Kits de Limpieza",
            "subcategorias": []
          },
          {
            "categoria": "Limpieza de Ventanillas",
            "subcategorias": []
          },
          {
            "categoria": "Productos de Cuidado Exterior",
            "subcategorias": []
          },
          {
            "categoria": "Productos de Cuidado Interior",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Herramientas para Coche",
        "subcategorias": [
          {
            "categoria": "Compresores de Muelles",
            "subcategorias": []
          },
          {
            "categoria": "Equipo y Herramientas de Garaje",
            "subcategorias": []
          },
          {
            "categoria": "Equipo y Herramientas para Sistemas de Aceite",
            "subcategorias": []
          },
          {
            "categoria": "Extractores y Separadores",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas de Diagnostico, Escaneo y Especialidad",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas de Direcci\u00f3n y Suspensi\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas de Frenos",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas de Llantas y Rines",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas de Mano",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas de Reparaci\u00f3n del Parachoques y Carrocer\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas del Embrague",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas del Limpiaparabrisas",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas del Parabrisas",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas del Sistema de Combustible",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas para Bater\u00edas",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas y Equipos de Aire Acondicionado",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas y Equipos de Motor",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Herramientas",
            "subcategorias": []
          },
          {
            "categoria": "Kits de Reparaci\u00f3n de Roscas",
            "subcategorias": []
          },
          {
            "categoria": "Llaves de Impacto",
            "subcategorias": []
          },
          {
            "categoria": "Remachadoras",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Llantas y Rines para Coche",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas de Neum\u00e1ticos y Ruedas",
            "subcategorias": []
          },
          {
            "categoria": "Llantas",
            "subcategorias": []
          },
          {
            "categoria": "Rines",
            "subcategorias": []
          },
          {
            "categoria": "Ruedas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Motos, Accesorios y Piezas",
        "subcategorias": [
          {
            "categoria": "Accesorios y Piezas",
            "subcategorias": []
          },
          {
            "categoria": "Partes y Refacciones",
            "subcategorias": []
          },
          {
            "categoria": "Seguridad",
            "subcategorias": []
          },
          {
            "categoria": "Illuminaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "LLantas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Partes y Refacciones",
        "subcategorias": [
          {
            "categoria": "Acondicionamiento Interior",
            "subcategorias": []
          },
          {
            "categoria": "Alternadores y Generadores",
            "subcategorias": []
          },
          {
            "categoria": "Arranque y Piezas del Motor",
            "subcategorias": []
          },
          {
            "categoria": "Cables",
            "subcategorias": []
          },
          {
            "categoria": "Correas y Tensores",
            "subcategorias": []
          },
          {
            "categoria": "Direcci\u00f3n y Suspensi\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Embellecedores y Accesorios para Carrocer\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Encendido y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Filtros",
            "subcategorias": []
          },
          {
            "categoria": "Frenos",
            "subcategorias": []
          },
          {
            "categoria": "Limpiaparabrisas y Partes",
            "subcategorias": []
          },
          {
            "categoria": "Luces, Bombillas e Indicadores",
            "subcategorias": []
          },
          {
            "categoria": "Motores",
            "subcategorias": []
          },
          {
            "categoria": "Motores y Piezas del Motor",
            "subcategorias": []
          },
          {
            "categoria": "Sensores",
            "subcategorias": []
          },
          {
            "categoria": "Sistemas de Escape Cat-Back",
            "subcategorias": []
          },
          {
            "categoria": "Tapas y Tapones",
            "subcategorias": []
          },
          {
            "categoria": "Tracci\u00f3n y Transmisi\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Pinturas y Accesorios de Pintura",
        "subcategorias": [
          {
            "categoria": "Pinturas en Spray",
            "subcategorias": []
          },
          {
            "categoria": "Pinturas en Acabado",
            "subcategorias": []
          },
          {
            "categoria": "Pistolas y Accesorios de Pintura",
            "subcategorias": []
          },
          {
            "categoria": "Aditivos",
            "subcategorias": []
          },
          {
            "categoria": "Cintas Adhesivas",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas de Pintura",
            "subcategorias": []
          },
          {
            "categoria": "Lacas para Pinzas de Frenos",
            "subcategorias": []
          },
          {
            "categoria": "Materiales de Esmerilado",
            "subcategorias": []
          },
          {
            "categoria": "Materiales de Revestimiento",
            "subcategorias": []
          },
          {
            "categoria": "Materiales para Tareas de Pintura",
            "subcategorias": []
          },
          {
            "categoria": "Pinturas para Retoques",
            "subcategorias": []
          },
          {
            "categoria": "Primers",
            "subcategorias": []
          },
          {
            "categoria": "Productos de Limpieza",
            "subcategorias": []
          },
          {
            "categoria": "Protecci\u00f3n para Tareas de Pintura",
            "subcategorias": []
          },
          {
            "categoria": "Rotuladores",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Sillas de Beb\u00e9 y Accesorios",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Sillas de Coche",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Transporte y Almacenamiento",
        "subcategorias": [
          {
            "categoria": "Canastillas y Portaequipajes",
            "subcategorias": []
          },
          {
            "categoria": "Bandas de Tensi\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Banderines de Seguridad",
            "subcategorias": []
          },
          {
            "categoria": "Cables y Adaptadores",
            "subcategorias": []
          },
          {
            "categoria": "Enganches de Remolque y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Escaleras para Camioneta",
            "subcategorias": []
          },
          {
            "categoria": "Escaleras para Compuerta Trasera",
            "subcategorias": []
          },
          {
            "categoria": "Rampas de Carga",
            "subcategorias": []
          },
          {
            "categoria": "Remolques",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Otros",
        "subcategorias": [
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      }
    ]
  },
  {
    "categoria": "Bebes",
    "subcategorias": [
      {
        "categoria": "Actividad y Entretenimiento",
        "subcategorias": [
          {
            "categoria": "Alfombras de Juego y Gimnasios",
            "subcategorias": []
          },
          {
            "categoria": "Andaderas",
            "subcategorias": []
          },
          {
            "categoria": "Centros de Actividades",
            "subcategorias": []
          },
          {
            "categoria": "Columpios Interiores",
            "subcategorias": []
          },
          {
            "categoria": "Libros Blandos",
            "subcategorias": []
          },
          {
            "categoria": "M\u00f3viles",
            "subcategorias": []
          },
          {
            "categoria": "Sillas Mecedoras",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Bacinicas y Taburetes",
        "subcategorias": [
          {
            "categoria": "Accesorios de Ayuda para Aprender a ir al Ba\u00f1o",
            "subcategorias": []
          },
          {
            "categoria": "Asientos Reductores de WC",
            "subcategorias": []
          },
          {
            "categoria": "Bacinicas",
            "subcategorias": []
          },
          {
            "categoria": "Pa\u00f1ales Desechables Entrenadores",
            "subcategorias": []
          },
          {
            "categoria": "Toallitas H\u00famedas",
            "subcategorias": []
          },
          {
            "categoria": "Toallitas Secas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Cambio de Pa\u00f1ales",
        "subcategorias": [
          {
            "categoria": "Cambiadores de Pa\u00f1ales",
            "subcategorias": []
          },
          {
            "categoria": "Cambiadores de Pa\u00f1ales T\u00e9rmicos",
            "subcategorias": []
          },
          {
            "categoria": "Colchones y Cobijas para Cambiar Pa\u00f1ales",
            "subcategorias": []
          },
          {
            "categoria": "Contenedores y Repuestos de Pa\u00f1ales",
            "subcategorias": []
          },
          {
            "categoria": "Cremas para Rozaduras",
            "subcategorias": []
          },
          {
            "categoria": "Organizadores y Guardapa\u00f1ales",
            "subcategorias": []
          },
          {
            "categoria": "Pa\u00f1aleras",
            "subcategorias": []
          },
          {
            "categoria": "Pa\u00f1ales",
            "subcategorias": []
          },
          {
            "categoria": "Toallitas y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Carriolas y Cochecitos",
        "subcategorias": [
          {
            "categoria": "Canastas para Beb\u00e9s",
            "subcategorias": []
          },
          {
            "categoria": "Carriolas Deportivas",
            "subcategorias": []
          },
          {
            "categoria": "Coches de paseo",
            "subcategorias": []
          },
          {
            "categoria": "Conjunto de silla de coche y carrito",
            "subcategorias": []
          },
          {
            "categoria": "Piezas y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Sillas de paseo",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Chupones y Mordederas",
        "subcategorias": [
          {
            "categoria": "Accesorios para Chupones",
            "subcategorias": []
          },
          {
            "categoria": "Chupones",
            "subcategorias": []
          },
          {
            "categoria": "Mordederas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Higiene y Cuidado",
        "subcategorias": [
          {
            "categoria": "Ba\u00f1o",
            "subcategorias": []
          },
          {
            "categoria": "B\u00e1sculas",
            "subcategorias": []
          },
          {
            "categoria": "Cuidado de la Piel",
            "subcategorias": []
          },
          {
            "categoria": "Cuidado para el Cabello",
            "subcategorias": []
          },
          {
            "categoria": "Higiene",
            "subcategorias": []
          },
          {
            "categoria": "Term\u00f3metros",
            "subcategorias": []
          },
          {
            "categoria": "Toallitas y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Tratamientos de Fr\u00edo y Calor",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Lactancia y Alimentaci\u00f3n",
        "subcategorias": [
          {
            "categoria": "Accesorios para la Lactancia",
            "subcategorias": []
          },
          {
            "categoria": "Alimentos para Beb\u00e9s",
            "subcategorias": []
          },
          {
            "categoria": "Baberos y Pa\u00f1os",
            "subcategorias": []
          },
          {
            "categoria": "B\u00e1sculas de Cocina para Beb\u00e9",
            "subcategorias": []
          },
          {
            "categoria": "Biberones y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Calentadores de Comida",
            "subcategorias": []
          },
          {
            "categoria": "Delantales para Ni\u00f1os",
            "subcategorias": []
          },
          {
            "categoria": "Licuadoras, Procesadores de Alimentos y Prensas de Cocina",
            "subcategorias": []
          },
          {
            "categoria": "Pa\u00f1os de Muselina",
            "subcategorias": []
          },
          {
            "categoria": "Recipientes de Comida",
            "subcategorias": []
          },
          {
            "categoria": "Sillas de Beb\u00e9, Asientos y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Vajilla y Cubiertos",
            "subcategorias": []
          },
          {
            "categoria": "Vasos Entrenadores",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Portabeb\u00e9s y Accesorios",
        "subcategorias": [
          {
            "categoria": "Accesorios de Portabeb\u00e9s",
            "subcategorias": []
          },
          {
            "categoria": "Cabestrillos Portabeb\u00e9s",
            "subcategorias": []
          },
          {
            "categoria": "Mochilas de Senderismo",
            "subcategorias": []
          },
          {
            "categoria": "Portabeb\u00e9s para Beb\u00e9s y Ni\u00f1os peque\u00f1os",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Rec\u00e1mara del Beb\u00e9",
        "subcategorias": [
          {
            "categoria": "Decoraci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Muebles",
            "subcategorias": []
          },
          {
            "categoria": "Ropa de Cama",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Regalos para Reci\u00e9n Nacidos",
        "subcategorias": [
          {
            "categoria": "\u00c1lbumes de Fotos",
            "subcategorias": []
          },
          {
            "categoria": "\u00c1lbumes de Recuerdos",
            "subcategorias": []
          },
          {
            "categoria": "Beb\u00e9s Ni\u00f1a",
            "subcategorias": []
          },
          {
            "categoria": "Beb\u00e9s Ni\u00f1o",
            "subcategorias": []
          },
          {
            "categoria": "Cajas de Recuerdos para Reci\u00e9n Nacidos",
            "subcategorias": []
          },
          {
            "categoria": "Calcoman\u00edas de Beb\u00e9 a Bordo para el Coche",
            "subcategorias": []
          },
          {
            "categoria": "Joyer\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Regalos para Reci\u00e9n Nacidos",
            "subcategorias": []
          },
          {
            "categoria": "Kits de Modelado e Impresi\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Marcos de Fotos",
            "subcategorias": []
          },
          {
            "categoria": "M\u00f3viles",
            "subcategorias": []
          },
          {
            "categoria": "Recuerdos para Bautizos",
            "subcategorias": []
          },
          {
            "categoria": "Sobres para Tarjetas de Maternidad",
            "subcategorias": []
          },
          {
            "categoria": "Velas para Bautizos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Ropa de Maternidad",
        "subcategorias": [
          {
            "categoria": "Faldas",
            "subcategorias": []
          },
          {
            "categoria": "Lactancia",
            "subcategorias": []
          },
          {
            "categoria": "Leggings",
            "subcategorias": []
          },
          {
            "categoria": "Lencer\u00eda y Ropa Interior",
            "subcategorias": []
          },
          {
            "categoria": "Pantalones",
            "subcategorias": []
          },
          {
            "categoria": "Pantalones de Mezclilla",
            "subcategorias": []
          },
          {
            "categoria": "Playeras y Tops",
            "subcategorias": []
          },
          {
            "categoria": "Ropa Deportiva",
            "subcategorias": []
          },
          {
            "categoria": "Sueteres y Tejidos",
            "subcategorias": []
          },
          {
            "categoria": "Trajes de Ba\u00f1o",
            "subcategorias": []
          },
          {
            "categoria": "Vestidos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Seguridad",
        "subcategorias": [
          {
            "categoria": "Arneses de Seguridad",
            "subcategorias": []
          },
          {
            "categoria": "Barandillas para Camas",
            "subcategorias": []
          },
          {
            "categoria": "Barreras de Puerta y Extensiones",
            "subcategorias": []
          },
          {
            "categoria": "Humidificadores",
            "subcategorias": []
          },
          {
            "categoria": "Monitor para Beb\u00e9s",
            "subcategorias": []
          },
          {
            "categoria": "Monitores Fetales",
            "subcategorias": []
          },
          {
            "categoria": "Orejeras de Protecci\u00f3n Auditiva",
            "subcategorias": []
          },
          {
            "categoria": "Pilas para Monitor para Beb\u00e9s",
            "subcategorias": []
          },
          {
            "categoria": "Protecciones y Cerraduras",
            "subcategorias": []
          },
          {
            "categoria": "Seguridad y Protecciones para Cuartos de Ba\u00f1o",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Sillas de Coche y Accesorios",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Sillas de Coche",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Otros",
        "subcategorias": [
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      }
    ]
  },
  {
    "categoria": "Belleza",
    "subcategorias": [
      {
        "categoria": "Ba\u00f1o y Cuerpo",
        "subcategorias": [
          {
            "categoria": "Accesorios Ba\u00f1o y Cuerpo",
            "subcategorias": []
          },
          {
            "categoria": "Aditivos para el Ba\u00f1o",
            "subcategorias": []
          },
          {
            "categoria": "Desodorantes y Antitranspirantes",
            "subcategorias": []
          },
          {
            "categoria": "Exfoliantes y Tratamientos Corporales",
            "subcategorias": []
          },
          {
            "categoria": "Limpieza Personal",
            "subcategorias": []
          },
          {
            "categoria": "Sets",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Cosm\u00e9ticos",
        "subcategorias": [
          {
            "categoria": "Accesorios y Utensilios para Maquillaje",
            "subcategorias": []
          },
          {
            "categoria": "Cara",
            "subcategorias": []
          },
          {
            "categoria": "Cuerpo",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Maquillaje",
            "subcategorias": []
          },
          {
            "categoria": "Labios",
            "subcategorias": []
          },
          {
            "categoria": "Ojos",
            "subcategorias": []
          },
          {
            "categoria": "Paletas de Maquillaje",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Cuidado de la Piel",
        "subcategorias": [
          {
            "categoria": "Cara",
            "subcategorias": []
          },
          {
            "categoria": "Cuello y Escote",
            "subcategorias": []
          },
          {
            "categoria": "Cuerpo",
            "subcategorias": []
          },
          {
            "categoria": "Desmaquillantes",
            "subcategorias": []
          },
          {
            "categoria": "Exfoliantes y Tratamientos Corporales",
            "subcategorias": []
          },
          {
            "categoria": "Juegos y Kits",
            "subcategorias": []
          },
          {
            "categoria": "Labios",
            "subcategorias": []
          },
          {
            "categoria": "Manos y Pies",
            "subcategorias": []
          },
          {
            "categoria": "Maternidad",
            "subcategorias": []
          },
          {
            "categoria": "Ojos",
            "subcategorias": []
          },
          {
            "categoria": "Sol",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Cuidado del Cabello",
        "subcategorias": [
          {
            "categoria": "Accesorios para Peinarse",
            "subcategorias": []
          },
          {
            "categoria": "Aceites para el Cabello",
            "subcategorias": []
          },
          {
            "categoria": "Champ\u00fa y Acondicionador",
            "subcategorias": []
          },
          {
            "categoria": "Extensiones de Cabello, Pelucas y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas de Peinado",
            "subcategorias": []
          },
          {
            "categoria": "Instrumentos para Corte de Pelo",
            "subcategorias": []
          },
          {
            "categoria": "Mascarillas para el Cabello",
            "subcategorias": []
          },
          {
            "categoria": "Permanentes y Texturizantes para el Cabello",
            "subcategorias": []
          },
          {
            "categoria": "Productos para la Ca\u00edda del Cabello",
            "subcategorias": []
          },
          {
            "categoria": "Productos para Peinar",
            "subcategorias": []
          },
          {
            "categoria": "Set de Viaje",
            "subcategorias": []
          },
          {
            "categoria": "Sets y Kits",
            "subcategorias": []
          },
          {
            "categoria": "Tintes para el Cabello",
            "subcategorias": []
          },
          {
            "categoria": "Tratamientos de Cuero Cabelludo",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Equipamiento de Sal\u00f3n y Spa",
        "subcategorias": [
          {
            "categoria": "Bolsas y Cajas de Herramientas",
            "subcategorias": []
          },
          {
            "categoria": "Calentadores de Toallas para Spa",
            "subcategorias": []
          },
          {
            "categoria": "Capas",
            "subcategorias": []
          },
          {
            "categoria": "Carritos de Mantenimiento",
            "subcategorias": []
          },
          {
            "categoria": "Casco Secador",
            "subcategorias": []
          },
          {
            "categoria": "Cepillos de Cuello",
            "subcategorias": []
          },
          {
            "categoria": "Escobas y Cepillos",
            "subcategorias": []
          },
          {
            "categoria": "Espejos de Mano",
            "subcategorias": []
          },
          {
            "categoria": "Frascos Atomizadores",
            "subcategorias": []
          },
          {
            "categoria": "Lavabos de Peluquer\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Maniqu\u00edes de Aprendizaje",
            "subcategorias": []
          },
          {
            "categoria": "M\u00e1quinas Galv\u00e1nicas",
            "subcategorias": []
          },
          {
            "categoria": "M\u00e1quinas de Alta Frecuencia",
            "subcategorias": []
          },
          {
            "categoria": "Mesas de Spa",
            "subcategorias": []
          },
          {
            "categoria": "Sillas de Barbero",
            "subcategorias": []
          },
          {
            "categoria": "Sistemas de Almacenamiento para Spa",
            "subcategorias": []
          },
          {
            "categoria": "Taburetes de Sal\u00f3n y Spa",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Manicure y Pedicure",
        "subcategorias": [
          {
            "categoria": "Cuidado de las Manos y los Pies",
            "subcategorias": []
          },
          {
            "categoria": "Dise\u00f1os para U\u00f1as",
            "subcategorias": []
          },
          {
            "categoria": "Quitaesmalte",
            "subcategorias": []
          },
          {
            "categoria": "Tratamientos para U\u00f1as",
            "subcategorias": []
          },
          {
            "categoria": "Utensilios y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Perfumes y Fragancias",
        "subcategorias": [
          {
            "categoria": "Aceite Esencial de Rosa",
            "subcategorias": []
          },
          {
            "categoria": "Atomizadores",
            "subcategorias": []
          },
          {
            "categoria": "Hombres",
            "subcategorias": []
          },
          {
            "categoria": "Infantiles",
            "subcategorias": []
          },
          {
            "categoria": "Mujeres",
            "subcategorias": []
          },
          {
            "categoria": "Perfumes S\u00f3lidos",
            "subcategorias": []
          },
          {
            "categoria": "Polvos con Fragancia",
            "subcategorias": []
          },
          {
            "categoria": "Sets",
            "subcategorias": []
          },
          {
            "categoria": "Velas y Esencias para el Hogar",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Rasurado y Depilaci\u00f3n",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Antes de Rasurarse y Depilarse",
            "subcategorias": []
          },
          {
            "categoria": "Depilaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Despues de Rasurarse y Depilarse",
            "subcategorias": []
          },
          {
            "categoria": "Rasurado Manual",
            "subcategorias": []
          },
          {
            "categoria": "Rasuradoras El\u00e9ctricas",
            "subcategorias": []
          },
          {
            "categoria": "Recortadoras y Rasuradoras Corporales",
            "subcategorias": []
          },
          {
            "categoria": "Tijeras",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Utensilios de Belleza",
        "subcategorias": [
          {
            "categoria": "Atomizadores",
            "subcategorias": []
          },
          {
            "categoria": "Bolitas y Almohadillas de Algod\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas y Estuches",
            "subcategorias": []
          },
          {
            "categoria": "Contenedores Rellenables",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas para el Cuidado de la Piel",
            "subcategorias": []
          },
          {
            "categoria": "Kits de Belleza",
            "subcategorias": []
          },
          {
            "categoria": "Suministros para Piercings y Tatuajes",
            "subcategorias": []
          },
          {
            "categoria": "Utensilios y Accesorios para Maquillaje",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Otros",
        "subcategorias": [
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      }
    ]
  },
  {
    "categoria": "Deportes y Aire libre",
    "subcategorias": [
      {
        "categoria": "Artes Marciales",
        "subcategorias": [
          {
            "categoria": "Artes marciales mixtas",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas para Equipo",
            "subcategorias": []
          },
          {
            "categoria": "Ch\u00e1ndales",
            "subcategorias": []
          },
          {
            "categoria": "Equipo de Entrenamiento",
            "subcategorias": []
          },
          {
            "categoria": "Exhibidores para Cinturones",
            "subcategorias": []
          },
          {
            "categoria": "Jiu-jitsu",
            "subcategorias": []
          },
          {
            "categoria": "Judo",
            "subcategorias": []
          },
          {
            "categoria": "K\u00e1rate",
            "subcategorias": []
          },
          {
            "categoria": "Kendo",
            "subcategorias": []
          },
          {
            "categoria": "Kickboxing",
            "subcategorias": []
          },
          {
            "categoria": "Kung Fu",
            "subcategorias": []
          },
          {
            "categoria": "Ninjutsu",
            "subcategorias": []
          },
          {
            "categoria": "Protecciones",
            "subcategorias": []
          },
          {
            "categoria": "Taekwondo",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Art\u00edculos para Fans",
        "subcategorias": [
          {
            "categoria": "Accesorios para celulares",
            "subcategorias": []
          },
          {
            "categoria": "Basquetbol",
            "subcategorias": []
          },
          {
            "categoria": "Beisbol",
            "subcategorias": []
          },
          {
            "categoria": "Bocinas de aire para estadio",
            "subcategorias": []
          },
          {
            "categoria": "Electr\u00f3nica",
            "subcategorias": []
          },
          {
            "categoria": "Equipo para deporte",
            "subcategorias": []
          },
          {
            "categoria": "Futbol",
            "subcategorias": []
          },
          {
            "categoria": "Futbol Americano",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas y mejoras del hogar",
            "subcategorias": []
          },
          {
            "categoria": "Hockey sobre Hielo",
            "subcategorias": []
          },
          {
            "categoria": "Joyer\u00eda y Relojes",
            "subcategorias": []
          },
          {
            "categoria": "Juguetes y Productos de Sala de Juegos",
            "subcategorias": []
          },
          {
            "categoria": "Memorabilia",
            "subcategorias": []
          },
          {
            "categoria": "Patio, c\u00e9sped y jard\u00edn",
            "subcategorias": []
          },
          {
            "categoria": "Productos de oficina",
            "subcategorias": []
          },
          {
            "categoria": "Productos para el Hogar",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Atletismo",
        "subcategorias": [
          {
            "categoria": "Equipo para Competencias",
            "subcategorias": []
          },
          {
            "categoria": "Equipo para Lanzamientos",
            "subcategorias": []
          },
          {
            "categoria": "Equipo para Saltos",
            "subcategorias": []
          },
          {
            "categoria": "Equipo para la Pista",
            "subcategorias": []
          },
          {
            "categoria": "Tenis",
            "subcategorias": []
          },
          {
            "categoria": "Carritos para Equipos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "B\u00e1dminton",
        "subcategorias": [
          {
            "categoria": "Bolsas para Equipo",
            "subcategorias": []
          },
          {
            "categoria": "Gallitos",
            "subcategorias": []
          },
          {
            "categoria": "Juegos Completos",
            "subcategorias": []
          },
          {
            "categoria": "Raquetas",
            "subcategorias": []
          },
          {
            "categoria": "Redes",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Basquetbol",
        "subcategorias": [
          {
            "categoria": "Accesorios de Cancha",
            "subcategorias": []
          },
          {
            "categoria": "Accesorios para Tablero",
            "subcategorias": []
          },
          {
            "categoria": "Balones",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas para Equipo",
            "subcategorias": []
          },
          {
            "categoria": "Equipo de Entrenamiento",
            "subcategorias": []
          },
          {
            "categoria": "Equipo Protector",
            "subcategorias": []
          },
          {
            "categoria": "Mangas para tirador",
            "subcategorias": []
          },
          {
            "categoria": "Tableros",
            "subcategorias": []
          },
          {
            "categoria": "Tenis",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "B\u00e9isbol",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Accesorios para Bates",
            "subcategorias": []
          },
          {
            "categoria": "Accesorios para Manoplas",
            "subcategorias": []
          },
          {
            "categoria": "Bates",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas para Equipo",
            "subcategorias": []
          },
          {
            "categoria": "Equipo de \u00c1rbitros",
            "subcategorias": []
          },
          {
            "categoria": "Equipo de Entrenamiento",
            "subcategorias": []
          },
          {
            "categoria": "Equipo para el Campo",
            "subcategorias": []
          },
          {
            "categoria": "Equipo para Principiantes",
            "subcategorias": []
          },
          {
            "categoria": "Guantes de Bateo",
            "subcategorias": []
          },
          {
            "categoria": "Manoplas y Manoplas",
            "subcategorias": []
          },
          {
            "categoria": "Pelotas",
            "subcategorias": []
          },
          {
            "categoria": "Protecciones",
            "subcategorias": []
          },
          {
            "categoria": "Zapatos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Billar",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Bolas de Billar",
            "subcategorias": []
          },
          {
            "categoria": "Estuches para Tacos",
            "subcategorias": []
          },
          {
            "categoria": "Fundas para Mesas de Billar",
            "subcategorias": []
          },
          {
            "categoria": "Tacos",
            "subcategorias": []
          },
          {
            "categoria": "Taqueras",
            "subcategorias": []
          },
          {
            "categoria": "Tri\u00e1ngulos y Estantes para Bolas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Boliche",
        "subcategorias": [
          {
            "categoria": "Bolas",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas",
            "subcategorias": []
          },
          {
            "categoria": "Guantes",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Boliche",
            "subcategorias": []
          },
          {
            "categoria": "Pinos",
            "subcategorias": []
          },
          {
            "categoria": "Protecciones",
            "subcategorias": []
          },
          {
            "categoria": "Pulidores para Bolas",
            "subcategorias": []
          },
          {
            "categoria": "Zapatos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Box",
        "subcategorias": [
          {
            "categoria": "Accesorios para Costales",
            "subcategorias": []
          },
          {
            "categoria": "Costales",
            "subcategorias": []
          },
          {
            "categoria": "Equipo de Gimnasio",
            "subcategorias": []
          },
          {
            "categoria": "Guantes",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Box",
            "subcategorias": []
          },
          {
            "categoria": "Paos de boxeo",
            "subcategorias": []
          },
          {
            "categoria": "Patas de oso",
            "subcategorias": []
          },
          {
            "categoria": "Protecciones",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Campismo y Senderismo",
        "subcategorias": [
          {
            "categoria": "Accesorios para Mochilas",
            "subcategorias": []
          },
          {
            "categoria": "Accesorios para Tiendas de Campa\u00f1a",
            "subcategorias": []
          },
          {
            "categoria": "Arrancadores de fuego",
            "subcategorias": []
          },
          {
            "categoria": "Bastones de Senderismo",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas de Acampar",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas, paquetes y accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Calentadores de Pies y Manos",
            "subcategorias": []
          },
          {
            "categoria": "Cocina",
            "subcategorias": []
          },
          {
            "categoria": "Cuidado Personal",
            "subcategorias": []
          },
          {
            "categoria": "Equipo para Dormir de Campismo",
            "subcategorias": []
          },
          {
            "categoria": "GPS y Navegaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Hidrataci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Luces y L\u00e1mparas",
            "subcategorias": []
          },
          {
            "categoria": "Mobiliario de Campismo",
            "subcategorias": []
          },
          {
            "categoria": "Mochilas y Bolsas",
            "subcategorias": []
          },
          {
            "categoria": "Navajas, Cuchillos y Herramientas",
            "subcategorias": []
          },
          {
            "categoria": "Seguridad y Supervivencia",
            "subcategorias": []
          },
          {
            "categoria": "Tiendas de Campa\u00f1a",
            "subcategorias": []
          },
          {
            "categoria": "Tiendas Refugio",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Ciclismo",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Bicicletas",
            "subcategorias": []
          },
          {
            "categoria": "Bicicletas Infantiles y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Calzado",
            "subcategorias": []
          },
          {
            "categoria": "Cascos y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Componentes y Refacciones",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas y Equipo para Bicicleta",
            "subcategorias": []
          },
          {
            "categoria": "Lentes",
            "subcategorias": []
          },
          {
            "categoria": "Luces y Reflectores",
            "subcategorias": []
          },
          {
            "categoria": "Protecciones",
            "subcategorias": []
          },
          {
            "categoria": "Ropa",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Dardos y Dianas",
        "subcategorias": [
          {
            "categoria": "Ca\u00f1as",
            "subcategorias": []
          },
          {
            "categoria": "Dardos",
            "subcategorias": []
          },
          {
            "categoria": "Dardos de Acero",
            "subcategorias": []
          },
          {
            "categoria": "Dardos de Pl\u00e1stico",
            "subcategorias": []
          },
          {
            "categoria": "Dianas",
            "subcategorias": []
          },
          {
            "categoria": "Gabinetes",
            "subcategorias": []
          },
          {
            "categoria": "Plumas",
            "subcategorias": []
          },
          {
            "categoria": "Puntas",
            "subcategorias": []
          },
          {
            "categoria": "Tableros",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Deportes Acu\u00e1ticos",
        "subcategorias": [
          {
            "categoria": "Buceo y Esnorquel",
            "subcategorias": []
          },
          {
            "categoria": "Canotaje",
            "subcategorias": []
          },
          {
            "categoria": "Esqu\u00ed Acu\u00e1tico y Deportes de Arrastre",
            "subcategorias": []
          },
          {
            "categoria": "Kayak",
            "subcategorias": []
          },
          {
            "categoria": "Kitesurf",
            "subcategorias": []
          },
          {
            "categoria": "Nataci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "N\u00e1utica",
            "subcategorias": []
          },
          {
            "categoria": "Remo",
            "subcategorias": []
          },
          {
            "categoria": "Ropa",
            "subcategorias": []
          },
          {
            "categoria": "Surf",
            "subcategorias": []
          },
          {
            "categoria": "Surf a Vela",
            "subcategorias": []
          },
          {
            "categoria": "Surf de Remo",
            "subcategorias": []
          },
          {
            "categoria": "Vela",
            "subcategorias": []
          },
          {
            "categoria": "Wakeboard",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Deportes de Invierno",
        "subcategorias": [
          {
            "categoria": "Esqu\u00ed",
            "subcategorias": []
          },
          {
            "categoria": "Hockey sobre Hielo",
            "subcategorias": []
          },
          {
            "categoria": "Motos de Nieve",
            "subcategorias": []
          },
          {
            "categoria": "Patinaje sobre Hielo",
            "subcategorias": []
          },
          {
            "categoria": "Patinetas para nieve",
            "subcategorias": []
          },
          {
            "categoria": "Snowboard",
            "subcategorias": []
          },
          {
            "categoria": "Snowboarding",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Deportes Ecuestres",
        "subcategorias": [
          {
            "categoria": "Accesorios para el Caballo",
            "subcategorias": []
          },
          {
            "categoria": "Arreos",
            "subcategorias": []
          },
          {
            "categoria": "Cascos",
            "subcategorias": []
          },
          {
            "categoria": "Equipo para Dirigir al Caballo",
            "subcategorias": []
          },
          {
            "categoria": "Fuetes y Cuartas",
            "subcategorias": []
          },
          {
            "categoria": "Guantes de Equitaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Protecciones",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Ejercicio y Acondicionamiento F\u00edsico",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Accesorios para M\u00e1quinas de Acondicionamiento F\u00edsico",
            "subcategorias": []
          },
          {
            "categoria": "Electr\u00f3nica",
            "subcategorias": []
          },
          {
            "categoria": "Entrenadores de Equilibrio",
            "subcategorias": []
          },
          {
            "categoria": "Entrenamiento de velocidad y agilidad",
            "subcategorias": []
          },
          {
            "categoria": "Equipo de Acondicionamiento F\u00edsico Acu\u00e1tico",
            "subcategorias": []
          },
          {
            "categoria": "Equipo de Desarrollo de Fuerza",
            "subcategorias": []
          },
          {
            "categoria": "M\u00e1quinas de Cardio",
            "subcategorias": []
          },
          {
            "categoria": "Pilates",
            "subcategorias": []
          },
          {
            "categoria": "Ropa",
            "subcategorias": []
          },
          {
            "categoria": "Yoga",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Electr\u00f3nica y Dispositivos",
        "subcategorias": [
          {
            "categoria": "Accesorios para Dispositivos",
            "subcategorias": []
          },
          {
            "categoria": "Alt\u00edmetros",
            "subcategorias": []
          },
          {
            "categoria": "Br\u00fajulas",
            "subcategorias": []
          },
          {
            "categoria": "C\u00e1maras de Acci\u00f3n y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Ciclocomputadoras",
            "subcategorias": []
          },
          {
            "categoria": "Cron\u00f3metros",
            "subcategorias": []
          },
          {
            "categoria": "Dispositivos GPS",
            "subcategorias": []
          },
          {
            "categoria": "Estaciones Meteorol\u00f3gicas Port\u00e1tiles",
            "subcategorias": []
          },
          {
            "categoria": "Monitores de Actividad",
            "subcategorias": []
          },
          {
            "categoria": "Pod\u00f3metros",
            "subcategorias": []
          },
          {
            "categoria": "Puls\u00f3metros",
            "subcategorias": []
          },
          {
            "categoria": "Tel\u00e9metros de Golf",
            "subcategorias": []
          },
          {
            "categoria": "Veloc\u00edmetros",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Escalada",
        "subcategorias": [
          {
            "categoria": "Arneses",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas de Magnesio",
            "subcategorias": []
          },
          {
            "categoria": "Cascos",
            "subcategorias": []
          },
          {
            "categoria": "Cuerdas y Correas",
            "subcategorias": []
          },
          {
            "categoria": "Guantes de Escalada",
            "subcategorias": []
          },
          {
            "categoria": "Herrajes para Escalada",
            "subcategorias": []
          },
          {
            "categoria": "Magnesio",
            "subcategorias": []
          },
          {
            "categoria": "Mosquetones",
            "subcategorias": []
          },
          {
            "categoria": "Pies de Gato",
            "subcategorias": []
          },
          {
            "categoria": "Presas de Escalada",
            "subcategorias": []
          },
          {
            "categoria": "Slacklines",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Exhibici\u00f3n y almacenaje de objetos de recuerdo",
        "subcategorias": [
          {
            "categoria": "\u00c1lbumes de Tarjetas",
            "subcategorias": []
          },
          {
            "categoria": "Cajas para Tarjetas",
            "subcategorias": []
          },
          {
            "categoria": "Fundas para Tarjetas",
            "subcategorias": []
          },
          {
            "categoria": "Tornillos de Ajuste de Tarjetas",
            "subcategorias": []
          },
          {
            "categoria": "Vitrinas de objetos de recuerdo deportivos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Futbol",
        "subcategorias": [
          {
            "categoria": "Balones",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas para Equipo",
            "subcategorias": []
          },
          {
            "categoria": "Bolsos y redes para pelotas",
            "subcategorias": []
          },
          {
            "categoria": "Equipo para Entrenar y Jugar",
            "subcategorias": []
          },
          {
            "categoria": "Espinilleras",
            "subcategorias": []
          },
          {
            "categoria": "Guantes de Portero",
            "subcategorias": []
          },
          {
            "categoria": "Porter\u00edas",
            "subcategorias": []
          },
          {
            "categoria": "Redes",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Futbol Americano",
        "subcategorias": [
          {
            "categoria": "Balones",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas para Equipo",
            "subcategorias": []
          },
          {
            "categoria": "Cascos",
            "subcategorias": []
          },
          {
            "categoria": "Cinturones de Banderines de Futbol",
            "subcategorias": []
          },
          {
            "categoria": "Equipo de Entrenamiento",
            "subcategorias": []
          },
          {
            "categoria": "Equipo de Protecci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Guantes",
            "subcategorias": []
          },
          {
            "categoria": "Guantes de Receptor",
            "subcategorias": []
          },
          {
            "categoria": "Haches",
            "subcategorias": []
          },
          {
            "categoria": "Marcadores de Yardas",
            "subcategorias": []
          },
          {
            "categoria": "Ropa",
            "subcategorias": []
          },
          {
            "categoria": "Soportes y Tes para Patada",
            "subcategorias": []
          },
          {
            "categoria": "Uniformes",
            "subcategorias": []
          },
          {
            "categoria": "Zapatos",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Gimnasia",
        "subcategorias": [
          {
            "categoria": "Agarres de Mano",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas para Equipo",
            "subcategorias": []
          },
          {
            "categoria": "Equipo de Competencia",
            "subcategorias": []
          },
          {
            "categoria": "Equipo de Entrenamiento",
            "subcategorias": []
          },
          {
            "categoria": "Magnesio",
            "subcategorias": []
          },
          {
            "categoria": "Ropa",
            "subcategorias": []
          },
          {
            "categoria": "Tapetes y Colchonetas",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Golf",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Accesorios para Bolsas de Palos",
            "subcategorias": []
          },
          {
            "categoria": "Accesorios para Carritos de Golf",
            "subcategorias": []
          },
          {
            "categoria": "Accesorios para el Campo",
            "subcategorias": []
          },
          {
            "categoria": "Bolas",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas de Palos",
            "subcategorias": []
          },
          {
            "categoria": "Calzado",
            "subcategorias": []
          },
          {
            "categoria": "Equipo de Entrenamiento",
            "subcategorias": []
          },
          {
            "categoria": "Guantes",
            "subcategorias": []
          },
          {
            "categoria": "Palos",
            "subcategorias": []
          },
          {
            "categoria": "Piezas para Palos",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Medicina Deportiva",
        "subcategorias": [
          {
            "categoria": "Cilindros de Hule Espuma",
            "subcategorias": []
          },
          {
            "categoria": "Param\u00e9dico y Medicina Deportiva",
            "subcategorias": []
          },
          {
            "categoria": "Protectores Bucales",
            "subcategorias": []
          },
          {
            "categoria": "Suplementos para Deportistas",
            "subcategorias": []
          },
          {
            "categoria": "Tirantes, F\u00e9rulas y Soportes",
            "subcategorias": []
          },
          {
            "categoria": "Tratamientos de Fr\u00edo y Calor",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Patinaje en Tabla",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas para Equipo",
            "subcategorias": []
          },
          {
            "categoria": "Cascos",
            "subcategorias": []
          },
          {
            "categoria": "Cera",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas",
            "subcategorias": []
          },
          {
            "categoria": "Patinetas y Patinetas Giratorias",
            "subcategorias": []
          },
          {
            "categoria": "Piezas de Patinetas",
            "subcategorias": []
          },
          {
            "categoria": "Protecciones",
            "subcategorias": []
          },
          {
            "categoria": "Rampas y Rieles",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Patinaje sobre Ruedas",
        "subcategorias": [
          {
            "categoria": "Cascos",
            "subcategorias": []
          },
          {
            "categoria": "Partes para Patines en L\u00ednea",
            "subcategorias": []
          },
          {
            "categoria": "Patines en L\u00ednea",
            "subcategorias": []
          },
          {
            "categoria": "Patines en Paralelo",
            "subcategorias": []
          },
          {
            "categoria": "Piezas para Patines en Paralelo",
            "subcategorias": []
          },
          {
            "categoria": "Protecciones",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Patines del Diablo y Equipo",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Monopatines autoequilibrantes",
            "subcategorias": []
          },
          {
            "categoria": "Patines del Diablo",
            "subcategorias": []
          },
          {
            "categoria": "Piezas de Patines del Diablo",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Pesca",
        "subcategorias": [
          {
            "categoria": "Aparejos del L\u00edder",
            "subcategorias": []
          },
          {
            "categoria": "Combos de Ca\u00f1a y Carrete",
            "subcategorias": []
          },
          {
            "categoria": "Patos",
            "subcategorias": []
          },
          {
            "categoria": "Pesca con Mosca",
            "subcategorias": []
          },
          {
            "categoria": "Pesca en Hielo",
            "subcategorias": []
          },
          {
            "categoria": "Sedales",
            "subcategorias": []
          },
          {
            "categoria": "Se\u00f1uelos y Moscas",
            "subcategorias": []
          },
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Anzuelos y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Aparejo y Accesorios de Terminal",
            "subcategorias": []
          },
          {
            "categoria": "Calzado",
            "subcategorias": []
          },
          {
            "categoria": "Carretes y accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas",
            "subcategorias": []
          },
          {
            "categoria": "Varillas y accesorios",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Ping Pong",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas para Equipo",
            "subcategorias": []
          },
          {
            "categoria": "Gomas",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Ping Pong",
            "subcategorias": []
          },
          {
            "categoria": "Mesas",
            "subcategorias": []
          },
          {
            "categoria": "Pelotas",
            "subcategorias": []
          },
          {
            "categoria": "Raquetas",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Tenis",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Antivibradores",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas para Equipo",
            "subcategorias": []
          },
          {
            "categoria": "Cordajes",
            "subcategorias": []
          },
          {
            "categoria": "Equipo de Entrenamiento",
            "subcategorias": []
          },
          {
            "categoria": "Mangos de Raquetas",
            "subcategorias": []
          },
          {
            "categoria": "M\u00e1quinas de Pelotas",
            "subcategorias": []
          },
          {
            "categoria": "M\u00e1quinas y Herramientas de Encordado",
            "subcategorias": []
          },
          {
            "categoria": "Pelotas",
            "subcategorias": []
          },
          {
            "categoria": "Raquetas",
            "subcategorias": []
          },
          {
            "categoria": "Recogepelotas",
            "subcategorias": []
          },
          {
            "categoria": "Redes",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Tiro con Arco",
        "subcategorias": [
          {
            "categoria": "Arcos",
            "subcategorias": []
          },
          {
            "categoria": "Botones de Boca",
            "subcategorias": []
          },
          {
            "categoria": "Carcajes",
            "subcategorias": []
          },
          {
            "categoria": "Cuerdas de Arco",
            "subcategorias": []
          },
          {
            "categoria": "Dactileras",
            "subcategorias": []
          },
          {
            "categoria": "Dianas",
            "subcategorias": []
          },
          {
            "categoria": "Disparadores",
            "subcategorias": []
          },
          {
            "categoria": "Dragoneras",
            "subcategorias": []
          },
          {
            "categoria": "Estabilizadores",
            "subcategorias": []
          },
          {
            "categoria": "Estuches de Arco",
            "subcategorias": []
          },
          {
            "categoria": "Flechas y Saetas",
            "subcategorias": []
          },
          {
            "categoria": "Mantenimiento del Arco",
            "subcategorias": []
          },
          {
            "categoria": "Miras",
            "subcategorias": []
          },
          {
            "categoria": "Montadores",
            "subcategorias": []
          },
          {
            "categoria": "Nocks",
            "subcategorias": []
          },
          {
            "categoria": "Plumas para Flechas",
            "subcategorias": []
          },
          {
            "categoria": "Protecciones",
            "subcategorias": []
          },
          {
            "categoria": "Reposaflechas",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Voleibol",
        "subcategorias": [
          {
            "categoria": "Balones",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas para Equipo",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Postes",
            "subcategorias": []
          },
          {
            "categoria": "Redes",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      }
    ]
  },
  {
    "categoria": "Electr\u00f3nicos",
    "subcategorias": [
      {
        "categoria": "Audio y Video Port\u00e1til",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Radio Casetes",
            "subcategorias": []
          },
          {
            "categoria": "Radios y DAB",
            "subcategorias": []
          },
          {
            "categoria": "Receptores de Onda Corta",
            "subcategorias": []
          },
          {
            "categoria": "Reproductores de MP3 y Medios Digitales",
            "subcategorias": []
          },
          {
            "categoria": "Reproductores Personales de Casete",
            "subcategorias": []
          },
          {
            "categoria": "Reproductores Personales de CD",
            "subcategorias": []
          },
          {
            "categoria": "Reproductores Port\u00e1tiles de DVD y Blu-ray",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "C\u00e1maras y Fotograf\u00eda",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Binoculares, Telescopios y \u00d3ptica",
            "subcategorias": []
          },
          {
            "categoria": "C\u00e1maras Anal\u00f3gicas",
            "subcategorias": []
          },
          {
            "categoria": "C\u00e1maras de Acci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "C\u00e1maras de Vigilancia",
            "subcategorias": []
          },
          {
            "categoria": "C\u00e1maras Digitales",
            "subcategorias": []
          },
          {
            "categoria": "C\u00e1maras Montadas en el Cuerpo",
            "subcategorias": []
          },
          {
            "categoria": "C\u00e1maras Simuladas",
            "subcategorias": []
          },
          {
            "categoria": "Drones y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Esc\u00e1neres de Pel\u00edculas y Diapositivas",
            "subcategorias": []
          },
          {
            "categoria": "Flashes",
            "subcategorias": []
          },
          {
            "categoria": "Fotograf\u00eda y V\u00eddeo Subacu\u00e1tico",
            "subcategorias": []
          },
          {
            "categoria": "Impresoras de Fotos",
            "subcategorias": []
          },
          {
            "categoria": "Lentes",
            "subcategorias": []
          },
          {
            "categoria": "Marcos Digitales",
            "subcategorias": []
          },
          {
            "categoria": "Proyectores de Diapositivas",
            "subcategorias": []
          },
          {
            "categoria": "Proyectores de Video",
            "subcategorias": []
          },
          {
            "categoria": "Tr\u00edpodes y Monopies",
            "subcategorias": []
          },
          {
            "categoria": "Videoc\u00e1maras",
            "subcategorias": []
          },
          {
            "categoria": "Videoc\u00e1maras Profesionales",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Celulares y Accesorios",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Banda Ancha M\u00f3vil",
            "subcategorias": []
          },
          {
            "categoria": "Celulares y Smartphones de Prepago",
            "subcategorias": []
          },
          {
            "categoria": "Celulares y Smartphones Desbloqueados",
            "subcategorias": []
          },
          {
            "categoria": "Relojes inteligentes",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Computadoras, Componentes y Accesorios",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Almacenamiento de Datos",
            "subcategorias": []
          },
          {
            "categoria": "Bocinas de Computadora",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas Mensajeras y al Hombro para Tablet",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas Mensajeras y Bolsas al Hombro para Laptop",
            "subcategorias": []
          },
          {
            "categoria": "Componentes",
            "subcategorias": []
          },
          {
            "categoria": "Componentes de Laptop",
            "subcategorias": []
          },
          {
            "categoria": "Componentes Externos",
            "subcategorias": []
          },
          {
            "categoria": "Computadoras de Escritorio",
            "subcategorias": []
          },
          {
            "categoria": "Dispositivos para Redes",
            "subcategorias": []
          },
          {
            "categoria": "Equipo para C\u00e1mara y VoIP",
            "subcategorias": []
          },
          {
            "categoria": "Esc\u00e1neres",
            "subcategorias": []
          },
          {
            "categoria": "Impresoras",
            "subcategorias": []
          },
          {
            "categoria": "Laptops",
            "subcategorias": []
          },
          {
            "categoria": "Mochilas para Laptop",
            "subcategorias": []
          },
          {
            "categoria": "Monitores",
            "subcategorias": []
          },
          {
            "categoria": "PC Semiensamblada",
            "subcategorias": []
          },
          {
            "categoria": "Portafolios para Laptop",
            "subcategorias": []
          },
          {
            "categoria": "Servidores",
            "subcategorias": []
          },
          {
            "categoria": "Tablets",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Electr\u00f3nica para Autos",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Electr\u00f3nica de Autos",
            "subcategorias": []
          },
          {
            "categoria": "Electr\u00f3nica de Motocicletas",
            "subcategorias": []
          },
          {
            "categoria": "Electr\u00f3nica Marina",
            "subcategorias": []
          },
          {
            "categoria": "GPS",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Electr\u00f3nicos de Oficina",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Apuntadores",
            "subcategorias": []
          },
          {
            "categoria": "B\u00e1sculas para Correo",
            "subcategorias": []
          },
          {
            "categoria": "Cartuchos de Tinta de Inyecci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Cartuchos de Tinta de Sublimaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Cartuchos de T\u00f3ner",
            "subcategorias": []
          },
          {
            "categoria": "Diccionarios Electr\u00f3nicos, Tesauros y Traductores",
            "subcategorias": []
          },
          {
            "categoria": "Enmicadoras",
            "subcategorias": []
          },
          {
            "categoria": "Esc\u00e1neres de C\u00f3digos de Barras",
            "subcategorias": []
          },
          {
            "categoria": "Esc\u00e1ners",
            "subcategorias": []
          },
          {
            "categoria": "Faxes",
            "subcategorias": []
          },
          {
            "categoria": "Fotocopiadoras",
            "subcategorias": []
          },
          {
            "categoria": "Grabadoras de Voz y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Impresoras",
            "subcategorias": []
          },
          {
            "categoria": "Kits y Recargas de Tinta para Inyecci\u00f3n de Tinta",
            "subcategorias": []
          },
          {
            "categoria": "Proyectores",
            "subcategorias": []
          },
          {
            "categoria": "Recargas y Kits de Tinta de Sublimaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Rotuladoras",
            "subcategorias": []
          },
          {
            "categoria": "Trituradoras de Papel y Documentos",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Equipos de Audio y Hi-Fi",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Bocinas",
            "subcategorias": []
          },
          {
            "categoria": "Dispositivos para Video En Tiempo Real",
            "subcategorias": []
          },
          {
            "categoria": "Minicomponentes",
            "subcategorias": []
          },
          {
            "categoria": "Radios y Grabadoras",
            "subcategorias": []
          },
          {
            "categoria": "Receptores y Componentes",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Lectores de Libros Electr\u00f3nicos y Accesorios",
        "subcategorias": [
          {
            "categoria": "Adaptadores de Corriente",
            "subcategorias": []
          },
          {
            "categoria": "Calcoman\u00edas Decorativas",
            "subcategorias": []
          },
          {
            "categoria": "Cubiertas",
            "subcategorias": []
          },
          {
            "categoria": "Fundas Blandas",
            "subcategorias": []
          },
          {
            "categoria": "Lectores de Libros Electr\u00f3nicos",
            "subcategorias": []
          },
          {
            "categoria": "Lotes",
            "subcategorias": []
          },
          {
            "categoria": "Protectores de Pantalla",
            "subcategorias": []
          },
          {
            "categoria": "Soportes",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Navegaci\u00f3n Satelital, GPS y Accesorios",
        "subcategorias": [
          {
            "categoria": "Dispositivos GPS deportivos",
            "subcategorias": []
          },
          {
            "categoria": "GPS Marinos",
            "subcategorias": []
          },
          {
            "categoria": "GPS RV",
            "subcategorias": []
          },
          {
            "categoria": "Localizadores GPS",
            "subcategorias": []
          },
          {
            "categoria": "Sistemas de Navegaci\u00f3n para Cami\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Sistemas de Navegaci\u00f3n para Coche",
            "subcategorias": []
          },
          {
            "categoria": "Sistemas de Navegaci\u00f3n para Motocicleta",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Radiocomunicaci\u00f3n",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Equipos Transmisores-receptores",
            "subcategorias": []
          },
          {
            "categoria": "Esc\u00e1neres de Radio",
            "subcategorias": []
          },
          {
            "categoria": "Radios Marinos",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Televisi\u00f3n y V\u00eddeo",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Bocinas",
            "subcategorias": []
          },
          {
            "categoria": "Combos TV-DVD",
            "subcategorias": []
          },
          {
            "categoria": "Decodificadores",
            "subcategorias": []
          },
          {
            "categoria": "Dispositivos para Streaming",
            "subcategorias": []
          },
          {
            "categoria": "Equipos de Home Theater",
            "subcategorias": []
          },
          {
            "categoria": "Equipos de TV Por Sat\u00e9lite",
            "subcategorias": []
          },
          {
            "categoria": "Equipos satelitales",
            "subcategorias": []
          },
          {
            "categoria": "Lentes de Video Virtual",
            "subcategorias": []
          },
          {
            "categoria": "Parab\u00f3licas",
            "subcategorias": []
          },
          {
            "categoria": "Proyectores",
            "subcategorias": []
          },
          {
            "categoria": "Receptores AV y Amplificadores",
            "subcategorias": []
          },
          {
            "categoria": "Reproductores y Grabadoras de Blu-ray",
            "subcategorias": []
          },
          {
            "categoria": "Reproductores y Grabadoras de DVD",
            "subcategorias": []
          },
          {
            "categoria": "Televisiones",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Tel\u00e9fonos, VoIP y Accesorios",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Contestadoras",
            "subcategorias": []
          },
          {
            "categoria": "Tel\u00e9fonos Anal\u00f3gicos y DECT",
            "subcategorias": []
          },
          {
            "categoria": "Tel\u00e9fonos Compatibles Con VoIP y Skype",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Accesorios de Alimentaci\u00f3n",
        "subcategorias": [
          {
            "categoria": "Adaptadores de CA",
            "subcategorias": []
          },
          {
            "categoria": "Adaptadores Internacionales",
            "subcategorias": []
          },
          {
            "categoria": "Cables de Extensi\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Protectores de Sobretensi\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Transformadores",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Aud\u00edfonos, auriculares y accesorios",
        "subcategorias": [
          {
            "categoria": "Adaptadores",
            "subcategorias": []
          },
          {
            "categoria": "Almohadillas",
            "subcategorias": []
          },
          {
            "categoria": "Amplificadores",
            "subcategorias": []
          },
          {
            "categoria": "Aud\u00edfonos",
            "subcategorias": []
          },
          {
            "categoria": "Estuches",
            "subcategorias": []
          },
          {
            "categoria": "Extensiones",
            "subcategorias": []
          },
          {
            "categoria": "Ganchos de Almacenamiento",
            "subcategorias": []
          },
          {
            "categoria": "Soportes",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Pilas y Cargadores",
        "subcategorias": [
          {
            "categoria": "Adaptadores de Pilas",
            "subcategorias": []
          },
          {
            "categoria": "Cargadores de Pilas",
            "subcategorias": []
          },
          {
            "categoria": "Paquetes de Pilas y Cargadores",
            "subcategorias": []
          },
          {
            "categoria": "Pilas Desechables",
            "subcategorias": []
          },
          {
            "categoria": "Pilas Recargables",
            "subcategorias": []
          },
          {
            "categoria": "Portapilas",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Tabletas",
        "subcategorias": [
          {
            "categoria": "Tablets",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Otros",
        "subcategorias": [
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      }
    ]
  },
  {
    "categoria": "Herramientas y Mejoras del Hogar",
    "subcategorias": [
      {
        "categoria": "Almacenamiento y Organizaci\u00f3n del Hogar",
        "subcategorias": [
          {
            "categoria": "Almacenamiento de Garaje",
            "subcategorias": []
          },
          {
            "categoria": "Almacenamiento para Exteriores",
            "subcategorias": []
          },
          {
            "categoria": "Armarios de Almacenamiento",
            "subcategorias": []
          },
          {
            "categoria": "Estantes Multiusos",
            "subcategorias": []
          },
          {
            "categoria": "Organizadores de Herramientas",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Chimeneas",
        "subcategorias": [
          {
            "categoria": "Chimeneas",
            "subcategorias": []
          },
          {
            "categoria": "Estufas",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Electricidad",
        "subcategorias": [
          {
            "categoria": "Accesorios para Conductos",
            "subcategorias": []
          },
          {
            "categoria": "Adaptadores Internacionales",
            "subcategorias": []
          },
          {
            "categoria": "Automatizaci\u00f3n del Hogar",
            "subcategorias": []
          },
          {
            "categoria": "Bridas",
            "subcategorias": []
          },
          {
            "categoria": "Cableado de Superficie",
            "subcategorias": []
          },
          {
            "categoria": "Cables el\u00e9ctricos",
            "subcategorias": []
          },
          {
            "categoria": "Capacitadores",
            "subcategorias": []
          },
          {
            "categoria": "Cojines T\u00e9rmicos Relajantes",
            "subcategorias": []
          },
          {
            "categoria": "Comparadores",
            "subcategorias": []
          },
          {
            "categoria": "Cristales",
            "subcategorias": []
          },
          {
            "categoria": "Diodos",
            "subcategorias": []
          },
          {
            "categoria": "Disyuntores",
            "subcategorias": []
          },
          {
            "categoria": "Enchufes y accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Extensiones",
            "subcategorias": []
          },
          {
            "categoria": "Fusibles",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas y Comprobadores",
            "subcategorias": []
          },
          {
            "categoria": "Interruptores y Reguladores de Luz",
            "subcategorias": []
          },
          {
            "categoria": "LED",
            "subcategorias": []
          },
          {
            "categoria": "Monitores",
            "subcategorias": []
          },
          {
            "categoria": "Monitores de Alimentaci\u00f3n El\u00e9ctrica",
            "subcategorias": []
          },
          {
            "categoria": "Montajes Empotrados",
            "subcategorias": []
          },
          {
            "categoria": "Optoacopladores",
            "subcategorias": []
          },
          {
            "categoria": "Osciladores",
            "subcategorias": []
          },
          {
            "categoria": "Paneles Disyuntores",
            "subcategorias": []
          },
          {
            "categoria": "Placa Adaptadora SMD",
            "subcategorias": []
          },
          {
            "categoria": "Placas de Pared",
            "subcategorias": []
          },
          {
            "categoria": "Radiotransmisores de Pared",
            "subcategorias": []
          },
          {
            "categoria": "Regletas El\u00e9ctricas",
            "subcategorias": []
          },
          {
            "categoria": "Resistores",
            "subcategorias": []
          },
          {
            "categoria": "Resonadores",
            "subcategorias": []
          },
          {
            "categoria": "Temporizadores",
            "subcategorias": []
          },
          {
            "categoria": "Terminales y Kits",
            "subcategorias": []
          },
          {
            "categoria": "Timbres y Campanas para Puerta",
            "subcategorias": []
          },
          {
            "categoria": "Transformadores",
            "subcategorias": []
          },
          {
            "categoria": "Transistores",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Equipamiento de Ba\u00f1os y Cocinas",
        "subcategorias": [
          {
            "categoria": "Equipamiento de Ba\u00f1os",
            "subcategorias": []
          },
          {
            "categoria": "Equipamiento de Lavaderos y Servicios",
            "subcategorias": []
          },
          {
            "categoria": "Equipamiento para Cocina",
            "subcategorias": []
          },
          {
            "categoria": "Filtros y Descalcificadores",
            "subcategorias": []
          },
          {
            "categoria": "Saunas",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Ferreter\u00eda",
        "subcategorias": [
          {
            "categoria": "Adhesivos y Selladores",
            "subcategorias": []
          },
          {
            "categoria": "Art\u00edculos para Ba\u00f1o",
            "subcategorias": []
          },
          {
            "categoria": "Buzones",
            "subcategorias": []
          },
          {
            "categoria": "Candados y Aldabas para Candados",
            "subcategorias": []
          },
          {
            "categoria": "Clavos, Tornillos y Sujetadores",
            "subcategorias": []
          },
          {
            "categoria": "Ferreter\u00eda para Armarios",
            "subcategorias": []
          },
          {
            "categoria": "Ferreter\u00eda para Muebles",
            "subcategorias": []
          },
          {
            "categoria": "Ferreter\u00eda para Puertas de Garaje",
            "subcategorias": []
          },
          {
            "categoria": "Ferreter\u00eda para Rejas",
            "subcategorias": []
          },
          {
            "categoria": "Ferreter\u00eda para Ventanas",
            "subcategorias": []
          },
          {
            "categoria": "Ferreter\u00eda y Cerraduras para Puertas",
            "subcategorias": []
          },
          {
            "categoria": "Ganchos",
            "subcategorias": []
          },
          {
            "categoria": "Linternas",
            "subcategorias": []
          },
          {
            "categoria": "Lonas y Amarres",
            "subcategorias": []
          },
          {
            "categoria": "N\u00fameros de Casa, Placas y Se\u00f1alamientos",
            "subcategorias": []
          },
          {
            "categoria": "Soportes para Estantes",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Herramientas Manuales y El\u00e9ctricas",
        "subcategorias": [
          {
            "categoria": "Accesorios para Herramientas El\u00e9ctricas",
            "subcategorias": []
          },
          {
            "categoria": "Aspiradoras en Seco y H\u00famedo",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas El\u00e9ctricas",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas Manuales",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas de Limpieza",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas para Medici\u00f3n y Dise\u00f1o",
            "subcategorias": []
          },
          {
            "categoria": "Organizadores de Herramientas",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Iluminaci\u00f3n",
        "subcategorias": [
          {
            "categoria": "Focos",
            "subcategorias": []
          },
          {
            "categoria": "Iluminaci\u00f3n de Exterior",
            "subcategorias": []
          },
          {
            "categoria": "Iluminaci\u00f3n de Interior",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Protecci\u00f3n y Seguridad",
        "subcategorias": [
          {
            "categoria": "Alarmas y Detectores para el Hogar",
            "subcategorias": []
          },
          {
            "categoria": "Cajas Fuertes y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Candados y Aldabas para Candados",
            "subcategorias": []
          },
          {
            "categoria": "Kits de Primeros Auxilios",
            "subcategorias": []
          },
          {
            "categoria": "Linternas",
            "subcategorias": []
          },
          {
            "categoria": "Material y Accesorios de Seguridad Laboral",
            "subcategorias": []
          },
          {
            "categoria": "Protecci\u00f3n Contra Incendios",
            "subcategorias": []
          },
          {
            "categoria": "Sirenas",
            "subcategorias": []
          },
          {
            "categoria": "Sistemas de Seguridad para el Hogar",
            "subcategorias": []
          },
          {
            "categoria": "Timbres de Alarmas",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Pinturas, Herramientas y Tratamiento de Paredes",
        "subcategorias": [
          {
            "categoria": "Adhesivos de Papel Tapiz",
            "subcategorias": []
          },
          {
            "categoria": "Adhesivos y Murales",
            "subcategorias": []
          },
          {
            "categoria": "Botes para Prueba de Color",
            "subcategorias": []
          },
          {
            "categoria": "Cenefas",
            "subcategorias": []
          },
          {
            "categoria": "Esp\u00e1tulas para Yeso",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas",
            "subcategorias": []
          },
          {
            "categoria": "Materiales de Preparaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Paneles de Color",
            "subcategorias": []
          },
          {
            "categoria": "Papel Tapiz",
            "subcategorias": []
          },
          {
            "categoria": "Pinturas, Tintes y Disolventes",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Suministros de Construcci\u00f3n",
        "subcategorias": [
          {
            "categoria": "Andamios",
            "subcategorias": []
          },
          {
            "categoria": "Climatizaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Escaleras de Mano",
            "subcategorias": []
          },
          {
            "categoria": "Iluminaci\u00f3n de \u00c1reas de Trabajo",
            "subcategorias": []
          },
          {
            "categoria": "Manipulaci\u00f3n de Materiales",
            "subcategorias": []
          },
          {
            "categoria": "Material de Construcci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Tuber\u00edas",
        "subcategorias": [
          {
            "categoria": "Bombas de Agua y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Calentadores de Agua y Piezas",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas para Cambiar Grifos",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas para Limpieza de Desag\u00fces",
            "subcategorias": []
          },
          {
            "categoria": "Piezas de Grifos",
            "subcategorias": []
          },
          {
            "categoria": "Piezas del Inodoro",
            "subcategorias": []
          },
          {
            "categoria": "Trituradores de Comida y Piezas",
            "subcategorias": []
          },
          {
            "categoria": "Tuber\u00edas, Equipo y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "V\u00e1lvulas",
            "subcategorias": []
          },
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "otros",
        "subcategorias": [
          {
            "categoria": "otros",
            "subcategorias": []
          }
        ]
      }
    ]
  },
  {
    "categoria": "Libros",
    "subcategorias": [
      {
        "categoria": "Arte y Fotograf\u00eda",
        "subcategorias": [
          {
            "categoria": "Arquit\u00e9ctura",
            "subcategorias": []
          },
          {
            "categoria": "Artes Esc\u00e9nicas",
            "subcategorias": []
          },
          {
            "categoria": "Danza",
            "subcategorias": []
          },
          {
            "categoria": "Dise\u00f1o Gr\u00e1fico",
            "subcategorias": []
          },
          {
            "categoria": "Fotograf\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "M\u00fasica",
            "subcategorias": []
          },
          {
            "categoria": "Teatro",
            "subcategorias": []
          },
          {
            "categoria": "Arte",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Hobbies y Hogar",
        "subcategorias": [
          {
            "categoria": "Antig\u00fcedades",
            "subcategorias": []
          },
          {
            "categoria": "Bodas",
            "subcategorias": []
          },
          {
            "categoria": "Cuidado de Animales y Mascotas",
            "subcategorias": []
          },
          {
            "categoria": "Dise\u00f1o de Interiores",
            "subcategorias": []
          },
          {
            "categoria": "Jardiner\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Manualidades",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Autoayuda",
        "subcategorias": [
          {
            "categoria": "Autoestima",
            "subcategorias": []
          },
          {
            "categoria": "Creatividad",
            "subcategorias": []
          },
          {
            "categoria": "Espiritual",
            "subcategorias": []
          },
          {
            "categoria": "Felicidad",
            "subcategorias": []
          },
          {
            "categoria": "Motivaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Manejo del Estr\u00e9s",
            "subcategorias": []
          },
          {
            "categoria": "Ni\u00f1o Interior",
            "subcategorias": []
          },
          {
            "categoria": "Transformaci\u00f3n Personal",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Ciencia Ficci\u00f3n y Fantas\u00eda",
        "subcategorias": [
          {
            "categoria": "Ciencia Ficci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Fantas\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Ciencia y Matem\u00e1ticas",
        "subcategorias": [
          {
            "categoria": "Astronom\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Ciencias Agr\u00edcolas",
            "subcategorias": []
          },
          {
            "categoria": "Biolog\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "F\u00edsica",
            "subcategorias": []
          },
          {
            "categoria": "Gen\u00e9tica",
            "subcategorias": []
          },
          {
            "categoria": "Matem\u00e1ticas",
            "subcategorias": []
          },
          {
            "categoria": "Ecolog\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Qu\u00edmica",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Comics y Novelas Gr\u00e1ficas",
        "subcategorias": [
          {
            "categoria": "Createspace",
            "subcategorias": []
          },
          {
            "categoria": "Dark Horse COmics",
            "subcategorias": []
          },
          {
            "categoria": "DC",
            "subcategorias": []
          },
          {
            "categoria": "Marvel Books",
            "subcategorias": []
          },
          {
            "categoria": "Seven Seas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Computadoras y Tecnolog\u00edas",
        "subcategorias": [
          {
            "categoria": "An\u00e1lisis y Dise\u00f1o de Sistemas",
            "subcategorias": []
          },
          {
            "categoria": "Bases de Datos",
            "subcategorias": []
          },
          {
            "categoria": "Dise\u00f1o de Sitios Web",
            "subcategorias": []
          },
          {
            "categoria": "Hardware",
            "subcategorias": []
          },
          {
            "categoria": "Programaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Redes Inform\u00e1ticas",
            "subcategorias": []
          },
          {
            "categoria": "Sistemas Operativos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Deportes y Tiempo Libre",
        "subcategorias": [
          {
            "categoria": "Baloncesto",
            "subcategorias": []
          },
          {
            "categoria": "B\u00e9isbol",
            "subcategorias": []
          },
          {
            "categoria": "Deportes Acu\u00e1ticos",
            "subcategorias": []
          },
          {
            "categoria": "Deportes de Invierno",
            "subcategorias": []
          },
          {
            "categoria": "Deportes Extremos",
            "subcategorias": []
          },
          {
            "categoria": "F\u00fatbol",
            "subcategorias": []
          },
          {
            "categoria": "F\u00fatbol Americano",
            "subcategorias": []
          },
          {
            "categoria": "Golf",
            "subcategorias": []
          },
          {
            "categoria": "Hockey",
            "subcategorias": []
          },
          {
            "categoria": "Juegos Olimpicos",
            "subcategorias": []
          },
          {
            "categoria": "Softbol",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Educaci\u00f3n y Referencia ",
        "subcategorias": [
          {
            "categoria": "Almanaques y Anuarios",
            "subcategorias": []
          },
          {
            "categoria": "Atlas y Mapas",
            "subcategorias": []
          },
          {
            "categoria": "Diccionarios",
            "subcategorias": []
          },
          {
            "categoria": "Enciclopedias",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Historia",
        "subcategorias": [
          {
            "categoria": "\u00c1frica",
            "subcategorias": []
          },
          {
            "categoria": "Asia",
            "subcategorias": []
          },
          {
            "categoria": "Australia y Oceania",
            "subcategorias": []
          },
          {
            "categoria": "Militar",
            "subcategorias": []
          },
          {
            "categoria": "Europa",
            "subcategorias": []
          },
          {
            "categoria": "Las Am\u00e9ricas",
            "subcategorias": []
          },
          {
            "categoria": "Mundial",
            "subcategorias": []
          },
          {
            "categoria": "Medio Oriente",
            "subcategorias": []
          },
          {
            "categoria": "Rusia",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Humor y Entretenimiento ",
        "subcategorias": [
          {
            "categoria": "Cine",
            "subcategorias": []
          },
          {
            "categoria": "Cultura Pop",
            "subcategorias": []
          },
          {
            "categoria": "Humor",
            "subcategorias": []
          },
          {
            "categoria": "Juegos",
            "subcategorias": []
          },
          {
            "categoria": "Televisi\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Libros de Recetas,Comida y Vino",
        "subcategorias": [
          {
            "categoria": "Alimentos Naturales",
            "subcategorias": []
          },
          {
            "categoria": "Artes Culinar\u00edas",
            "subcategorias": []
          },
          {
            "categoria": "Dietas Especiales",
            "subcategorias": []
          },
          {
            "categoria": "Gastronom\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Refrescos y Bebidas",
            "subcategorias": []
          },
          {
            "categoria": "Regional e Internacional ",
            "subcategorias": []
          },
          {
            "categoria": "Vegetariana",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Misterio",
        "subcategorias": [
          {
            "categoria": "Misterio",
            "subcategorias": []
          },
          {
            "categoria": "Thrillers",
            "subcategorias": []
          },
          {
            "categoria": "Policiaco",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Negocios",
        "subcategorias": [
          {
            "categoria": "Desarrollo Empresiarial ",
            "subcategorias": []
          },
          {
            "categoria": "Econom\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Finanzas",
            "subcategorias": []
          },
          {
            "categoria": "Gesti\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Gobierno",
            "subcategorias": []
          },
          {
            "categoria": "Inversi\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Pol\u00edtica y Ciencias Sociales",
        "subcategorias": [
          {
            "categoria": "Ciencias Sociales",
            "subcategorias": []
          },
          {
            "categoria": "Crimen",
            "subcategorias": []
          },
          {
            "categoria": "Filosof\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Pol\u00edtica",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Romance",
        "subcategorias": [
          {
            "categoria": "Suspenso",
            "subcategorias": []
          },
          {
            "categoria": "Contemporaneo ",
            "subcategorias": []
          },
          {
            "categoria": "Paranormal",
            "subcategorias": []
          },
          {
            "categoria": "Historico",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Salud",
        "subcategorias": [
          {
            "categoria": "Medicina Alternativa",
            "subcategorias": []
          },
          {
            "categoria": "Relaciones",
            "subcategorias": []
          },
          {
            "categoria": "Salud Mental",
            "subcategorias": []
          },
          {
            "categoria": "Salud Personal",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Libros en Idiomas Extranjeros",
        "subcategorias": [
          {
            "categoria": "Acci\u00f3n y Aventura",
            "subcategorias": []
          },
          {
            "categoria": "Arte, Cine y Fotograf\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Autoayuda",
            "subcategorias": []
          },
          {
            "categoria": "Ciencia y Tecnolog\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Suspenso y Misterio",
            "subcategorias": []
          },
          {
            "categoria": "Deportes",
            "subcategorias": []
          },
          {
            "categoria": "Derecho",
            "subcategorias": []
          },
          {
            "categoria": "Fantas\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Historia",
            "subcategorias": []
          },
          {
            "categoria": "Turismo",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Otros",
        "subcategorias": [
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      }
    ]
  },
  {
    "categoria": "Hogar y Cocina",
    "subcategorias": [
      {
        "categoria": "Almacenamiento",
        "subcategorias": [
          {
            "categoria": "Adornos",
            "subcategorias": []
          },
          {
            "categoria": "Regalos",
            "subcategorias": []
          },
          {
            "categoria": "Oficina",
            "subcategorias": []
          },
          {
            "categoria": "Ropa",
            "subcategorias": []
          },
          {
            "categoria": "Basura",
            "subcategorias": []
          },
          {
            "categoria": "Cestos",
            "subcategorias": []
          },
          {
            "categoria": "Ganchos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Herramientas de Limpieza",
        "subcategorias": [
          {
            "categoria": "Carritos de Limpieza",
            "subcategorias": []
          },
          {
            "categoria": "Guantes",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Ba\u00f1o",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Tapetes",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Blancos",
        "subcategorias": [
          {
            "categoria": "Accesorios para Cama",
            "subcategorias": []
          },
          {
            "categoria": "Blancos de Cocina",
            "subcategorias": []
          },
          {
            "categoria": "Cojines",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Calefacci\u00f3n",
        "subcategorias": [
          {
            "categoria": "Deshumidificadores",
            "subcategorias": []
          },
          {
            "categoria": "Purificadores de Aire",
            "subcategorias": []
          },
          {
            "categoria": "Ventiladores",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Cocina",
        "subcategorias": [
          {
            "categoria": "Almacenamiento de Despensa",
            "subcategorias": []
          },
          {
            "categoria": "Caf\u00e9 y T\u00e9",
            "subcategorias": []
          },
          {
            "categoria": "Vajilla",
            "subcategorias": []
          },
          {
            "categoria": "Electrodom\u00e9sticos",
            "subcategorias": []
          },
          {
            "categoria": "Reposter\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Utensilios",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Decoraci\u00f3n",
        "subcategorias": [
          {
            "categoria": "Cortinas y persianas",
            "subcategorias": []
          },
          {
            "categoria": "Espejos",
            "subcategorias": []
          },
          {
            "categoria": "Fundas",
            "subcategorias": []
          },
          {
            "categoria": "Jarrones",
            "subcategorias": []
          },
          {
            "categoria": "Marcos",
            "subcategorias": []
          },
          {
            "categoria": "Imanes",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Iluminaci\u00f3n",
        "subcategorias": [
          {
            "categoria": "Exterior",
            "subcategorias": []
          },
          {
            "categoria": "Interior",
            "subcategorias": []
          },
          {
            "categoria": "Navidad",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Muebles",
        "subcategorias": [
          {
            "categoria": "Comedor",
            "subcategorias": []
          },
          {
            "categoria": "Rec\u00e1mara",
            "subcategorias": []
          },
          {
            "categoria": "Oficina",
            "subcategorias": []
          },
          {
            "categoria": "Infantil",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Otros",
        "subcategorias": [
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      }
    ]
  },
  {
    "categoria": "Instrumentos Musicales",
    "subcategorias": [
      {
        "categoria": "Accesorios para Producci\u00f3n Musical",
        "subcategorias": [
          {
            "categoria": "Afinadores",
            "subcategorias": []
          },
          {
            "categoria": "Aprendizaje Musical",
            "subcategorias": []
          },
          {
            "categoria": "Atriles",
            "subcategorias": []
          },
          {
            "categoria": "Atriles de Lira",
            "subcategorias": []
          },
          {
            "categoria": "Batutas de Director",
            "subcategorias": []
          },
          {
            "categoria": "Cables y Conectores",
            "subcategorias": []
          },
          {
            "categoria": "Cuadernos de Papel para Personal",
            "subcategorias": []
          },
          {
            "categoria": "L\u00e1mparas para Atril",
            "subcategorias": []
          },
          {
            "categoria": "Metr\u00f3nomos",
            "subcategorias": []
          },
          {
            "categoria": "Papel Pautado",
            "subcategorias": []
          },
          {
            "categoria": "Regalos de M\u00fasica",
            "subcategorias": []
          },
          {
            "categoria": "Tableros de Anuncios",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Bajos y Accesorios",
        "subcategorias": [
          {
            "categoria": "Amplificadores",
            "subcategorias": []
          },
          {
            "categoria": "Bajos El\u00e9ctricos",
            "subcategorias": []
          },
          {
            "categoria": "Bajos y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Efectos",
            "subcategorias": []
          },
          {
            "categoria": "Piezas y Repuestos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Bater\u00edas y Percusi\u00f3n",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Bater\u00edas, Roto Toms y Sets de Tambores",
            "subcategorias": []
          },
          {
            "categoria": "Gongs",
            "subcategorias": []
          },
          {
            "categoria": "Herrajes",
            "subcategorias": []
          },
          {
            "categoria": "Pads de Pr\u00e1ctica",
            "subcategorias": []
          },
          {
            "categoria": "Percusi\u00f3n de Mano",
            "subcategorias": []
          },
          {
            "categoria": "Percusi\u00f3n Mel\u00f3dica y de Orquesta",
            "subcategorias": []
          },
          {
            "categoria": "Platillos",
            "subcategorias": []
          },
          {
            "categoria": "Tambores de Mano",
            "subcategorias": []
          },
          {
            "categoria": "Tambores Electr\u00f3nicos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Equipos de DJ y VJ",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Auriculares para DJ",
            "subcategorias": []
          },
          {
            "categoria": "Controladores para DJ",
            "subcategorias": []
          },
          {
            "categoria": "Iluminaci\u00f3n y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Mesas Mezcladoras",
            "subcategorias": []
          },
          {
            "categoria": "Micr\u00f3fonos",
            "subcategorias": []
          },
          {
            "categoria": "Reproductores de CD",
            "subcategorias": []
          },
          {
            "categoria": "Sets para DJ",
            "subcategorias": []
          },
          {
            "categoria": "Tornamesas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Equipos de Karaoke",
        "subcategorias": [
          {
            "categoria": "Sistemas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Grabaci\u00f3n y Computadoras",
        "subcategorias": [
          {
            "categoria": "Accesorios de Estudio",
            "subcategorias": []
          },
          {
            "categoria": "Auriculares y Monitores Internos",
            "subcategorias": []
          },
          {
            "categoria": "Cables y Conectores",
            "subcategorias": []
          },
          {
            "categoria": "Controladores MIDI",
            "subcategorias": []
          },
          {
            "categoria": "Controladores para Estaciones de Trabajo de Audio Digital",
            "subcategorias": []
          },
          {
            "categoria": "Convertidores Digitales",
            "subcategorias": []
          },
          {
            "categoria": "Grabadores Multipista",
            "subcategorias": []
          },
          {
            "categoria": "Interfaces de Audio",
            "subcategorias": []
          },
          {
            "categoria": "Interfaces MIDI",
            "subcategorias": []
          },
          {
            "categoria": "Mesas Mezcladoras",
            "subcategorias": []
          },
          {
            "categoria": "Micr\u00f3fonos",
            "subcategorias": []
          },
          {
            "categoria": "Monitores de Estudio",
            "subcategorias": []
          },
          {
            "categoria": "Preamplificadores",
            "subcategorias": []
          },
          {
            "categoria": "Procesadores de Se\u00f1ales y de Efectos",
            "subcategorias": []
          },
          {
            "categoria": "Software de Grabaci\u00f3n y Reproducci\u00f3n de Audio",
            "subcategorias": []
          },
          {
            "categoria": "Software de Notaci\u00f3n Musical",
            "subcategorias": []
          },
          {
            "categoria": "Tratamientos para Salas Ac\u00fasticas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Guitarras y Accesorios",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Amplificadores para Guitarras",
            "subcategorias": []
          },
          {
            "categoria": "Efectos",
            "subcategorias": []
          },
          {
            "categoria": "Guitarras Ac\u00fasticas de Cuerdas Met\u00e1licas",
            "subcategorias": []
          },
          {
            "categoria": "Guitarras Cl\u00e1sicas",
            "subcategorias": []
          },
          {
            "categoria": "Guitarras Electroac\u00fasticas",
            "subcategorias": []
          },
          {
            "categoria": "Guitarras El\u00e9ctricas",
            "subcategorias": []
          },
          {
            "categoria": "Kits de Guitarras El\u00e9ctricas",
            "subcategorias": []
          },
          {
            "categoria": "Piezas y Repuestos para Guitarras Ac\u00fasticas y Cl\u00e1sicas",
            "subcategorias": []
          },
          {
            "categoria": "Piezas y Repuestos para Guitarras El\u00e9ctricas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Instrumentos de Cuerda",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Piezas y Repuestos",
            "subcategorias": []
          },
          {
            "categoria": "Violas",
            "subcategorias": []
          },
          {
            "categoria": "Violines",
            "subcategorias": []
          },
          {
            "categoria": "Guitarras Cl\u00e1sicas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Instrumentos de Viento",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Arm\u00f3nicas",
            "subcategorias": []
          },
          {
            "categoria": "Arpas de Boca",
            "subcategorias": []
          },
          {
            "categoria": "Didgeridoos",
            "subcategorias": []
          },
          {
            "categoria": "Instrumentos de Viento Madera",
            "subcategorias": []
          },
          {
            "categoria": "Mel\u00f3dicas",
            "subcategorias": []
          },
          {
            "categoria": "Neys",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Micr\u00f3fonos",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Condensadores",
            "subcategorias": []
          },
          {
            "categoria": "Din\u00e1micos",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Pianos y Teclados",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Folclore y Acordeones",
            "subcategorias": []
          },
          {
            "categoria": "Pianos",
            "subcategorias": []
          },
          {
            "categoria": "Sintetizadores",
            "subcategorias": []
          },
          {
            "categoria": "Teclados Electr\u00f3nicos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Sintetizadores, Sampleadores y M\u00e1s",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Sampleadores",
            "subcategorias": []
          },
          {
            "categoria": "Sintetizadores",
            "subcategorias": []
          },
          {
            "categoria": "Teclados Electr\u00f3nicos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Sistemas de Escenario y Megafon\u00eda",
        "subcategorias": [
          {
            "categoria": "Altavoces",
            "subcategorias": []
          },
          {
            "categoria": "Amplificadores",
            "subcategorias": []
          },
          {
            "categoria": "Cables y Conectores",
            "subcategorias": []
          },
          {
            "categoria": "Cajas DI",
            "subcategorias": []
          },
          {
            "categoria": "Fundas, Estuches y Soportes",
            "subcategorias": []
          },
          {
            "categoria": "Iluminaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Micr\u00f3fonos",
            "subcategorias": []
          },
          {
            "categoria": "Monitores Intra-aurales",
            "subcategorias": []
          },
          {
            "categoria": "M\u00e1quinas de Efectos",
            "subcategorias": []
          },
          {
            "categoria": "Procesadores de Se\u00f1ales y de Efectos",
            "subcategorias": []
          },
          {
            "categoria": "Sistemas de Megafon\u00eda y Anuncio",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Otros",
        "subcategorias": [
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      }
    ]
  },
  {
    "categoria": "Jard\u00edn",
    "subcategorias": [
      {
        "categoria": "Almacenamiento y Cubiertas para Exterior",
        "subcategorias": [
          {
            "categoria": "Bancas de Almacenamiento",
            "subcategorias": []
          },
          {
            "categoria": "Cajas para Deck",
            "subcategorias": []
          },
          {
            "categoria": "Casas de Verano",
            "subcategorias": []
          },
          {
            "categoria": "Cobertizos de Almacenamiento",
            "subcategorias": []
          },
          {
            "categoria": "Cobertizos de Almacenamiento de Basura",
            "subcategorias": []
          },
          {
            "categoria": "Contenedores de Almacenamiento",
            "subcategorias": []
          },
          {
            "categoria": "Garajes",
            "subcategorias": []
          },
          {
            "categoria": "Kits de Casas Miniatura",
            "subcategorias": []
          },
          {
            "categoria": "Saunas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Asadores y Comedor en Exteriores",
        "subcategorias": [
          {
            "categoria": "Accesorios para Asadores y Ahumadores",
            "subcategorias": []
          },
          {
            "categoria": "Asadores y Hornos para Ahumar Carne",
            "subcategorias": []
          },
          {
            "categoria": "Cocinas al Aire Libre",
            "subcategorias": []
          },
          {
            "categoria": "Piezas de repuesto",
            "subcategorias": []
          },
          {
            "categoria": "Utensilios de Cocina para Asador",
            "subcategorias": []
          },
          {
            "categoria": "Utensilios para Asador",
            "subcategorias": []
          },
          {
            "categoria": "Vajilla y Utensilios para Picnic",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Calefacci\u00f3n y Refrigeraci\u00f3n para Exterior",
        "subcategorias": [
          {
            "categoria": "Accesorios para Chimeneas al Aire Libre",
            "subcategorias": []
          },
          {
            "categoria": "Calentadores para Exterior, Piezas y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Fogatas y Chimeneas al Aire Libre",
            "subcategorias": []
          },
          {
            "categoria": "Piezas y Accesorios para Nebulizadores",
            "subcategorias": []
          },
          {
            "categoria": "Sistemas de Nebulizaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Ventiladores con nebulizaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Cortadoras y Herramientas El\u00e9ctricas",
        "subcategorias": [
          {
            "categoria": "Detectores de Metal y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Fresadoras",
            "subcategorias": []
          },
          {
            "categoria": "Generadores y Energ\u00eda Port\u00e1til",
            "subcategorias": []
          },
          {
            "categoria": "Hachas para Hierba",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas El\u00e9ctricas de Exterior",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas y Accesorios de Mantenimiento para \u00c1rboles",
            "subcategorias": []
          },
          {
            "categoria": "Lavadoras a Presi\u00f3n y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Piezas y Accesorios para Podadoras",
            "subcategorias": []
          },
          {
            "categoria": "Podadoras y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Repuestos para Herramientas El\u00e9ctricas de Exterior",
            "subcategorias": []
          },
          {
            "categoria": "Sopladores de Hojas, Aspiradoras y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Tijeras de Podar, Piezas y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Cuidado de C\u00e9sped y Plantas",
        "subcategorias": [
          {
            "categoria": "Control de Insectos y Plagas",
            "subcategorias": []
          },
          {
            "categoria": "Control de Malezas, Musgos y Hongos",
            "subcategorias": []
          },
          {
            "categoria": "Fertilizantes y Alimentos para Plantas",
            "subcategorias": []
          },
          {
            "categoria": "Monitorizaci\u00f3n de plantas y suelos",
            "subcategorias": []
          },
          {
            "categoria": "Tierras, Abonos y Medios de Plantaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Decoraci\u00f3n para Exteriores",
        "subcategorias": [
          {
            "categoria": "Accesorios para Fuentes",
            "subcategorias": []
          },
          {
            "categoria": "Alfombras de Exteriores",
            "subcategorias": []
          },
          {
            "categoria": "Banderas",
            "subcategorias": []
          },
          {
            "categoria": "Cadenas de Lluvia",
            "subcategorias": []
          },
          {
            "categoria": "Campanas",
            "subcategorias": []
          },
          {
            "categoria": "Cercas Decorativas",
            "subcategorias": []
          },
          {
            "categoria": "Conos de Viento",
            "subcategorias": []
          },
          {
            "categoria": "Cortinas para Exteriores",
            "subcategorias": []
          },
          {
            "categoria": "Decoraciones de Festividades para Exterior",
            "subcategorias": []
          },
          {
            "categoria": "Esculturas y Estatuas de Jard\u00edn",
            "subcategorias": []
          },
          {
            "categoria": "Estacas Decorativas Para Jard\u00edn",
            "subcategorias": []
          },
          {
            "categoria": "Estacas Decorativas para Jard\u00edn",
            "subcategorias": []
          },
          {
            "categoria": "Fuentes",
            "subcategorias": []
          },
          {
            "categoria": "Ganchos de Pastor para Exteriores",
            "subcategorias": []
          },
          {
            "categoria": "Herraje para M\u00e1stil",
            "subcategorias": []
          },
          {
            "categoria": "Letreros de Direcci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Materiales para su Jard\u00edn y Patio",
            "subcategorias": []
          },
          {
            "categoria": "Pasto Artificial",
            "subcategorias": []
          },
          {
            "categoria": "Relojes de Sol",
            "subcategorias": []
          },
          {
            "categoria": "Relojes para Exteriores",
            "subcategorias": []
          },
          {
            "categoria": "Se\u00f1alamientos para Patio",
            "subcategorias": []
          },
          {
            "categoria": "Soportes para Colgar de Exteriores",
            "subcategorias": []
          },
          {
            "categoria": "Veletas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Estanques y Jardines Acu\u00e1ticos",
        "subcategorias": [
          {
            "categoria": "Bombas",
            "subcategorias": []
          },
          {
            "categoria": "Boquillas de Bomba",
            "subcategorias": []
          },
          {
            "categoria": "Fuentes para Estanques",
            "subcategorias": []
          },
          {
            "categoria": "Luces para Estanques",
            "subcategorias": []
          },
          {
            "categoria": "Tubos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Estructuras y Equipo de Germinaci\u00f3n",
        "subcategorias": [
          {
            "categoria": "Acuapon\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Canteros Elevados y Estructuras de Apoyo",
            "subcategorias": []
          },
          {
            "categoria": "Cenadores",
            "subcategorias": []
          },
          {
            "categoria": "Hidropon\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Invernaderos y Equipo de Germinaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Toldos, Gazebos y P\u00e9rgolas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Herramientas de Jard\u00edn y Equipo de Riego",
        "subcategorias": [
          {
            "categoria": "Accesorios de Jardiner\u00eda y Ropa de Protecci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Carros y Vagones",
            "subcategorias": []
          },
          {
            "categoria": "Composta y Residuos de Patio",
            "subcategorias": []
          },
          {
            "categoria": "Contenedores para Plantas y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Equipo de Riego",
            "subcategorias": []
          },
          {
            "categoria": "Esparcidores",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas Manuales",
            "subcategorias": []
          },
          {
            "categoria": "Pulverizadores y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Iluminaci\u00f3n de Exterior",
        "subcategorias": [
          {
            "categoria": "Accesorios de Iluminaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Apliques de Exterior",
            "subcategorias": []
          },
          {
            "categoria": "Farolas",
            "subcategorias": []
          },
          {
            "categoria": "Focos de Exterior",
            "subcategorias": []
          },
          {
            "categoria": "Guirnaldas Luminosas de Exterior",
            "subcategorias": []
          },
          {
            "categoria": "Iluminaci\u00f3n de Caminos",
            "subcategorias": []
          },
          {
            "categoria": "Iluminaci\u00f3n de Estanques y Albercas",
            "subcategorias": []
          },
          {
            "categoria": "Iluminaci\u00f3n de Patio y Terraza",
            "subcategorias": []
          },
          {
            "categoria": "Iluminaci\u00f3n de Seguridad",
            "subcategorias": []
          },
          {
            "categoria": "L\u00e1mparas de Piso para Exteriores",
            "subcategorias": []
          },
          {
            "categoria": "Linternas de Exterior",
            "subcategorias": []
          },
          {
            "categoria": "Luces para Sombrillas",
            "subcategorias": []
          },
          {
            "categoria": "Mangueras LED de Exterior",
            "subcategorias": []
          },
          {
            "categoria": "Postes de Luz",
            "subcategorias": []
          },
          {
            "categoria": "Proyectores de Iluminaci\u00f3n Decorativa",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Muebles de Patio y Accesorios",
        "subcategorias": [
          {
            "categoria": "Almohadas Decorativas",
            "subcategorias": []
          },
          {
            "categoria": "Asientos para Patio",
            "subcategorias": []
          },
          {
            "categoria": "Bancas con Cajones",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas de Almacenamiento de Coj\u00edn",
            "subcategorias": []
          },
          {
            "categoria": "Cajas para Deck",
            "subcategorias": []
          },
          {
            "categoria": "Carros",
            "subcategorias": []
          },
          {
            "categoria": "Cojines",
            "subcategorias": []
          },
          {
            "categoria": "Contenedores de Almacenamiento",
            "subcategorias": []
          },
          {
            "categoria": "Fundas",
            "subcategorias": []
          },
          {
            "categoria": "Fundas de Coj\u00edn",
            "subcategorias": []
          },
          {
            "categoria": "Hamacas, Columpios y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Muebles",
            "subcategorias": []
          },
          {
            "categoria": "Manteles",
            "subcategorias": []
          },
          {
            "categoria": "Mesas",
            "subcategorias": []
          },
          {
            "categoria": "Sombrillas y Sombras",
            "subcategorias": []
          },
          {
            "categoria": "Toldos, Gazebos y P\u00e9rgolas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Observaci\u00f3n de Aves y Fauna de Patio",
        "subcategorias": [
          {
            "categoria": "Ardillas",
            "subcategorias": []
          },
          {
            "categoria": "Aves",
            "subcategorias": []
          },
          {
            "categoria": "Hoteles de Insectos",
            "subcategorias": []
          },
          {
            "categoria": "Mariposas",
            "subcategorias": []
          },
          {
            "categoria": "Murci\u00e9lagos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Piscinas, Jacuzzis y Suministros",
        "subcategorias": [
          {
            "categoria": "Calentadores y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Duchas para Exteriores",
            "subcategorias": []
          },
          {
            "categoria": "Filtros, Bombas y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Fundas y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas de Limpieza y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Jacuzzis",
            "subcategorias": []
          },
          {
            "categoria": "Pintura y Sellado",
            "subcategorias": []
          },
          {
            "categoria": "Piscinas",
            "subcategorias": []
          },
          {
            "categoria": "Productos de Iluminaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Pruebas de Qu\u00edmicos y Agua",
            "subcategorias": []
          },
          {
            "categoria": "Revestimientos",
            "subcategorias": []
          },
          {
            "categoria": "Saunas al Aire Libre y Piezas",
            "subcategorias": []
          },
          {
            "categoria": "Seguridad",
            "subcategorias": []
          },
          {
            "categoria": "Term\u00f3metros",
            "subcategorias": []
          },
          {
            "categoria": "Toboganes, Escaleras y Trampolines",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Term\u00f3metros e Instrumentos Meteorol\u00f3gicos",
        "subcategorias": [
          {
            "categoria": "Anem\u00f3metros",
            "subcategorias": []
          },
          {
            "categoria": "Bar\u00f3metros",
            "subcategorias": []
          },
          {
            "categoria": "Estaciones Meteorol\u00f3gicas",
            "subcategorias": []
          },
          {
            "categoria": "Higr\u00f3metros",
            "subcategorias": []
          },
          {
            "categoria": "Medidores de Lluvia",
            "subcategorias": []
          },
          {
            "categoria": "Term\u00f3metros",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Terrazas de Madera y Cercas",
        "subcategorias": [
          {
            "categoria": "Barandales y Postes",
            "subcategorias": []
          },
          {
            "categoria": "Ferreter\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Materiales",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Otros",
        "subcategorias": [
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      }
    ]
  },
  {
    "categoria": "Juguetes y Juegos",
    "subcategorias": [
      {
        "categoria": "Aire Libre y Deportes",
        "subcategorias": [
          {
            "categoria": "Albercas de Bolas y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Albercas de Jard\u00edn y Juegos Acu\u00e1ticos",
            "subcategorias": []
          },
          {
            "categoria": "Armas y Proyectiles de Juguete",
            "subcategorias": []
          },
          {
            "categoria": "Bastones y Pelotas para Saltar",
            "subcategorias": []
          },
          {
            "categoria": "Bicicletas, Triciclos y Carritos",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas de Dormir",
            "subcategorias": []
          },
          {
            "categoria": "B\u00fameran",
            "subcategorias": []
          },
          {
            "categoria": "Cajones de Arena y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Casas de Juguete",
            "subcategorias": []
          },
          {
            "categoria": "Dardos y Dianas",
            "subcategorias": []
          },
          {
            "categoria": "Gimnasios y Columpios",
            "subcategorias": []
          },
          {
            "categoria": "Habilidad y Gimnasia",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas de Jard\u00edn para Ni\u00f1os",
            "subcategorias": []
          },
          {
            "categoria": "Juguetes Deportivos",
            "subcategorias": []
          },
          {
            "categoria": "Papalotes y Juguetes de Vuelo",
            "subcategorias": []
          },
          {
            "categoria": "Rehiletes de Jard\u00edn",
            "subcategorias": []
          },
          {
            "categoria": "Tiendas de Campa\u00f1a para Ni\u00f1os",
            "subcategorias": []
          },
          {
            "categoria": "Burbujas",
            "subcategorias": []
          },
          {
            "categoria": "Equipo para parque infantil y juegos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Artes y Manualidades",
        "subcategorias": [
          {
            "categoria": "\u00c1lbumes y Calcoman\u00edas",
            "subcategorias": []
          },
          {
            "categoria": "Arcilla y Plastilina",
            "subcategorias": []
          },
          {
            "categoria": "Construcci\u00f3n de Maquetas y Pasatiempos",
            "subcategorias": []
          },
          {
            "categoria": "Cuentas para Planchar",
            "subcategorias": []
          },
          {
            "categoria": "Delantales y Batas",
            "subcategorias": []
          },
          {
            "categoria": "Grabados y Sellos",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Manualidades",
            "subcategorias": []
          },
          {
            "categoria": "Libros para Colorear",
            "subcategorias": []
          },
          {
            "categoria": "Material de Escritura y Dibujo",
            "subcategorias": []
          },
          {
            "categoria": "Mosaicos",
            "subcategorias": []
          },
          {
            "categoria": "Pizarrones",
            "subcategorias": []
          },
          {
            "categoria": "Pizarrones M\u00e1gicos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Art\u00edculos para Fiesta",
        "subcategorias": [
          {
            "categoria": "Cubiertos y platos para fiestas",
            "subcategorias": []
          },
          {
            "categoria": "Decoraciones",
            "subcategorias": []
          },
          {
            "categoria": "Invitaciones",
            "subcategorias": []
          },
          {
            "categoria": "Manteles y Accesorios para Mesas",
            "subcategorias": []
          },
          {
            "categoria": "Espantasuegras",
            "subcategorias": []
          },
          {
            "categoria": "Pi\u00f1atas",
            "subcategorias": []
          },
          {
            "categoria": "Recordatorios para cumplea\u00f1os",
            "subcategorias": []
          },
          {
            "categoria": "Gorros, Gafas y Accesorios para Fiestas",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Lanzamiento",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Pin",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Instrumentos Musicales de Juguete",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Bater\u00edas y Percusiones",
            "subcategorias": []
          },
          {
            "categoria": "Guitarras y Cuerdas",
            "subcategorias": []
          },
          {
            "categoria": "Pianos y Teclados",
            "subcategorias": []
          },
          {
            "categoria": "Viento y Metal",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Juegos de Construcci\u00f3n",
        "subcategorias": [
          {
            "categoria": "Almacenamiento y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Construcci\u00f3n Magn\u00e9tica",
            "subcategorias": []
          },
          {
            "categoria": "Figuras",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Construcci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Engranes",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Juegos de Imitaci\u00f3n",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas de Juguete",
            "subcategorias": []
          },
          {
            "categoria": "Dinero y banca",
            "subcategorias": []
          },
          {
            "categoria": "Disfraces",
            "subcategorias": []
          },
          {
            "categoria": "Equipo de Espionaje para Ni\u00f1os",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas de Juguete",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de M\u00e9dicos",
            "subcategorias": []
          },
          {
            "categoria": "Juguetes de Cocina",
            "subcategorias": []
          },
          {
            "categoria": "Juguetes del Hogar",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Juegos y Accesorios para Juegos",
        "subcategorias": [
          {
            "categoria": "Ajedrez",
            "subcategorias": []
          },
          {
            "categoria": "Arcade y Juegos de Mesa",
            "subcategorias": []
          },
          {
            "categoria": "Bingo",
            "subcategorias": []
          },
          {
            "categoria": "Canicas",
            "subcategorias": []
          },
          {
            "categoria": "Equipo de Casino",
            "subcategorias": []
          },
          {
            "categoria": "Juegos Electr\u00f3nicos Port\u00e1tiles",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Apilar",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Cartas",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Mesa",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Piso",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Tablero y Miniatura",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Viaje y de Bolsillo",
            "subcategorias": []
          },
          {
            "categoria": "Juegos para DVD",
            "subcategorias": []
          },
          {
            "categoria": "Trompos de Batalla",
            "subcategorias": []
          },
          {
            "categoria": "Accesorios para Juegos",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de mesa",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Juguetes Coleccionables",
        "subcategorias": [
          {
            "categoria": "Almacenamiento de Coleccionables",
            "subcategorias": []
          },
          {
            "categoria": "Cromos, Cartas Coleccionables y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Estatuas y Bustos",
            "subcategorias": []
          },
          {
            "categoria": "Monedas Coleccionables y Papel Moneda",
            "subcategorias": []
          },
          {
            "categoria": "Sellos Postales Coleccionables",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Juguetes Educativos",
        "subcategorias": [
          {
            "categoria": "Ciencias",
            "subcategorias": []
          },
          {
            "categoria": "Electr\u00f3nica",
            "subcategorias": []
          },
          {
            "categoria": "Energ\u00eda Solar",
            "subcategorias": []
          },
          {
            "categoria": "H\u00e1bitats",
            "subcategorias": []
          },
          {
            "categoria": "Imanes y Juegos Magn\u00e9ticos",
            "subcategorias": []
          },
          {
            "categoria": "Juguetes de Desarrollo Temprano y de Actividad",
            "subcategorias": []
          },
          {
            "categoria": "Juguetes para Necesidades Especiales",
            "subcategorias": []
          },
          {
            "categoria": "Lectura y Escritura",
            "subcategorias": []
          },
          {
            "categoria": "\u00d3ptica",
            "subcategorias": []
          },
          {
            "categoria": "Pistas para Canicas",
            "subcategorias": []
          },
          {
            "categoria": "Tarjetas Did\u00e1cticas",
            "subcategorias": []
          },
          {
            "categoria": "Visores",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Juguetes Electr\u00f3nicos",
        "subcategorias": [
          {
            "categoria": "Boomboxes y Reproductores de MP3",
            "subcategorias": []
          },
          {
            "categoria": "C\u00e1maras Digitales",
            "subcategorias": []
          },
          {
            "categoria": "Juguetes de Cuentacuentos",
            "subcategorias": []
          },
          {
            "categoria": "Mascotas Electr\u00f3nicas",
            "subcategorias": []
          },
          {
            "categoria": "Tabletas y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Videojuegos",
            "subcategorias": []
          },
          {
            "categoria": "Walkie Talkies",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Juguetes Novedosos y de Broma",
        "subcategorias": [
          {
            "categoria": "Art\u00edculos de Broma",
            "subcategorias": []
          },
          {
            "categoria": "Juguetes antiestr\u00e9s",
            "subcategorias": []
          },
          {
            "categoria": "Juguetes de adivinaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Juguetes de Broma de Chorro de Agua",
            "subcategorias": []
          },
          {
            "categoria": "Juguetes de Cuerda",
            "subcategorias": []
          },
          {
            "categoria": "Kits de Magia y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Masas Viscosas para Jugar",
            "subcategorias": []
          },
          {
            "categoria": "Miniaturas",
            "subcategorias": []
          },
          {
            "categoria": "Monedas Novedosas y Papel Moneda",
            "subcategorias": []
          },
          {
            "categoria": "Mu\u00f1ecas Matrioska",
            "subcategorias": []
          },
          {
            "categoria": "Prismas",
            "subcategorias": []
          },
          {
            "categoria": "Trompos de juguete",
            "subcategorias": []
          },
          {
            "categoria": "Yoyos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Juguetes para Beb\u00e9s y Ni\u00f1os Peque\u00f1os",
        "subcategorias": [
          {
            "categoria": "Caballos y Animales Mecedores",
            "subcategorias": []
          },
          {
            "categoria": "Centros de Actividades",
            "subcategorias": []
          },
          {
            "categoria": "Estructuras de Juego para Interiores",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Bloques",
            "subcategorias": []
          },
          {
            "categoria": "Juguetes con Sonido",
            "subcategorias": []
          },
          {
            "categoria": "Juguetes de Ba\u00f1o",
            "subcategorias": []
          },
          {
            "categoria": "Juguetes de Habilidades Motoras",
            "subcategorias": []
          },
          {
            "categoria": "Juguetes para Beb\u00e9s",
            "subcategorias": []
          },
          {
            "categoria": "Trompos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Mu\u00f1ecas y Accesorios",
        "subcategorias": [
          {
            "categoria": "Accesorios de Casa de Mu\u00f1ecas",
            "subcategorias": []
          },
          {
            "categoria": "Accesorios para Mu\u00f1ecas",
            "subcategorias": []
          },
          {
            "categoria": "Casas de Mu\u00f1ecas",
            "subcategorias": []
          },
          {
            "categoria": "Mu\u00f1ecas",
            "subcategorias": []
          },
          {
            "categoria": "Mu\u00f1ecas Recortables y Magn\u00e9ticas",
            "subcategorias": []
          },
          {
            "categoria": "Sets de Juego",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Mu\u00f1ecos, Figuras y Sets de Juego",
        "subcategorias": [
          {
            "categoria": "Edificios y Paisajes",
            "subcategorias": []
          },
          {
            "categoria": "Figuras de Acci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Juegos",
            "subcategorias": []
          },
          {
            "categoria": "Mu\u00f1ecos y Figuras Articulados",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Peluches",
        "subcategorias": [
          {
            "categoria": "Animales y Figuras",
            "subcategorias": []
          },
          {
            "categoria": "Cojines de Peluche",
            "subcategorias": []
          },
          {
            "categoria": "Conjuntos de Juguetes y Mazadas de Felpa",
            "subcategorias": []
          },
          {
            "categoria": "Figuras de Juguete Interactivo de Felpa",
            "subcategorias": []
          },
          {
            "categoria": "Mu\u00f1ecas de Trapo",
            "subcategorias": []
          },
          {
            "categoria": "Ropa y Accesorios de Animales de Peluche",
            "subcategorias": []
          },
          {
            "categoria": "T\u00edteres de Peluche",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Radiocontrol",
        "subcategorias": [
          {
            "categoria": "Drones",
            "subcategorias": []
          },
          {
            "categoria": "Piezas y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Robots",
            "subcategorias": []
          },
          {
            "categoria": "Veh\u00edculos controlados por aplicaci\u00f3n y control remoto",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Rompecabezas",
        "subcategorias": [
          {
            "categoria": "Accesorios para Rompecabezas",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Preguntas Capciosas",
            "subcategorias": []
          },
          {
            "categoria": "Rompecabezas 3-D",
            "subcategorias": []
          },
          {
            "categoria": "Rompecabezas T\u00edpicos",
            "subcategorias": []
          },
          {
            "categoria": "Rompecabezas con Mango",
            "subcategorias": []
          },
          {
            "categoria": "Rompecabezas de Madera",
            "subcategorias": []
          },
          {
            "categoria": "Rompecabezas de Suelo",
            "subcategorias": []
          },
          {
            "categoria": "Sudokus",
            "subcategorias": []
          },
          {
            "categoria": "Tapetes para Rompecabezas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "T\u00edteres y Escenarios para T\u00edteres",
        "subcategorias": [
          {
            "categoria": "Marionetas de Ventr\u00edlocuo",
            "subcategorias": []
          },
          {
            "categoria": "T\u00edteres de Dedos",
            "subcategorias": []
          },
          {
            "categoria": "T\u00edteres de Mano",
            "subcategorias": []
          },
          {
            "categoria": "T\u00edteres de Peluche",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Veh\u00edculos de Juguete",
        "subcategorias": [
          {
            "categoria": "Aerodeslizadores",
            "subcategorias": []
          },
          {
            "categoria": "Ambulancias",
            "subcategorias": []
          },
          {
            "categoria": "Autobuses",
            "subcategorias": []
          },
          {
            "categoria": "Autos y autos de carreras",
            "subcategorias": []
          },
          {
            "categoria": "Aviones",
            "subcategorias": []
          },
          {
            "categoria": "Camiones",
            "subcategorias": []
          },
          {
            "categoria": "Coches Slot, Pistas y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Cohetes",
            "subcategorias": []
          },
          {
            "categoria": "Cohetes y Naves Espaciales",
            "subcategorias": []
          },
          {
            "categoria": "Embarcaciones",
            "subcategorias": []
          },
          {
            "categoria": "Helic\u00f3pteros",
            "subcategorias": []
          },
          {
            "categoria": "Juguetes de Dedo",
            "subcategorias": []
          },
          {
            "categoria": "Motocicletas",
            "subcategorias": []
          },
          {
            "categoria": "Naves Espaciales",
            "subcategorias": []
          },
          {
            "categoria": "Rastreadores",
            "subcategorias": []
          },
          {
            "categoria": "Scooters",
            "subcategorias": []
          },
          {
            "categoria": "Sets de Juego para Veh\u00edculos de Juguete",
            "subcategorias": []
          },
          {
            "categoria": "Tractores",
            "subcategorias": []
          },
          {
            "categoria": "Trenes y Tranv\u00edas",
            "subcategorias": []
          },
          {
            "categoria": "Veh\u00edculos Blindados de Combate",
            "subcategorias": []
          },
          {
            "categoria": "Veh\u00edculos de Construcci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Veh\u00edculos todo terreno",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Otros",
        "subcategorias": [
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      }
    ]
  },
  {
    "categoria": "Industria, Empresas y Ciencia ",
    "subcategorias": [
      {
        "categoria": "Medici\u00f3n e Inspecci\u00f3n",
        "subcategorias": [
          {
            "categoria": "B\u00e1sculas",
            "subcategorias": []
          },
          {
            "categoria": "Calibraci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Calidad del Agua e Instrumentaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Flujo y Calidad del Aire",
            "subcategorias": []
          },
          {
            "categoria": "Medici\u00f3n Dimensional",
            "subcategorias": []
          },
          {
            "categoria": "Movimiento, Velocidad y Fuerza",
            "subcategorias": []
          },
          {
            "categoria": "Pruebas El\u00e9ctricas",
            "subcategorias": []
          },
          {
            "categoria": "Registradores y Adquisici\u00f3n de Datos",
            "subcategorias": []
          },
          {
            "categoria": "Inclin\u00f3metros",
            "subcategorias": []
          },
          {
            "categoria": "Medici\u00f3n del sonido",
            "subcategorias": []
          },
          {
            "categoria": "Probadores de redes y cables",
            "subcategorias": []
          },
          {
            "categoria": "Sensores",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Seguridad",
        "subcategorias": [
          {
            "categoria": "Avisos y Se\u00f1alizaci\u00f3n de Seguridad",
            "subcategorias": []
          },
          {
            "categoria": "Capacitaci\u00f3n en Seguridad",
            "subcategorias": []
          },
          {
            "categoria": "Equipos de Respuesta a Emergencias",
            "subcategorias": []
          },
          {
            "categoria": "Manipulaci\u00f3n de Materiales Peligrosos",
            "subcategorias": []
          },
          {
            "categoria": "Material y Accesorios de Seguridad Laboral",
            "subcategorias": []
          },
          {
            "categoria": "Productos de Bloqueo y Etiquetado",
            "subcategorias": []
          },
          {
            "categoria": "Productos de Seguridad para Instalaciones",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Limpieza y Saneamiento",
        "subcategorias": [
          {
            "categoria": "Accesorios de Ba\u00f1o",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas de Limpieza",
            "subcategorias": []
          },
          {
            "categoria": "Productos de Cuidado Personal",
            "subcategorias": []
          },
          {
            "categoria": "Productos de Mantenimiento de Pisos",
            "subcategorias": []
          },
          {
            "categoria": "Productos de Papel",
            "subcategorias": []
          },
          {
            "categoria": "Recipientes y Bolsas para Desecho",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Otros",
        "subcategorias": [
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      }
    ]
  },
  {
    "categoria": "Mascotas",
    "subcategorias": [
      {
        "categoria": "Animales Peque\u00f1os",
        "subcategorias": [
          {
            "categoria": "Art\u00edculos de Salud",
            "subcategorias": []
          },
          {
            "categoria": "Ruedas de Ejercicio",
            "subcategorias": []
          },
          {
            "categoria": "Casas y H\u00e1bitats",
            "subcategorias": []
          },
          {
            "categoria": "Collares, Arneses y Correas",
            "subcategorias": []
          },
          {
            "categoria": "Comida",
            "subcategorias": []
          },
          {
            "categoria": "Eliminadores de Olores y Manchas",
            "subcategorias": []
          },
          {
            "categoria": "Transportadoras",
            "subcategorias": []
          },
          {
            "categoria": "Juguetes",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Aves Dom\u00e9sticas",
        "subcategorias": [
          {
            "categoria": "Accesorios para Jaula Protectora",
            "subcategorias": []
          },
          {
            "categoria": "Transportadoras",
            "subcategorias": []
          },
          {
            "categoria": "Comida",
            "subcategorias": []
          },
          {
            "categoria": "Jaulas y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Juguetes",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Caballos",
        "subcategorias": [
          {
            "categoria": "Art\u00edculos de Salud",
            "subcategorias": []
          },
          {
            "categoria": "Art\u00edculos para Comida y Agua",
            "subcategorias": []
          },
          {
            "categoria": "Cobijas y S\u00e1banas",
            "subcategorias": []
          },
          {
            "categoria": "Herraduras y Zapatos",
            "subcategorias": []
          },
          {
            "categoria": "Premios",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Gatos",
        "subcategorias": [
          {
            "categoria": "Arena y Adiestramiento para Evacuar",
            "subcategorias": []
          },
          {
            "categoria": "Camas y Muebles",
            "subcategorias": []
          },
          {
            "categoria": "Collares, Arneses y Correas",
            "subcategorias": []
          },
          {
            "categoria": "Comida",
            "subcategorias": []
          },
          {
            "categoria": "Control de Pulgas, Piojos y Garrapatas",
            "subcategorias": []
          },
          {
            "categoria": "Criptas y Funerales",
            "subcategorias": []
          },
          {
            "categoria": "Gateras, Escalones, Redes y Corrales",
            "subcategorias": []
          },
          {
            "categoria": "Higiene",
            "subcategorias": []
          },
          {
            "categoria": "Juguetes",
            "subcategorias": []
          },
          {
            "categoria": "Repelentes Educativos",
            "subcategorias": []
          },
          {
            "categoria": "Ropas",
            "subcategorias": []
          },
          {
            "categoria": "Transportadoras y Carriolas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Insectos",
        "subcategorias": [
          {
            "categoria": "Accesorios para Terrarios",
            "subcategorias": []
          },
          {
            "categoria": "Art\u00edculos de Salud",
            "subcategorias": []
          },
          {
            "categoria": "Comida",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Perros",
        "subcategorias": [
          {
            "categoria": "Accesorios y Ropa",
            "subcategorias": []
          },
          {
            "categoria": "Amarres, Estacas y Cercas Inal\u00e1mbricas",
            "subcategorias": []
          },
          {
            "categoria": "Arena y Adiestramiento para Evacuar",
            "subcategorias": []
          },
          {
            "categoria": "Camas y Muebles",
            "subcategorias": []
          },
          {
            "categoria": "Casas, Perreras y Corrales",
            "subcategorias": []
          },
          {
            "categoria": "Collares, Arneses y Correas",
            "subcategorias": []
          },
          {
            "categoria": "Comida",
            "subcategorias": []
          },
          {
            "categoria": "Control de Pulgas, Piojos y Garrapatas",
            "subcategorias": []
          },
          {
            "categoria": "Criptas y Funerales",
            "subcategorias": []
          },
          {
            "categoria": "Higiene",
            "subcategorias": []
          },
          {
            "categoria": "Juguetes",
            "subcategorias": []
          },
          {
            "categoria": "Puertas, Rejas y Rampas",
            "subcategorias": []
          },
          {
            "categoria": "Transportadoras y Productos para Viajar",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Reptiles y Anfibios",
        "subcategorias": [
          {
            "categoria": "Camas, Arena Y Sustrato para Terrarios",
            "subcategorias": []
          },
          {
            "categoria": "Comida",
            "subcategorias": []
          },
          {
            "categoria": "Cubiertas para Terrarios",
            "subcategorias": []
          },
          {
            "categoria": "Decoraci\u00f3n para H\u00e1bitats",
            "subcategorias": []
          },
          {
            "categoria": "Term\u00f3metros",
            "subcategorias": []
          },
          {
            "categoria": "Terrarios",
            "subcategorias": []
          },
          {
            "categoria": "Transportadoras",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Otros",
        "subcategorias": [
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      }
    ]
  },
  {
    "categoria": "Musica",
    "subcategorias": [
      {
        "categoria": "Clasica",
        "subcategorias": [
          {
            "categoria": "Clasica",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Country",
        "subcategorias": [
          {
            "categoria": "Bluegrass",
            "subcategorias": []
          },
          {
            "categoria": "Country Alternativo y Estadounidense",
            "subcategorias": []
          },
          {
            "categoria": "Country Contempor\u00e1neo",
            "subcategorias": []
          },
          {
            "categoria": "Honky-Tonk",
            "subcategorias": []
          },
          {
            "categoria": "Swing Western",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Dance y Electronica",
        "subcategorias": [
          {
            "categoria": "Ambient",
            "subcategorias": []
          },
          {
            "categoria": "Dance Mundial",
            "subcategorias": []
          },
          {
            "categoria": "Electr\u00f3nica",
            "subcategorias": []
          },
          {
            "categoria": "House",
            "subcategorias": []
          },
          {
            "categoria": "Tecno",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Folk",
        "subcategorias": [
          {
            "categoria": "Folk Contempor\u00e1nea",
            "subcategorias": []
          },
          {
            "categoria": "Folk Tradicional",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Hard Rock y Metal",
        "subcategorias": [
          {
            "categoria": "Death Metal",
            "subcategorias": []
          },
          {
            "categoria": "Hard Rock",
            "subcategorias": []
          },
          {
            "categoria": "Metal Alternativo",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Indie y Alternativo",
        "subcategorias": [
          {
            "categoria": "Cantautores",
            "subcategorias": []
          },
          {
            "categoria": "Hardcore y Punk",
            "subcategorias": []
          },
          {
            "categoria": "Indie y Lo-Fi",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Jazz",
        "subcategorias": [
          {
            "categoria": "Acid Jazz",
            "subcategorias": []
          },
          {
            "categoria": "Bebop",
            "subcategorias": []
          },
          {
            "categoria": "Jazz Swing",
            "subcategorias": []
          },
          {
            "categoria": "Jazz Tradicional",
            "subcategorias": []
          },
          {
            "categoria": "Posbebop Moderno",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Pop",
        "subcategorias": [
          {
            "categoria": "Cantautores",
            "subcategorias": []
          },
          {
            "categoria": "Disco",
            "subcategorias": []
          },
          {
            "categoria": "Pop Dance",
            "subcategorias": []
          },
          {
            "categoria": "Rock Pop",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Otros",
        "subcategorias": [
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      }
    ]
  },
  {
    "categoria": "Oficina y Papeleria",
    "subcategorias": [
      {
        "categoria": "Arte y Manualidades",
        "subcategorias": [
          {
            "categoria": "Estuches, Almacenaje y Transporte",
            "subcategorias": []
          },
          {
            "categoria": "Herramientas de Corte",
            "subcategorias": []
          },
          {
            "categoria": "Muebles y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Calendarios, Agendas y Organizadores Personales",
        "subcategorias": [
          {
            "categoria": "Agendas",
            "subcategorias": []
          },
          {
            "categoria": "Calendarios de Escritorio y Suministros",
            "subcategorias": []
          },
          {
            "categoria": "Repuestos de Agendas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Electr\u00f3nicos de Oficina",
        "subcategorias": [
          {
            "categoria": "Acesorios",
            "subcategorias": []
          },
          {
            "categoria": "Cartuchos de Tinta",
            "subcategorias": []
          },
          {
            "categoria": "Enmicadoras",
            "subcategorias": []
          },
          {
            "categoria": "Impresoras",
            "subcategorias": []
          },
          {
            "categoria": "Proyectores",
            "subcategorias": []
          },
          {
            "categoria": "Rotuladores",
            "subcategorias": []
          },
          {
            "categoria": "Trituradores",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Material Escolar y Educativo",
        "subcategorias": [
          {
            "categoria": "Cuadernos de Asistencia y de Clases",
            "subcategorias": []
          },
          {
            "categoria": "Decoraci\u00f3n para las Aulas",
            "subcategorias": []
          },
          {
            "categoria": "Juegos de Geometr\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Material de Educaci\u00f3n Infantil",
            "subcategorias": []
          },
          {
            "categoria": "Material Educativo",
            "subcategorias": []
          },
          {
            "categoria": "Tijeras",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Plumas, L\u00e1pices y \u00datiles de Escritura",
        "subcategorias": [
          {
            "categoria": "Crayones",
            "subcategorias": []
          },
          {
            "categoria": "Gises",
            "subcategorias": []
          },
          {
            "categoria": "Gomas y Art\u00edculos para Corregir",
            "subcategorias": []
          },
          {
            "categoria": "L\u00e1pices",
            "subcategorias": []
          },
          {
            "categoria": "Marcadores y Resaltadores",
            "subcategorias": []
          },
          {
            "categoria": "Plumas y Repuestos",
            "subcategorias": []
          },
          {
            "categoria": "Sacapuntas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Productos de Papel para Oficina",
        "subcategorias": [
          {
            "categoria": "Cuadernos, Blocs de Notas y Diarios",
            "subcategorias": []
          },
          {
            "categoria": "Papel",
            "subcategorias": []
          },
          {
            "categoria": "Tarjetas y Cartulinas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Otros",
        "subcategorias": [
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      }
    ]
  },
  {
    "categoria": "Peliculas y Series de TV",
    "subcategorias": [
      {
        "categoria": "Pel\u00edculas",
        "subcategorias": [
          {
            "categoria": "Peliculas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "TV",
        "subcategorias": [
          {
            "categoria": "TV",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Otros",
        "subcategorias": [
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      }
    ]
  },
  {
    "categoria": "Ropa/Zapatos/Accesorios - Mujer",
    "subcategorias": [
      {
        "categoria": "Vestidos",
        "subcategorias": [
          {
            "categoria": "Casual",
            "subcategorias": []
          },
          {
            "categoria": "Ceremonia y Eventos",
            "subcategorias": []
          },
          {
            "categoria": "C\u00f3ctel",
            "subcategorias": []
          },
          {
            "categoria": "Fiesta",
            "subcategorias": []
          },
          {
            "categoria": "Oficina",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Pantalones",
        "subcategorias": [
          {
            "categoria": "Pantalones",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Tenis",
        "subcategorias": [
          {
            "categoria": "Alpargatas para Mujer",
            "subcategorias": []
          },
          {
            "categoria": "Botas para Mujer",
            "subcategorias": []
          },
          {
            "categoria": "Calzado de Uniformes, T\u00e9cnico y de Seguridad de Mujer",
            "subcategorias": []
          },
          {
            "categoria": "Casuales para Mujer",
            "subcategorias": []
          },
          {
            "categoria": "Calzado Deportivo para Mujer",
            "subcategorias": []
          },
          {
            "categoria": "Flats para Mujer",
            "subcategorias": []
          },
          {
            "categoria": "Formales para Mujer",
            "subcategorias": []
          },
          {
            "categoria": "Mocasines para Mujer",
            "subcategorias": []
          },
          {
            "categoria": "N\u00e1uticos para Mujer",
            "subcategorias": []
          },
          {
            "categoria": "Pantuflas para Mujer",
            "subcategorias": []
          },
          {
            "categoria": "Sandalias de Piso para Mujer",
            "subcategorias": []
          },
          {
            "categoria": "Sandalias de Tac\u00f3n para Mujer",
            "subcategorias": []
          },
          {
            "categoria": "Zapatillas para Mujer",
            "subcategorias": []
          },
          {
            "categoria": "Zuecos para Mujer",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Tops",
        "subcategorias": [
          {
            "categoria": "Blusas y Camisas",
            "subcategorias": []
          },
          {
            "categoria": "Henleys",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Chamarras",
        "subcategorias": [
          {
            "categoria": "Chamarras",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Relojes",
        "subcategorias": [
          {
            "categoria": "Correas de Reloj",
            "subcategorias": []
          },
          {
            "categoria": "Relojes de Bolsillo",
            "subcategorias": []
          },
          {
            "categoria": "Relojes de Pulsera",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Bolsas",
        "subcategorias": [
          {
            "categoria": "Bolsas de Tela y de Playa",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas Cross-Body",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas de Asas",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas de Mano",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas Hobos y al Hombro",
            "subcategorias": []
          },
          {
            "categoria": "Mochilas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Joyeria",
        "subcategorias": [
          {
            "categoria": "Anillos",
            "subcategorias": []
          },
          {
            "categoria": "Aretes",
            "subcategorias": []
          },
          {
            "categoria": "Collares",
            "subcategorias": []
          },
          {
            "categoria": "Pulseras",
            "subcategorias": []
          },
          {
            "categoria": "Tobilleras",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Otros",
        "subcategorias": [
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      }
    ]
  },
  {
    "categoria": "Ropa/Zapatos/Accesorios - Hombre",
    "subcategorias": [
      {
        "categoria": "Chamarras",
        "subcategorias": [
          {
            "categoria": "Chamarras",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Pantalones",
        "subcategorias": [
          {
            "categoria": "Pantalones",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Playeras",
        "subcategorias": [
          {
            "categoria": "Camisas Casuales",
            "subcategorias": []
          },
          {
            "categoria": "Camisas de Vestir",
            "subcategorias": []
          },
          {
            "categoria": "Camisas Formales",
            "subcategorias": []
          },
          {
            "categoria": "Playeras de Manga Corta",
            "subcategorias": []
          },
          {
            "categoria": "Playeras de Manga Larga",
            "subcategorias": []
          },
          {
            "categoria": "Playeras sin Mangas",
            "subcategorias": []
          },
          {
            "categoria": "Polos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Accesorios",
        "subcategorias": [
          {
            "categoria": "Bandas Deportivas para la Cabeza",
            "subcategorias": []
          },
          {
            "categoria": "Bufandas",
            "subcategorias": []
          },
          {
            "categoria": "Carteras y Estuches",
            "subcategorias": []
          },
          {
            "categoria": "Cinturones",
            "subcategorias": []
          },
          {
            "categoria": "Corbatas y Mo\u00f1os",
            "subcategorias": []
          },
          {
            "categoria": "Gafas y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Guantes",
            "subcategorias": []
          },
          {
            "categoria": "Llaveros",
            "subcategorias": []
          },
          {
            "categoria": "Pa\u00f1uelos",
            "subcategorias": []
          },
          {
            "categoria": "Sombreros y Gorras",
            "subcategorias": []
          },
          {
            "categoria": "Tirantes",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Sudaderas",
        "subcategorias": [
          {
            "categoria": "Sudaderas con Capucha",
            "subcategorias": []
          },
          {
            "categoria": "Sudaderas sin Capucha",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Zapatos",
        "subcategorias": [
          {
            "categoria": "Alpargatas para Hombre",
            "subcategorias": []
          },
          {
            "categoria": "Botas para Hombre",
            "subcategorias": []
          },
          {
            "categoria": "Calzado de Uniformes, T\u00e9cnico y de Seguridad de Hombre",
            "subcategorias": []
          },
          {
            "categoria": "Casuales para Hombre",
            "subcategorias": []
          },
          {
            "categoria": "Calzado Deportivo para Hombre",
            "subcategorias": []
          },
          {
            "categoria": "Formales para Hombre",
            "subcategorias": []
          },
          {
            "categoria": "Mocasines para Hombre",
            "subcategorias": []
          },
          {
            "categoria": "N\u00e1uticos para Hombre",
            "subcategorias": []
          },
          {
            "categoria": "Pantuflas para Hombre",
            "subcategorias": []
          },
          {
            "categoria": "Sandalias Formales para Hombre",
            "subcategorias": []
          },
          {
            "categoria": "Sandalias de Playa para Hombre",
            "subcategorias": []
          },
          {
            "categoria": "Zuecos para Hombre",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Camisas",
        "subcategorias": [
          {
            "categoria": "Camisas Casuales",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Relojes",
        "subcategorias": [
          {
            "categoria": "Correas de Reloj",
            "subcategorias": []
          },
          {
            "categoria": "Relojes de Bolsillo",
            "subcategorias": []
          },
          {
            "categoria": "Relojes de Pulsera",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Otros",
        "subcategorias": [
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      }
    ]
  },
  {
    "categoria": "Ropa, Zapatos y Accesorios",
    "subcategorias": [
      {
        "categoria": "Ni\u00f1os",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Relojes",
            "subcategorias": []
          },
          {
            "categoria": "Ropa",
            "subcategorias": []
          },
          {
            "categoria": "Zapatos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Ni\u00f1as",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Bolsas de Mano y al Hombro",
            "subcategorias": []
          },
          {
            "categoria": "Joyer\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Relojes",
            "subcategorias": []
          },
          {
            "categoria": "Ropa",
            "subcategorias": []
          },
          {
            "categoria": "Zapatos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Beb\u00e9s (Ni\u00f1a, Ni\u00f1o)",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Ropa",
            "subcategorias": []
          },
          {
            "categoria": "Zapatos para Beb\u00e9s (Ni\u00f1a, Ni\u00f1o)",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Otros",
        "subcategorias": [
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      }
    ]
  },
  {
    "categoria": "Salud y Cuidado Personal",
    "subcategorias": [
      {
        "categoria": "Ayuda para la Vida Diaria, el Cuidado en Casa y la Movilidad",
        "subcategorias": [
          {
            "categoria": "Ayudas para la vida diaria",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Ba\u00f1o y Cuerpo",
        "subcategorias": [
          {
            "categoria": "Accesorios Ba\u00f1o y Cuerpo",
            "subcategorias": []
          },
          {
            "categoria": "Aditivos para el Ba\u00f1o",
            "subcategorias": []
          },
          {
            "categoria": "Desodorantes y Antitranspirantes",
            "subcategorias": []
          },
          {
            "categoria": "Exfoliantes y Tratamientos Corporales",
            "subcategorias": []
          },
          {
            "categoria": "Limpieza Personal",
            "subcategorias": []
          },
          {
            "categoria": "Sets",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Bienestar y Relajaci\u00f3n",
        "subcategorias": [
          {
            "categoria": "Masaje y Relajaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Metodos Alternativos",
            "subcategorias": []
          },
          {
            "categoria": "Monedas y Fichas de Sobriedad",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Cuidado de Boca",
        "subcategorias": [
          {
            "categoria": "Alivio de la Resequedad Bucal",
            "subcategorias": []
          },
          {
            "categoria": "Blanqueadores Dentales",
            "subcategorias": []
          },
          {
            "categoria": "Cepillos de Dientes y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Cuidado Dental para Beb\u00e9s y Ni\u00f1os",
            "subcategorias": []
          },
          {
            "categoria": "Enjuagues Bucales",
            "subcategorias": []
          },
          {
            "categoria": "Kits de Cuidado Bucal",
            "subcategorias": []
          },
          {
            "categoria": "Limpiadores de Lengua",
            "subcategorias": []
          },
          {
            "categoria": "Limpieza Interdental",
            "subcategorias": []
          },
          {
            "categoria": "Pastas de Dientes",
            "subcategorias": []
          },
          {
            "categoria": "Refrescantes de Aliento",
            "subcategorias": []
          },
          {
            "categoria": "Suministros de Ortodoncia",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Cuidado de Ojos",
        "subcategorias": [
          {
            "categoria": "Anteojos de Bloqueo de Luz Azul",
            "subcategorias": []
          },
          {
            "categoria": "Cuidado para Lentes y Anteojos",
            "subcategorias": []
          },
          {
            "categoria": "Lentes de Lectura y Anteojos",
            "subcategorias": []
          },
          {
            "categoria": "Marcos para Lentes y Anteojos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Cuidado del Hogar y Limpieza",
        "subcategorias": [
          {
            "categoria": "Bater\u00edas",
            "subcategorias": []
          },
          {
            "categoria": "Cuidado de Zapatos",
            "subcategorias": []
          },
          {
            "categoria": "Encendedores y Cerillos",
            "subcategorias": []
          },
          {
            "categoria": "Insecticidas y Pesticidas",
            "subcategorias": []
          },
          {
            "categoria": "Lavander\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Lavatrastes y Lavavajillas",
            "subcategorias": []
          },
          {
            "categoria": "Papeles, Envolturas y Bolsas",
            "subcategorias": []
          },
          {
            "categoria": "Productos y Utensilios de Limpieza",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Cuidado \u00cdntimo e Higiene",
        "subcategorias": [
          {
            "categoria": "Copas Menstruales",
            "subcategorias": []
          },
          {
            "categoria": "Cuidado \u00cdntimo",
            "subcategorias": []
          },
          {
            "categoria": "Protectores Diarios",
            "subcategorias": []
          },
          {
            "categoria": "Toallas Sanitarias",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Cuidado para Bebes y Ni\u00f1os",
        "subcategorias": [
          {
            "categoria": "Ba\u00f1o",
            "subcategorias": []
          },
          {
            "categoria": "B\u00e1sculas",
            "subcategorias": []
          },
          {
            "categoria": "Cambio de Pa\u00f1ales",
            "subcategorias": []
          },
          {
            "categoria": "Cuidado de la Piel",
            "subcategorias": []
          },
          {
            "categoria": "Cuidado Dental",
            "subcategorias": []
          },
          {
            "categoria": "Higiene",
            "subcategorias": []
          },
          {
            "categoria": "Lactancia y Alimentaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Term\u00f3metros",
            "subcategorias": []
          },
          {
            "categoria": "Toallitas y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Tratamientos de Fr\u00edo y Calor",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Equipo y Suministros M\u00e9dicos",
        "subcategorias": [
          {
            "categoria": "Accesorios de Ayuda para la Movilidad y Vida Diaria",
            "subcategorias": []
          },
          {
            "categoria": "Cloth Face Masks & Accessories",
            "subcategorias": []
          },
          {
            "categoria": "M\u00e1scaras Desechables para Rostro",
            "subcategorias": []
          },
          {
            "categoria": "M\u00e1scaras Faciales M\u00e9dicas y Protecciones",
            "subcategorias": []
          },
          {
            "categoria": "Monitores de Salud y Diagn\u00f3sticos",
            "subcategorias": []
          },
          {
            "categoria": "Prendas de compresi\u00f3n m\u00e9dica",
            "subcategorias": []
          },
          {
            "categoria": "Productos Post Mastectom\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Tirantes, F\u00e9rulas y Soportes",
            "subcategorias": []
          },
          {
            "categoria": "Utensilios de Ayuda para Terapia Ocupacional y F\u00edsica",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Salud y Tratamientos",
        "subcategorias": [
          {
            "categoria": "Cuidado del O\u00eddo",
            "subcategorias": []
          },
          {
            "categoria": "Cuidado de los Ojos",
            "subcategorias": []
          },
          {
            "categoria": "Cuidado de Pies",
            "subcategorias": []
          },
          {
            "categoria": "Incontinencia",
            "subcategorias": []
          },
          {
            "categoria": "Inhaladores de Vapor, Nebulizadores y Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Metodos Alternativos",
            "subcategorias": []
          },
          {
            "categoria": "Primeros Auxilios",
            "subcategorias": []
          },
          {
            "categoria": "Salud de la Mujer",
            "subcategorias": []
          },
          {
            "categoria": "Sue\u00f1o y Ronquidos",
            "subcategorias": []
          },
          {
            "categoria": "Medicamento de Venta Libre",
            "subcategorias": []
          },
          {
            "categoria": "Tratamientos para Piojos",
            "subcategorias": []
          },
          {
            "categoria": "Terapias de Fr\u00edo y Calor",
            "subcategorias": []
          },
          {
            "categoria": "Utensilios para Guardar Medicamentos",
            "subcategorias": []
          },
          {
            "categoria": "Repelentes de Insectos y Plagas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Vitaminas y Suplementos",
        "subcategorias": [
          {
            "categoria": "Barras Nutritivas",
            "subcategorias": []
          },
          {
            "categoria": "Botanas & Bebidas Saludables",
            "subcategorias": []
          },
          {
            "categoria": "Productos de Control Nutricional",
            "subcategorias": []
          },
          {
            "categoria": "Suplementos para Deportistas",
            "subcategorias": []
          },
          {
            "categoria": "Vitaminas, Minerales y Suplementos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Otros",
        "subcategorias": [
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      }
    ]
  },
  {
    "categoria": "Software",
    "subcategorias": [
      {
        "categoria": "Casa y Pasatiempos",
        "subcategorias": [
          {
            "categoria": "Artes y Artesan\u00edas",
            "subcategorias": []
          },
          {
            "categoria": "Dise\u00f1o de Casa y Jard\u00edn",
            "subcategorias": []
          },
          {
            "categoria": "Edici\u00f3n en Casa",
            "subcategorias": []
          },
          {
            "categoria": "Familia y Genealog\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Contabilidad y Finanzas",
        "subcategorias": [
          {
            "categoria": "Contabilidad de Negocios",
            "subcategorias": []
          },
          {
            "categoria": "Declaraci\u00f3n de Impuestos",
            "subcategorias": []
          },
          {
            "categoria": "Finanzas Personales",
            "subcategorias": []
          },
          {
            "categoria": "Impresi\u00f3n de Cheques",
            "subcategorias": []
          },
          {
            "categoria": "N\u00f3mina",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Declaraci\u00f3n de Impuestos",
        "subcategorias": [
          {
            "categoria": "Declaraci\u00f3n de Impuestos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Educaci\u00f3n y Consulta",
        "subcategorias": [
          {
            "categoria": "Educaci\u00f3n y Consulta",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Fotograf\u00eda y Dise\u00f1o Gr\u00e1fico",
        "subcategorias": [
          {
            "categoria": "Capacitaci\u00f3n y Tutoriales",
            "subcategorias": []
          },
          {
            "categoria": "Fotograf\u00eda",
            "subcategorias": []
          },
          {
            "categoria": "Ilustraci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Suites de Dise\u00f1o Gr\u00e1fico",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Idiomas y Viajes",
        "subcategorias": [
          {
            "categoria": "Idiomas y Viajes",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "M\u00fasica",
        "subcategorias": [
          {
            "categoria": "Complementos de Audio",
            "subcategorias": []
          },
          {
            "categoria": "Edici\u00f3n y Efectos de MP3",
            "subcategorias": []
          },
          {
            "categoria": "Ense\u00f1anza de Instrumentos",
            "subcategorias": []
          },
          {
            "categoria": "Instrumentos Virtuales",
            "subcategorias": []
          },
          {
            "categoria": "Notaci\u00f3n Musical",
            "subcategorias": []
          },
          {
            "categoria": "Quemado y Etiquetado",
            "subcategorias": []
          },
          {
            "categoria": "Software de Producci\u00f3n Musical",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Negocios y Oficina",
        "subcategorias": [
          {
            "categoria": "Administraci\u00f3n de Documentos",
            "subcategorias": []
          },
          {
            "categoria": "Hojas de C\u00e1lculo",
            "subcategorias": []
          },
          {
            "categoria": "Reconocimiento de Voz",
            "subcategorias": []
          },
          {
            "categoria": "Suites para Oficina",
            "subcategorias": []
          },
          {
            "categoria": "Visualizaci\u00f3n y Presentaci\u00f3n",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Programaci\u00f3n y Desarrollo Web",
        "subcategorias": [
          {
            "categoria": "Programaci\u00f3n y Desarrollo Web",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Redes y Servidores",
        "subcategorias": [
          {
            "categoria": "Administraci\u00f3n de Redes",
            "subcategorias": []
          },
          {
            "categoria": "Firewalls",
            "subcategorias": []
          },
          {
            "categoria": "Licencias de Acceso de Clientes",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Sistemas Operativos",
        "subcategorias": [
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Software para Ni\u00f1os",
        "subcategorias": [
          {
            "categoria": "Arte y Creatividad",
            "subcategorias": []
          },
          {
            "categoria": "Ciencias y Naturaleza",
            "subcategorias": []
          },
          {
            "categoria": "Juegos",
            "subcategorias": []
          },
          {
            "categoria": "Lectura e Idioma",
            "subcategorias": []
          },
          {
            "categoria": "Matem\u00e1ticas",
            "subcategorias": []
          },
          {
            "categoria": "Razonamiento y Soluci\u00f3n de Problemas",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Utilidades de Sistemas",
        "subcategorias": [
          {
            "categoria": "Controladores y Recuperaci\u00f3n de Controladores",
            "subcategorias": []
          },
          {
            "categoria": "Protectores de Pantalla",
            "subcategorias": []
          },
          {
            "categoria": "Utilidades de Internet",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Video",
        "subcategorias": [
          {
            "categoria": "Animaci\u00f3n y Anime",
            "subcategorias": []
          },
          {
            "categoria": "Edici\u00f3n de Video",
            "subcategorias": []
          },
          {
            "categoria": "Quemado y Etiquetado",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Otros",
        "subcategorias": [
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      }
    ]
  },
  {
    "categoria": "Videojuegos",
    "subcategorias": [
      {
        "categoria": "Juegos Linux",
        "subcategorias": [
          {
            "categoria": "Juegos Linux",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Mac",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Contenido Descargable",
            "subcategorias": []
          },
          {
            "categoria": "Juegos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Membres\u00edas y Tarjetas Prepago",
        "subcategorias": [
          {
            "categoria": "Nintendo eShop",
            "subcategorias": []
          },
          {
            "categoria": "PlayStation Network",
            "subcategorias": []
          },
          {
            "categoria": "Xbox Live",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Nintendo Switch",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Consolas",
            "subcategorias": []
          },
          {
            "categoria": "Figuras Interactivas",
            "subcategorias": []
          },
          {
            "categoria": "Juegos",
            "subcategorias": []
          },
          {
            "categoria": "Nintendo eShop",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "PC",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Contenido Descargable",
            "subcategorias": []
          },
          {
            "categoria": "Hardware de Realidad Virtual",
            "subcategorias": []
          },
          {
            "categoria": "Juegos",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "PlayStation 4",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Consolas",
            "subcategorias": []
          },
          {
            "categoria": "Contenido Descargable",
            "subcategorias": []
          },
          {
            "categoria": "Figuras de Juegos Interactivos",
            "subcategorias": []
          },
          {
            "categoria": "Hardware de PlayStation VR",
            "subcategorias": []
          },
          {
            "categoria": "Juegos",
            "subcategorias": []
          },
          {
            "categoria": "Paquetes",
            "subcategorias": []
          },
          {
            "categoria": "PlayStation Network",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "PlayStation 5",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Consolas",
            "subcategorias": []
          },
          {
            "categoria": "Contenido Descargable",
            "subcategorias": []
          },
          {
            "categoria": "Hardware de PlayStation VR2",
            "subcategorias": []
          },
          {
            "categoria": "Juegos",
            "subcategorias": []
          },
          {
            "categoria": "PlayStation Network",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Realidad Virtual",
        "subcategorias": [
          {
            "categoria": "Hardware Aut\u00f3nomo",
            "subcategorias": []
          },
          {
            "categoria": "Hardware de PlayStation VR",
            "subcategorias": []
          },
          {
            "categoria": "Hardware de PlayStation VR2",
            "subcategorias": []
          },
          {
            "categoria": "Hardware para PC",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Sistemas Heredados",
        "subcategorias": [
          {
            "categoria": "ColecoVision",
            "subcategorias": []
          },
          {
            "categoria": "Sistemas Atari",
            "subcategorias": []
          },
          {
            "categoria": "Sistemas de Juego de Mano",
            "subcategorias": []
          },
          {
            "categoria": "Sistemas Nintendo",
            "subcategorias": []
          },
          {
            "categoria": "Sistemas PlayStation",
            "subcategorias": []
          },
          {
            "categoria": "Sistemas Sega",
            "subcategorias": []
          },
          {
            "categoria": "Sistemas Xbox",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Xbox One",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Consolas",
            "subcategorias": []
          },
          {
            "categoria": "Contenido Descargable",
            "subcategorias": []
          },
          {
            "categoria": "Figuras de Juegos Interactivos",
            "subcategorias": []
          },
          {
            "categoria": "Juegos",
            "subcategorias": []
          },
          {
            "categoria": "Paquetes",
            "subcategorias": []
          },
          {
            "categoria": "Xbox Live",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Xbox Series X & S",
        "subcategorias": [
          {
            "categoria": "Accesorios",
            "subcategorias": []
          },
          {
            "categoria": "Consolas",
            "subcategorias": []
          },
          {
            "categoria": "Contenido Descargable",
            "subcategorias": []
          },
          {
            "categoria": "Juegos",
            "subcategorias": []
          },
          {
            "categoria": "Xbox Live",
            "subcategorias": []
          },
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      },
      {
        "categoria": "Otros",
        "subcategorias": [
          {
            "categoria": "Otros",
            "subcategorias": []
          }
        ]
      }
    ]
  }
]'''
  menu_data = json.loads(json_data)
  return render(request, "logo.html", {'menu_data': menu_data})

# def LogIn_Firebase(Email, Password):
#     config = {
#     "apiKey": "AIzaSyDMoLUyDxcIkcJZPeC_RoZelQ8AhxOSAvQ",
#     "authDomain": "pbay-733d6.firebaseapp.com",
#     "databaseURL": "https://pbay-733d6-default-rtdb.firebaseio.com",

#     "storageBucket": "pbay-733d6.appspot.com",
#     "serviceAccount": "./pbay-733d6-firebase-adminsdk-r84zp-e324c11afb.json"
#     }

#     firebase = pyrebase.initialize_app(config)
#     auth = firebase.auth()
#     try:
#         user = auth.sign_in_with_email_and_password(Email, Password)
#         return user
#     except:
#         return False
