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
database = firebase.database()
storage = firebase.storage()

cred = credentials.Certificate(
    './pbay-733d6-firebase-adminsdk-r84zp-e324c11afb.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'pbay-733d6.appspot.com'
})
db = firestore.client()


def LogIn_Firebase(Correo, Contra):
    try:
        user = auth.sign_in_with_email_and_password(Correo, Contra)
        docs = db.collection('users').where('oficial_id', '==', user['localId']).get()
        response=""
        for doc in docs:
            data = doc.to_dict()
            if data['status']:
                return (user)
        else:
            print("Status falso")
            return 'NoAuthorized'
    except:
        print("Error")
    return False


def signUp_Firebase(Correo, Contra):
    try:
        user = auth.create_user_with_email_and_password(Correo, Contra)
        # return(user["localId"])
        return (user)
    except:
        print("Error")
    return False


def infoUser(user):
    docs = db.collection('users').where('oficial_id', '==', user).get()
    response = ""
    for doc in docs:
        data = doc.to_dict()
        response = [data['name']+" "+data['lastNames'],
                    data['mail'], data['phoneNumber'], data['birthDate']]
    return (response)


def infoProductoUser(user, action):
    nombre_coleccion = "transactions"
    coleccion_ref = db.collection(nombre_coleccion)
    documentos = coleccion_ref.get()
    # Itera sobre los documentos
    response = []
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
                ruta_imagen = "products/" + \
                    datos['id_prod']+"/"+datosimg['mainImg']
                bucket = st.bucket()
                imagen_ref = bucket.blob(ruta_imagen)
                expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
                url_imagen = imagen_ref.generate_signed_url(expiration=int(
                    expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                response.append([documento.id, tipo,  datos['price'], datos['shippingFee'],
                                datos['deliveryStatus'],  datos['shippingAddress'], url_imagen, datos['tran_date']])
            if action == 1:
                if tipo == "Subasta":
                    coleccion_ref = db.collection('products')
                    document_id = datos['id_prod']
                    documento = coleccion_ref.document(document_id).get()
                    datosimg = documento.to_dict()
                    ruta_imagen = "products/" + \
                        datos['id_prod']+"/"+datosimg['mainImg']
                    bucket = st.bucket()
                    imagen_ref = bucket.blob(ruta_imagen)
                    expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
                    url_imagen = imagen_ref.generate_signed_url(expiration=int(
                        expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                    response.append([documento.id, tipo,  datos['price'], datos['shippingFee'],
                                    datos['deliveryStatus'],  datos['shippingAddress'], url_imagen, datos['tran_date']])
            if action == 2:
                if tipo == "Venta Directa":
                    coleccion_ref = db.collection('products')
                    document_id = datos['id_prod']
                    documento = coleccion_ref.document(document_id).get()
                    datosimg = documento.to_dict()
                    ruta_imagen = "products/" + \
                        datos['id_prod']+"/"+datosimg['mainImg']
                    bucket = st.bucket()
                    imagen_ref = bucket.blob(ruta_imagen)
                    expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
                    url_imagen = imagen_ref.generate_signed_url(expiration=int(
                        expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                    response.append([documento.id, tipo,  datos['price'], datos['shippingFee'],
                                    datos['deliveryStatus'],  datos['shippingAddress'], url_imagen, datos['tran_date']])

    response = sorted(response, key=lambda x: datetime.datetime.strptime(
        x[7], '%d/%m/%Y').date())
    return response


def infoventas(user, action):
    nombre_coleccion = "products"
    coleccion_ref = db.collection(nombre_coleccion)
    documentos = coleccion_ref.get()
    # Itera sobre los documentos
    response = []
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
                url_imagen = imagen_ref.generate_signed_url(expiration=int(
                    expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                response.append([datos['prodName'], datos['categories'], datos['prodDesc'], datos['Brand'],
                                datos['Model'], condition, tipo, datos['Price'], datos['Stock'], datos['pubDate'], url_imagen])
            if action == 1:
                if tipo == "Subasta":
                    ruta_imagen = "products/"+documento.id+"/"+datos['mainImg']
                    bucket = st.bucket()
                    imagen_ref = bucket.blob(ruta_imagen)
                    expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
                    url_imagen = imagen_ref.generate_signed_url(expiration=int(
                        expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                    response.append([datos['prodName'], datos['categories'], datos['prodDesc'], datos['Brand'],
                                    datos['Model'], condition, tipo, datos['Price'], datos['Stock'], datos['pubDate'], url_imagen])

            if action == 2:
                if tipo == "Venta Directa":
                    ruta_imagen = "products/"+documento.id+"/"+datos['mainImg']
                    bucket = st.bucket()
                    imagen_ref = bucket.blob(ruta_imagen)
                    expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
                    url_imagen = imagen_ref.generate_signed_url(expiration=int(
                        expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                    response.append([datos['prodName'], datos['categories'], datos['prodDesc'], datos['Brand'],
                                    datos['Model'], condition, tipo, datos['Price'], datos['Stock'], datos['pubDate'], url_imagen])
    return response


def firestore_connection(col):
    try:
        app = firebase_admin.get_app()

    except ValueError as e:
        cred = credentials.Certificate(
            './pbay-733d6-firebase-adminsdk-r84zp-e324c11afb.json')
        # firebase_admin.initialize_app(cred, { 'databaseURL':'https://pbay-733d6-default-rtdb.firebaseio.com/'})
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    ref = db.collection(col)
    return ref
    # print(ref.get())


def storeOfficialID(uid, name):  # Saves user official ID to firebase storage
    # storage.child(path) sets the directory the file is going to be stored, must include filename with extension
    # .put() grabs the local file stored in media and uploads it to firebase
    storedID = storage.child('users/' + str(uid) +
                             '/' + name).put("media/" + name)
    return storedID


def payment_detail_by_month(uid, month, year):

    docs = db.collection('transactions').where('seller_id', '==', uid).get()

    def filter_by_month(doc):
        doc = doc.to_dict()
        _, mm, yy = doc['tran_date'].split('/')
        print(mm, '==', month, '|', yy, '==', year)
        return mm == month and yy == year

    payments = filter(filter_by_month, docs)

    result = []

    for doc in payments:
        payment = doc.to_dict()
        prod_doc = db.collection('products').document(payment['id_prod']).get()
        prod = prod_doc.to_dict()

        payment['id'] = doc.id
        payment['product'] = prod['prodName']
        payment['comission'] = payment['shippingFee']

        result.append(payment)

    return result

# Returns a list of all the sells made by the user


def sells_history(uid):
    docs = db.collection('transactions').where('seller_id', '==', uid).get()
    sells = []
    for doc in docs:
        sell = doc.to_dict()
        prod_doc = db.collection('products').document(sell['id_prod']).get()
        prod = prod_doc.to_dict()

        refUrl = storage.child(
            f"products/{sell['id_prod']}/{prod['mainImg']}").get_url(None)
        sell['id'] = doc.id
        sell['prod_name'] = prod['prodName']
        sell['prod_img'] = refUrl
        sells.append(sell)
    return sells

def searchCat(search):
    print(search)
    docs = db.collection('products').where('categories', '==', search).get()
    response = []
    for doc in docs:
        data = doc.to_dict()
        ruta_imagen = "products/"+doc.id+"/"+data['mainImg']
        bucket = st.bucket()
        imagen_ref = bucket.blob(ruta_imagen)
        expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
        url_imagen = imagen_ref.generate_signed_url(expiration=int(expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
        if data['saleType']:
            response.append([data['prodName'], "Subasta", url_imagen, doc.id])
        else:
            response.append([data['prodName'], '$' + str(data['Price']), url_imagen, doc.id])
    print(response)
    return(response)
            
        

def getdirection(user):
    docs = db.collection('users').where('oficial_id', '==', user["localId"]).get()
    for doc in docs:
        data = doc.to_dict()
        array = [data['maindirection']]
        for i in data['directions']:
            if i != data['maindirection']:
                array.append(i)
    return array

def switchMainDirection(direction, user):
    docs = db.collection('users').where('oficial_id', '==', user["localId"]).get()
    for doc in docs:
        id = doc.id
    documento_ref = db.collection('users').document(id)
    cambio = {'maindirection': direction}
    documento_ref.update(cambio)
    
def addDirect(user, direction):
    docs = db.collection('users').where('oficial_id', '==', user["localId"]).get()
    for doc in docs:
        id = doc.id
        data = doc.to_dict()
    documento_ref = db.collection('users').document(id)
    result = data['directions']
    result.append(direction)
    cambio = {'directions': result}
    documento_ref.update(cambio)  

# Obtener datos desde Firebase
def PayDetails(uid):
    datos = {}
    # Obtener todas las colecciones de la base de datos
    colecciones =  db.collection('transactions').where('seller_id', '==', uid).get()
    for coleccion in colecciones:
        # Obtener el año de la colección
        anio = coleccion.id
        datos[anio] = {
            'total_pagos': 0,
            'estatus': {}
        }

        # Obtener documentos de la colección
        documentos = coleccion.get()
        for documento in documentos:
            # Obtener el estado y el pago del documento
            estado = documento.get('deliveryStatus')
            pago = documento.get('price')

            # Actualizar el estado y el total de pagos
            if estado not in datos[anio]['estatus']:
                datos[anio]['estatus'][estado] = 1
            else:
                datos[anio]['estatus'][estado] += 1

            datos[anio]['total_pagos'] += pago

    return datos
