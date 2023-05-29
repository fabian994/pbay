# Importo Firebase Admin SDK 

import firebase_admin
 
# Hacemos uso de credenciales que nos permitirán usar Firebase Admin SDK 
from firebase_admin import credentials
 
# Importo el Servicio Firebase Realtime Database 
from firebase_admin import firestore
from firebase_admin import storage as st
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
storage = firebase.storage()

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

def infoProductoUser(user, action):
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
            if action == 0:
                # Hacer algo con los datos
                coleccion_ref = db.collection('products')
                document_id = datos['id_prod']
                documento = coleccion_ref.document(document_id).get()
                datosimg = documento.to_dict()       
                ruta_imagen = "products/"+datos['id_prod']+"/"+datosimg['mainImg']
                bucket = st.bucket()
                imagen_ref = bucket.blob(ruta_imagen)
                expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
                url_imagen = imagen_ref.generate_signed_url(expiration=int(expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                response.append([documento.id, tipo,  datos['price'], datos['shippingFee'],  datos['deliveryStatus'],  datos['shippingAddress'], url_imagen, datos['tran_date']])
            if action == 1:
                if tipo == "Subasta":
                    coleccion_ref = db.collection('products')
                    document_id = datos['id_prod']
                    documento = coleccion_ref.document(document_id).get()
                    datosimg = documento.to_dict()       
                    ruta_imagen = "products/"+datos['id_prod']+"/"+datosimg['mainImg']
                    bucket = st.bucket()
                    imagen_ref = bucket.blob(ruta_imagen)
                    expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
                    url_imagen = imagen_ref.generate_signed_url(expiration=int(expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                    response.append([documento.id, tipo,  datos['price'], datos['shippingFee'],  datos['deliveryStatus'],  datos['shippingAddress'], url_imagen, datos['tran_date']])
            if action == 2:
                if tipo == "Venta Directa":
                    coleccion_ref = db.collection('products')
                    document_id = datos['id_prod']
                    documento = coleccion_ref.document(document_id).get()
                    datosimg = documento.to_dict()       
                    ruta_imagen = "products/"+datos['id_prod']+"/"+datosimg['mainImg']
                    bucket = st.bucket()
                    imagen_ref = bucket.blob(ruta_imagen)
                    expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
                    url_imagen = imagen_ref.generate_signed_url(expiration=int(expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                    response.append([documento.id, tipo,  datos['price'], datos['shippingFee'],  datos['deliveryStatus'],  datos['shippingAddress'], url_imagen, datos['tran_date']])
                    
                
    response = sorted(response, key=lambda x: datetime.datetime.strptime(x[7], '%d/%m/%Y').date())
    return response


def infoventas(user, action):
    nombre_coleccion = "products"
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
            
        condition = datos['Condition']
        if bool(tipo):
            condition = "Nuevo"
        else:
            condition = "Usado"
                
        if datos['seller_id'] == user["localId"]:
            if action == 0:
                ruta_imagen = "products/"+documento.id+"/"+datos['mainImg']
                bucket = st.bucket()
                imagen_ref = bucket.blob(ruta_imagen)
                expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
                url_imagen = imagen_ref.generate_signed_url(expiration=int(expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                response.append([datos['prodName'], datos['categories'], datos['prodDesc'], datos['Brand'],datos['Model'], condition , tipo , datos['Price'], datos['shippingFee'], datos['pubDate'], url_imagen])
            if action == 1:
                if tipo == "Subasta":
                    ruta_imagen = "products/"+documento.id+"/"+datos['mainImg']
                    bucket = st.bucket()
                    imagen_ref = bucket.blob(ruta_imagen)
                    expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
                    url_imagen = imagen_ref.generate_signed_url(expiration=int(expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                    response.append([datos['prodName'], datos['categories'], datos['prodDesc'], datos['Brand'],datos['Model'], condition , tipo , datos['Price'], datos['shippingFee'], datos['pubDate'], url_imagen])
                    
            if action == 2:
                if tipo == "Venta Directa":
                    ruta_imagen = "products/"+documento.id+"/"+datos['mainImg']
                    bucket = st.bucket()
                    imagen_ref = bucket.blob(ruta_imagen)
                    expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
                    url_imagen = imagen_ref.generate_signed_url(expiration=int(expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                    response.append([datos['prodName'], datos['categories'], datos['prodDesc'], datos['Brand'],datos['Model'], condition , tipo , datos['Price'], datos['shippingFee'], datos['pubDate'], url_imagen])     
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

def storeOfficialID(uid,name):#Saves user official ID to firebase storage
    # storage.child(path) sets the directory the file is going to be stored, must include filename with extension
    # .put() grabs the local file stored in media and uploads it to firebase
    storedID = storage.child('users/' + str(uid) + '/' + name).put("media/" + name)
    return storedID
