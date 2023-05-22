from django.shortcuts import render
from django.views.generic import View
# Importo Firebase Admin SDK 
# import firebase_admin
 
# # Hacemos uso de credenciales que nos permitirán usar Firebase Admin SDK 
# from firebase_admin import credentials
 
# # Importo el Servicio Firebase Realtime Database 
# from firebase_admin import db
from utils import firestore_connection
def home(request):
    # try:
    #     app = firebase_admin.get_app()
    #     # Iniciamos los servicios de Firebase con las credenciales y el nombre de mi proyecto en Firebase 
    # except ValueError as e:
    #     cred = credentials.Certificate('./pbay-733d6-firebase-adminsdk-r84zp-e324c11afb.json')
    #     firebase_admin.initialize_app(cred, { 'databaseURL':'https://pbay-733d6-default-rtdb.firebaseio.com/'})
	# 	# Accedo a la base de datos, específicamente a la tabla 'postres' 
    # ref = db.reference('data') 
	# #print(ref.get())
    ref = firestore_connection('sample')
    docs = ref.get()
    datos = {}
    for doc in docs:
        #doc.to_dict()
        print(doc.to_dict())
        print(doc.id)
        datos[doc.id] = doc.to_dict()
        print('dict\n',datos)
    print(datos)
    return render(request, "Home.html",{'datos':datos})