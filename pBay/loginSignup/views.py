from django.shortcuts import render
from .form import *
from utils import LogIn_Firebase, signUp_Firebase, firestore_connection, firebaseStorage
from datetime import datetime

# Create your views here.
def home(request):
    form = MiFormulario()
    context = {"form": form, "title": "Login"}
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
                print("False")
                div_content = 'Error en contraseña o correo'
                context['div_content'] = div_content
                return render(request, 'login.html', context)
            else:
                print("True")
                request.session['usuario'] =  result
                userid = request.session['usuario']
                context= {'usuario': result, 'id': userid['localId']}
                return render(request, "log.html", context)
        else:
            div_content = 'Error forma invalida, verifica el correo'
            context['div_content'] = div_content
            return render(request, 'login.html', context)
            
    return render(request, "login.html", context)
    
def log(request):
    return render(request, "log.html")

def signUp(request):
    print('enter signup')
    form = signUpForm()
    context = {"form": form, "title": "signup"}
    print(request)
    if request.method=='POST':
        print('enter req')
        form = signUpForm(request.POST, request.FILES)
        context = {"form": form, "title": "signup"}
        print(form.is_valid())
        print(form.errors)
        if form.is_valid():
            print("Form valid")
            data = form.cleaned_data
            Correo= data["mail"]
            Contra= data["password"]
            result =signUp_Firebase(Correo, Contra)
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
                            'postalCode': data['postalCode'], 'phoneNumber': data['phoneNumber'], 'mail': data['mail']}
                    ref = firestore_connection('users')
                    ref.document(uid).set(uData)
                    #fileStorage = firebaseStorage(uid).put(request.FILES["official_id"])
                    context= {'usuario': result, 'id': result['localId']}
                    return render(request, "signup.html", context)
                except:
                    print('failed create')
        print('not valid')
    print('fail')
    return render(request, "signup.html", context)
    


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