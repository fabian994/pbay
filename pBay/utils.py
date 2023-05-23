# Importo Firebase Admin SDK 

import firebase_admin
 
# Hacemos uso de credenciales que nos permitirán usar Firebase Admin SDK 
from firebase_admin import credentials
 
# Importo el Servicio Firebase Realtime Database 
from firebase_admin import firestore

import pyrebase

config = {
  "apiKey": "AIzaSyDMoLUyDxcIkcJZPeC_RoZelQ8AhxOSAvQ",
  "authDomain": "pbay-733d6.firebaseapp.com",
  "databaseURL": "https://pbay-733d6-default-rtdb.firebaseio.com",
  "projectId": "pbay-733d6",
  "storageBucket": "pbay-733d6.appspot.com",
  "messagingSenderId": "336573451844",
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
database=firebase.database()

def LogIn_Firebase(Correo, Contra):
    try:
        user = auth.sign_in_with_email_and_password(Correo, Contra)
        #return(user["localId"])
        return(user)
    except:
        print("Error")
    return False

    
    
def firestore_connection(col):
    try:
        app = firebase_admin.get_app()
       
    except ValueError as e:
        cred = credentials.Certificate('./pbay-733d6-firebase-adminsdk-r84zp-e324c11afb.json')
        #firebase_admin.initialize_app(cred, { 'databaseURL':'https://pbay-733d6-default-rtdb.firebaseio.com/'})
        firebase_admin.initialize_app(cred)
        
    db=firestore.client()
    ref = db.collection(col) 
    return ref
	#print(ref.get())