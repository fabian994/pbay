# Importo Firebase Admin SDK

import firebase_admin

# Hacemos uso de credenciales que nos permitirán usar Firebase Admin SDK
from firebase_admin import credentials

# Importo el Servicio Firebase Realtime Database
from firebase_admin import firestore
from firebase_admin import storage as st
import firebase
import datetime
import random
import datetime
from django.http import HttpResponse
from collections import Counter
from google.api_core.datetime_helpers import DatetimeWithNanoseconds 
from google.api_core.datetime_helpers import to_rfc3339

config = {
    "apiKey": "AIzaSyDMoLUyDxcIkcJZPeC_RoZelQ8AhxOSAvQ",
    "authDomain": "pbay-733d6.firebaseapp.com",
    "databaseURL": "https://pbay-733d6-default-rtdb.firebaseio.com",
    "projectId": "pbay-733d6",
    "storageBucket": "pbay-733d6.appspot.com",
    "messagingSenderId": "336573451844",
}

app  = firebase.initialize_app(config)
auth = app.auth()
database = app.database()
storage = app.storage()

cred = credentials.Certificate(
    './pbay-733d6-firebase-adminsdk-r84zp-e324c11afb.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'pbay-733d6.appspot.com'
})
db = firestore.client()


def LogIn_Firebase(Correo, Contra):
    try:
        user = auth.sign_in_with_email_and_password(Correo, Contra)
        userData = auth.get_account_info(user['idToken'])
        
        if userData['users'][0]['emailVerified'] == False:
            print('should send email')
            auth.send_email_verification(user['idToken'])
            print('email not verified',userData['users'][0]['emailVerified'])
        print('email verified',userData['users'][0]['emailVerified'])
        docs = db.collection('users').where(
            'oficial_id', '==', user['localId']).get()
        response = ""
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
        auth.send_email_verification(user['idToken'])
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
    documentos = db.collection(nombre_coleccion).where('buyerId', '==', user["localId"]).get()
    print( user["localId"])
    # Itera sobre los documentos
    response = []
    for documento in documentos:
        # Accede a los datos de cada documento
        datos = documento.to_dict()

        tipo = datos['saleType']
        
        if tipo=='True':
            tipo = "Subasta"
        else:
            tipo = "Venta Directa"
        
        if datos['buyerId'] == user["localId"]:
            if action == 0:
                # Hacer algo con los datos
                coleccion_ref = db.collection('products')
                document_id = datos['id_prod']
                documento2 = coleccion_ref.document(document_id).get()
                datosimg = documento2.to_dict()
                ruta_imagen = "products/" + \
                    documento2.id+"/"+datosimg['mainImg']
                bucket = st.bucket()
                imagen_ref = bucket.blob(ruta_imagen)
                expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
                url_imagen = imagen_ref.generate_signed_url(expiration=int(
                    expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                response.append([documento.id, tipo,  datos['price'], datos['shippingFee'],
                                datos['deliveryStatus'],  datos['shippingAddress'], url_imagen, datos['tran_date']])
                print(datos['tran_date'])
            if action == 1:
                if tipo == "Subasta":
                    coleccion_ref = db.collection('products')
                    document_id = datos['id_prod']
                    documento2 = coleccion_ref.document(document_id).get()
                    datosimg = documento2.to_dict()
                    ruta_imagen = "products/" + \
                        documento2.id+"/"+datosimg['mainImg']
                    bucket = st.bucket()
                    imagen_ref = bucket.blob(ruta_imagen)
                    expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
                    url_imagen = imagen_ref.generate_signed_url(expiration=int(
                        expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                    response.append([documento.id, tipo,  datos['price'], datos['shippingFee'],
                                    datos['deliveryStatus'],  datos['shippingAddress'], url_imagen, datos['tran_date']])
                    print(datos['tran_date'])
            if action == 2:
                if tipo == "Venta Directa":
                    coleccion_ref = db.collection('products')
                    document_id = datos['id_prod']
                    documento2 = coleccion_ref.document(document_id).get()
                    datosimg = documento2.to_dict()
                    ruta_imagen = "products/" + \
                        documento2.id +"/"+datosimg['mainImg']
                    bucket = st.bucket()
                    imagen_ref = bucket.blob(ruta_imagen)
                    expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
                    url_imagen = imagen_ref.generate_signed_url(expiration=int(
                        expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                    response.append([documento.id, tipo,  datos['price'], datos['shippingFee'],
                                    datos['deliveryStatus'],  datos['shippingAddress'], url_imagen, datos['tran_date']])
                    print(datos['tran_date'])
    response = sorted(response, key=lambda x: datetime.datetime.strptime(x[7], '%d/%m/%Y'))

    return response

def productFiltering(user, action):
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
        if datos['seller_id'] == user["localId"]:
            if action == 0:
                # Hacer algo con los datos
                coleccion_ref = db.collection('products')
                document_id = documento.id
                documento = coleccion_ref.document(document_id).get()
                datosimg = documento.to_dict()
                ruta_imagen = "products/" + \
                    documento.id + "/" + datosimg['mainImg']
                bucket = st.bucket()
                imagen_ref = bucket.blob(ruta_imagen)
                expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
                url_imagen = imagen_ref.generate_signed_url(expiration=int(
                    expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                response.append([documento.id, tipo, datos['prodName'],
                                datos['category'],  datos['pubDate'], url_imagen, datos['Price'], datos['Stock'], datos['saleType']])
            if action == 1:
                if tipo == "Subasta":
                    coleccion_ref = db.collection('products')
                    document_id = documento.id
                    documento = coleccion_ref.document(document_id).get()
                    datosimg = documento.to_dict()
                    ruta_imagen = "products/" + \
                    documento.id + "/" + datosimg['mainImg']
                    bucket = st.bucket()
                    imagen_ref = bucket.blob(ruta_imagen)
                    expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
                    url_imagen = imagen_ref.generate_signed_url(expiration=int(
                        expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                    response.append([documento.id, tipo, datos['prodName'],
                                datos['category'],  datos['pubDate'], url_imagen, datos['retireDate'], datos['Price'], datos['Stock'], datos['saleType']])
            if action == 2:
                if tipo == "Venta Directa":
                    coleccion_ref = db.collection('products')
                    document_id = documento.id
                    documento = coleccion_ref.document(document_id).get()
                    datosimg = documento.to_dict()
                    ruta_imagen = "products/" + \
                    documento.id + "/" + datosimg['mainImg']
                    bucket = st.bucket()
                    imagen_ref = bucket.blob(ruta_imagen)
                    expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
                    url_imagen = imagen_ref.generate_signed_url(expiration=int(
                        expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                    response.append([documento.id, tipo, datos['prodName'],
                                datos['category'],  datos['pubDate'], url_imagen, datos['retireDate'], datos['Price'], datos['Stock'], datos['saleType']])
    response = sorted(response, key=lambda x: DatetimeWithNanoseconds.rfc3339(x[4]))

    return response

def productList(user):
    collection = "products"
    collection_ref = db.collection(collection)
    members = collection_ref.get()
    #collection_id = db.collection(collection).select(field_paths = []).get()
    #data_id = collection_id.to_dict()
    #print(collection_id)
    ruta_imagen = "products/"
    response = []
    for ids, member in zip(''' collection_id ''', members):
        #print(ids.id)
        data = member.to_dict()
        try:
            if user == data['seller_id']:
                print(data)
                #print(collection_ref)
                ''' ruta_imagen = ruta_imagen + str(ids.id()) + "/" + data['prodImages']
                bucket = st.bucket()
                imagen_ref = bucket.blob(ruta_imagen)
                expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
                url_imagen = imagen_ref.generate_signed_url(expiration=int(
                    expiracion.timestamp()))
                data ["imageUrl"] = url_imagen '''
                response.append(data)
        except:
            print("Database is broken")
    return response

def deleteVenta(idDoc):
    db.collection('products').document(idDoc).delete()


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
                docId = documento.id
                bucket = st.bucket()
                imagen_ref = bucket.blob(ruta_imagen)
                expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
                url_imagen = imagen_ref.generate_signed_url(expiration=int(
                    expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                response.append([datos['prodName'], datos['category'], datos['prodDesc'], datos['Brand'],
                                datos['Model'], condition, tipo, datos['Price'], datos['Stock'], datos['pubDate'], url_imagen, docId])
            if action == 1:
                if tipo == "Subasta":
                    ruta_imagen = "products/"+documento.id+"/"+datos['mainImg']
                    docId = documento.id
                    bucket = st.bucket()
                    imagen_ref = bucket.blob(ruta_imagen)
                    expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
                    url_imagen = imagen_ref.generate_signed_url(expiration=int(
                        expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                    response.append([datos['prodName'], datos['category'], datos['prodDesc'], datos['Brand'],
                                    datos['Model'], condition, tipo, datos['Price'], datos['Stock'], datos['pubDate'], url_imagen, docId])

            if action == 2:
                if tipo == "Venta Directa":
                    ruta_imagen = "products/"+documento.id+"/"+datos['mainImg']
                    docId = documento.id
                    bucket = st.bucket()
                    imagen_ref = bucket.blob(ruta_imagen)
                    expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
                    url_imagen = imagen_ref.generate_signed_url(expiration=int(
                        expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                    response.append([datos['prodName'], datos['category'], datos['prodDesc'], datos['Brand'],
                                    datos['Model'], condition, tipo, datos['Price'], datos['Stock'], datos['pubDate'], url_imagen, docId])
    return response

'''
def infoProductos(id):
    documento=db.collection('products').document(id).get()
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
    response = []
    ruta_imagen = "products/"+documento.id+"/"+datos['mainImg']
    docId = documento.id
    bucket = st.bucket()
    imagen_ref = bucket.blob(ruta_imagen)
    expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
    url_imagen = imagen_ref.generate_signed_url(expiration=int(
    expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
    if tipo == "Venta Directa":
        response.append([datos['prodName'], datos['category'], datos['prodDesc'], datos['Brand'],
                        datos['Model'], condition, tipo, datos['Price'], datos['Stock'], datos['pubDate'], 
                        url_imagen, docId, datos['shippingFee']])
    if tipo == "Subasta":
        response.append([datos['prodName'], datos['category'], datos['prodDesc'], datos['Brand'],
                        datos['Model'], condition, tipo, datos['pubDate'], 
                        url_imagen, docId, datos['shippingFee'], datos['initialOffer'], datos['auctionDateEnd']])
    return response
'''

def infoProductos(id):
    documento = db.collection('products').document(id).get()
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
    
    response = []
    ruta_imagen = "products/" + documento.id + "/" + datos['mainImg']
    docId = documento.id
    bucket = st.bucket()
    imagen_ref = bucket.blob(ruta_imagen)
    expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
    url_imagen = imagen_ref.generate_signed_url(expiration=int(expiracion.timestamp()))

    ruta_imagen2 = "products/" + documento.id + "/"
    url_imagen2 = []
    for image in datos['images']:
        imagen_ref2 = bucket.blob(ruta_imagen2 + image)
        expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
        url_imagen2.append(imagen_ref2.generate_signed_url(expiration=int(expiracion.timestamp())))

    if tipo == "Venta Directa":
        response.append([
            datos['prodName'], datos['category'], datos['prodDesc'], datos['Brand'],
            datos['Model'], condition, tipo, datos['Price'], datos['Stock'], datos['pubDate'],
            url_imagen, docId, datos['shippingFee'], url_imagen2
        ])
    if tipo == "Subasta":
        response.append([
            datos['prodName'], datos['category'], datos['prodDesc'], datos['Brand'],
            datos['Model'], condition, tipo, datos['pubDate'],
            url_imagen, docId, datos['shippingFee'], datos['initialOffer'], datos['auctionDateEnd']
        ])

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


def storeProductImages(uid, name):  # Saves user official ID to firebase storage
    # storage.child(path) sets the directory the file is going to be stored, must include filename with extension
    # .put() grabs the local file stored in media and uploads it to firebase
    storedID = storage.child('products/' + str(uid) +
                             '/' + name).put("media/" + name)
    return storedID


def payment_detail_by_month(uid, month, year):

    docs = db.collection('transactions').where('seller_id', '==', uid).get()

    def filter_by_month(doc):
        doc = doc.to_dict()
        _, mm, yy = doc['tran_date'].split('/')
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
        sell['tipo'] = prod['saleType']
        sell['cancelled'] = prod.get('AuctionCancelled')
        sells.append(sell)
    return sells

def cancel_auction(id_prod):
    reslut = db.collection('products').document(id_prod).update({
        'AuctionCancelled': True
    })


def searchCat(category,subcategory,subcategory2):
    docs = db.collection('products').where('category', '==', category).where('subCategory1', '==', subcategory).where('SubCategory2', '==', subcategory2).get()
    response = []
    for doc in docs:
        data = doc.to_dict()
        print(data)
        ruta_imagen = "products/"+doc.id+"/"+data['mainImg']
        bucket = st.bucket()
        imagen_ref = bucket.blob(ruta_imagen)
        expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
        url_imagen = imagen_ref.generate_signed_url(expiration=int(
            expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
        if data['saleType']:
            response.append([data['prodName'], "Subasta", url_imagen, doc.id, data['PromoStatus']])
        else:
            response.append(
                [data['prodName'], '$' + str(data['Price']), url_imagen, doc.id, data['PromoStatus']])
    sorted_data = sorted(response, key=lambda x: x[4] is True, reverse=True)
    return (sorted_data)


def searchList(document, user):
    doc = db.collection('wishList').document(user["localId"]).get()
    data = doc.to_dict()
    array = []
    for i in data[document]:
        array.append(i)
    response = []
    for i in array:
        docitem = db.collection('products').document(i).get()
        dataitem = docitem.to_dict()
        ruta_imagen = "products/"+docitem.id+"/"+dataitem['mainImg']
        bucket = st.bucket()
        imagen_ref = bucket.blob(ruta_imagen)
        expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
        url_imagen = imagen_ref.generate_signed_url(expiration=int(
            expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
        if dataitem['saleType']:
            response.append(
                [dataitem['prodName'], "Subasta", url_imagen, docitem.id])
        else:
            response.append([dataitem['prodName'], '$' +
                            str(dataitem['Price']), url_imagen, docitem.id])
    return (response)


def search(keyword):
    collection_ref = firestore.client().collection('products')
    #query = collection_ref.where('prodName', '>=', keyword).where('prodName', '<', keyword + u'\uf8ff')
    #docs = query.stream()
    docs = db.collection('products').get()
    array=[]
    for doc in docs:
        data = doc.to_dict()
        if keyword.upper() in data['prodName'].upper():
            array.append(doc.id)
    response = []
    for i in array:
        doc = db.collection('products').document(i).get()
        data = doc.to_dict()
        ruta_imagen = "products/"+doc.id+"/"+data['mainImg']
        bucket = st.bucket()
        imagen_ref = bucket.blob(ruta_imagen)
        expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
        url_imagen = imagen_ref.generate_signed_url(expiration=int(
            expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
        if bool(data['saleType']):
            response.append([data['prodName'], "Subasta", url_imagen, doc.id, data['PromoStatus']])
        else:
            response.append(
                [data['prodName'], '$' + str(data['Price']), url_imagen, doc.id, data['PromoStatus']])
    sorted_data = sorted(response, key=lambda x: x[4] is True, reverse=True)
    return (sorted_data)

def getdirection(user):
    docs = db.collection('users').where(
        'oficial_id', '==', user["localId"]).get()
    for doc in docs:
        data = doc.to_dict()
        array = [data['maindirection']]
        for i in data['directions']:
            if i != data['maindirection']:
                array.append(i)
    return array


def getWish(user):
    doc = db.collection('wishList').document(user["localId"]).get()
    data = doc.to_dict()
    array = []
    for i in data.keys():
        array.append(i)
    return array


def switchMainDirection(direction, user):
    docs = db.collection('users').where(
        'oficial_id', '==', user["localId"]).get()
    for doc in docs:
        id = doc.id
    documento_ref = db.collection('users').document(id)
    cambio = {'maindirection': direction}
    documento_ref.update(cambio)


def addDirect(user, direction):
    docs = db.collection('users').where(
        'oficial_id', '==', user["localId"]).get()
    for doc in docs:
        id = doc.id
        data = doc.to_dict()
    documento_ref = db.collection('users').document(id)
    result = data['directions']
    result.append(direction)
    cambio = {'directions': result}
    documento_ref.update(cambio)


def addLista(user, direction):
    documento_ref = db.collection('wishList').document(user["localId"])
    documento_ref.update({
        direction: []
    })

# Obtener datos desde Firebase


def PayDetails(uid):
    datos = {}
    # Obtener todas las colecciones de la base de datos
    colecciones = db.collection('transactions').where(
        'seller_id', '==', uid).get()
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

def addCart(product, user):
    try:
        documento_ref = db.collection('cart').document(user["localId"]).get()
        data = documento_ref.to_dict()
        newData = data['items']
        occurrences = {}
        for item in newData:
            if item in occurrences:
                occurrences[item] += 1
            else:
                occurrences[item] = 1
        if occurrences.get(product) == None:
            quantity = 0
        else:
            quantity = occurrences[product]

        document2 = db.collection('products').document(product).get()
        dataproduct = document2.to_dict()
        stock = dataproduct['Stock']
        print(stock)
        print(quantity)
        if int(quantity) < int(stock):
            newData.append(product)
            cambio = {'items': newData}
            documento_ref = db.collection('cart').document(user["localId"])
            documento_ref.update(cambio)
            return True
        return False
    except:
        document2 = db.collection('products').document(product).get()
        dataproduct = document2.to_dict()
        stock = dataproduct['Stock']
        quantity = 1
        print(stock)
        print(quantity)
        if int(quantity) < int(stock):
            ref = firestore_connection('cart')
            uData = {'items': [product]}
            ref.document(user["localId"]).set(uData)
    return HttpResponse(status=200)
            
def getRecomendations():
    docs = db.collection('products').where('PromoStatus', '==', "true").get()
    docs = docs + db.collection('products').where('PromoStatus', '==', True).get()
    try:
        doc_list = [doc for doc in docs]
        random_docs = random.sample(doc_list, 10)
    except: 
        random_docs = docs
    response =[]
    for doc in random_docs:
        data = doc.to_dict()
        ruta_imagen = "products/"+doc.id+"/"+data['mainImg']
        bucket = st.bucket()
        imagen_ref = bucket.blob(ruta_imagen)
        expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
        url_imagen = imagen_ref.generate_signed_url(expiration=int(
            expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
        response.append([data['prodName'], url_imagen, doc.id, str(data['saleType'])])
    return(response)

def getCart(user):
    snapshot = db.collection('cart').document(user["localId"]).get()
    print(snapshot)
    response = []
    subtotal = 0
    shipping_fee = 0
    ocurrences = []
    temp = 1

    if snapshot.exists:
        data_snapshot = snapshot.to_dict()
        products = data_snapshot.get('items')
        print('PRINT PRODUCTS')
        print(products)

        if products:

            counts = dict(Counter(products))
            duplicates = {key:value for key, value in counts.items() if value > 0}

            print(duplicates)

            for item in duplicates:

                # Count how many times theres the same item in the shopping cart
                #if i =
                documento = db.collection('products').document(item).get()
                datos = documento.to_dict()
                #print(datos)

                print('ENTRA')
                
                ruta_imagen = "products/"+item+"/"+datos['mainImg']
                docId = item
                bucket = st.bucket()
                imagen_ref = bucket.blob(ruta_imagen)
                expiracion = datetime.datetime.now() + datetime.timedelta(minutes=5)
                url_imagen = imagen_ref.generate_signed_url(expiration=int(
                expiracion.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                # Enviar prodDesc
                response.append([datos['prodName'], datos['Price'] * duplicates[item], duplicates[item], url_imagen, docId, datos['shippingFee']])
                print(response)
            
            
            for item in response:
                print('Entra items loop')
                print(item[1])
                # item[1] es precio
                # item[2] es cantidad
                # item[5] es costo de envio
                subtotal += item[1]
                shipping_fee += item[5]

            total = subtotal + shipping_fee
            print(total)
            prices = [subtotal, shipping_fee, total]

            print('entra final')
            print(response)
            print(prices)

            return response, prices
        
        else:
            return 0, 0

def addWish(product, user, array_name):
    documento_ref = db.collection('wishList').document(user["localId"]).get()
    data = documento_ref.to_dict()
    addC = data.get(array_name, [])  
    addC.append(product)
    data[array_name] = addC
    db.collection('wishList').document(user["localId"]).set(data)
    return True

def delete_item(user, product_id):
    print('ENTRA DELETE ITEM')
    snapshot = db.collection('cart').document(user["localId"]).get()
    data_snapshot = snapshot.to_dict()
    my_list = list(data_snapshot.values())
    items = list(my_list[0])
    print(items)
   # items.remove(product_id)
    items = [i for i in items if i != product_id]
    db.collection('cart').document(user["localId"]).update({"items": list(items)})
    print(items)
    
def increase_item(user, product_id, amount):
    snapshot = db.collection('cart').document(user["localId"]).get()
    data_snapshot = snapshot.to_dict()
    my_list = list(data_snapshot.values())
    items = list(my_list[0])
    items.append(product_id)
    db.collection('cart').document(user["localId"]).update({"items": list(items)})

def decrease_item(user, product_id, amount):
    snapshot = db.collection('cart').document(user["localId"]).get()
    data_snapshot = snapshot.to_dict()
    my_list = list(data_snapshot.values())
    items = list(my_list[0])
    items.remove(product_id)
    db.collection('cart').document(user["localId"]).update({"items": list(items)})


def process_transaction(user, prices):
    snapshot = db.collection('cart').document(user["localId"]).get()
    data_snapshot = snapshot.to_dict()
    my_list = list(data_snapshot.values())
    items = list(my_list[0])

    if snapshot.exists:
        data_snapshot = snapshot.to_dict()
        products = data_snapshot.get('items')
        print(products)
        # transactionID, product(s) name, product(s) price, product(s) quantity, seller id, date, time, total price, total shipping fee, 
            # total_tax, shipping_address, deliveryStatus

        if products:
            
            counts = dict(Counter(products))
            duplicates = {key:value for key, value in counts.items() if value > 0}

            print('Entra loop de transaccion')
            for item in duplicates:
                print('item:', item)
                transaction = {}
                transaction = {'buyerId' : user["localId"]}
                documento = db.collection('products').document(item).get()
                #product = 'id_product' + str(temp)
                product = 'id_prod'
                datos = documento.to_dict()
                currenttime = datetime.datetime.now().strftime("%d/%m/%Y")
                transaction.update({product: item,
                                    'price': str(datos['Price']),
                                    'quantity': str(duplicates[item]),
                                    'saleType': str(datos['saleType']),
                                    'seller_id': str(datos['seller_id']),
                                    'shippingAddress': 'Mi casa', #editar en un momento
                                    'shippingFee': str(datos['shippingFee'] * duplicates[item]),
                                    'tran_date': str(currenttime),
                                    'deliveryStatus' : 'En espera de envio'
                                    })
                print('PRINT TRANSACTION!!!!!!!!')
                print(transaction)
                db.collection('transactions').add(transaction)

def boolValidator(val):
    if val == 'false':
        val = False
    else:
        val = True
    return val