from django.shortcuts import render, redirect
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import default_storage
from django.contrib import messages
from .form import *
from utils import LogIn_Firebase, signUp_Firebase, firestore_connection, storeOfficialID, infoUser, addDirect
from datetime import datetime
from django.http import JsonResponse
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
            passw= data["password"]
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
                            'postalCode': data['postalCode'], 'phoneNumber': data['phoneNumber'], 'mail': data['mail'], 'status': False, 'maindirection': data['direction1']}
                    ref = firestore_connection('users')
                    ref.document(uid).set(uData)

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
                    return redirect('compras')
                    #return render(request, "signup.html", context) Qwerty*1234
                except Exception as e:
                    print('error: ',e)
                    print('failed create')
        print('not valid')
    print('fail')
    return render(request, "signup.html", context)
    
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
