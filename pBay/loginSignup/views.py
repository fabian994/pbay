from django.shortcuts import render
from .form import MiFormulario
from utils import LogIn_Firebase


# Create your views here.
def home(request):
    print("Algo")
    form = MiFormulario()
    context = {"form": form, "title": "Login"}
    if request.method=='POST':
        print("Hola2")
        form = MiFormulario(request.POST)
        context = {"form": form, "title": "Login"}
        if form.is_valid():
            print("Form valid")
            data = form.cleaned_data
            Correo= data["campo1"]
            Contra= data["campo2"]
            result =LogIn_Firebase(Correo, Contra)
            if result == False:
                return render(request, 'login.html', context)
            else:
                print(result)
    return render(request, "login.html", context)




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