# Importo Firebase Admin SDK 
import firebase_admin
 
# Hacemos uso de credenciales que nos permitirán usar Firebase Admin SDK 
from firebase_admin import credentials
 
# Importo el Servicio Firebase Realtime Database 
from firebase_admin import firestore

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