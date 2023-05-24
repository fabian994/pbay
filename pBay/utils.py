# Importo Firebase Admin SDK 

import firebase_admin
 
# Hacemos uso de credenciales que nos permitirán usar Firebase Admin SDK 
from firebase_admin import credentials
 
# Importo el Servicio Firebase Realtime Database 
from firebase_admin import firestore
from firebase_admin import storage
import pyrebase
import datetime

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

cred = credentials.Certificate('./pbay-733d6-firebase-adminsdk-r84zp-e324c11afb.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'pbay-733d6.appspot.com'
})
db = firestore.client()

def LogIn_Firebase(Correo, Contra):
    try:
        user = auth.sign_in_with_email_and_password(Correo, Contra)
        
        return(user)
    except:
        print("Error")
    return False

def signUp_Firebase(Correo, Contra):
    try:
        user = auth.create_user_with_email_and_password(Correo, Contra)
        #return(user["localId"])
        return(user)
    except:
        print("Error")
    return False

def infoProductoUser(Correo, Contra):
    user = auth.sign_in_with_email_and_password(Correo, Contra)
    nombre_coleccion = "transactions"
    coleccion_ref = db.collection(nombre_coleccion)
    documentos = coleccion_ref.get()
    # Itera sobre los documentos
    response=[]
    for documento in documentos:
            # Accede a los datos de cada documento
        datos = documento.to_dict()
        
        tipo = datos['saleType']
        if bool(tipo):
            tipo = "Subasta"
        else:
            tipo = "Venta Directa"
        if datos['buyer_id'] == user["localId"]:
            print(datos)
            # Hacer algo con los datos
            coleccion_ref = db.collection('products')
            document_id = datos['id_prod']
            documento = coleccion_ref.document(document_id).get()
            datosimg = documento.to_dict()
            print(datosimg)        
            ruta_imagen = "products/"+datos['id_prod']+"/"+datosimg['mainImg']
            print(ruta_imagen)
            bucket = storage.bucket()
            imagen_ref = bucket.blob(ruta_imagen)
            expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
            url_imagen = imagen_ref.generate_signed_url(expiration=int(expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
            response.append([documento.id, tipo,  datos['price'], datos['shippingFee'],  datos['deliveryStatus'],  datos['shippingAddress'], url_imagen])
    return response

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

def firebaseStorage(c_bucket):
    # try:
    #     app = firebase_admin.get_app()
       
    # except ValueError as e:
    #     cred = credentials.Certificate('./pbay-733d6-firebase-adminsdk-r84zp-e324c11afb.json')
    #     #firebase_admin.initialize_app(cred, { 'databaseURL':'https://pbay-733d6-default-rtdb.firebaseio.com/'})
    #     #gs://pbay-733d6.appspot.com/
    #     firebase_admin.initialize_app(cred, {
    #         'storageBucket': 'gs://pbay-733d6.appspot.com'
    #     })
    bucket = storage.child(c_bucket).child('user_id')
    return bucket


