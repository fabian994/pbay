# Import Firebase Admin SDK
import firebase_admin

# We import credentials to use Firebase Admin SDK
from firebase_admin import credentials

# Import the service Firebase Realtime Database
from firebase_admin import firestore
from firebase_admin import storage as st

#Import general librarys 
from collections import Counter
import firebase
import datetime
import random
import datetime

# Import library to comunicate whith frontend
from django.http import HttpResponse

# Import librarys to manipulate times
from google.api_core.datetime_helpers import DatetimeWithNanoseconds 
from google.api_core.datetime_helpers import to_rfc3339

# This configuration was used by the previous firebase project
    # "apiKey": "AIzaSyDMoLUyDxcIkcJZPeC_RoZelQ8AhxOSAvQ",
    # "authDomain": "pbay-733d6.firebaseapp.com",
    # "databaseURL": "https://pbay-733d6-default-rtdb.firebaseio.com",
    # "projectId": "pbay-733d6",
    # "storageBucket": "pbay-733d6.appspot.com",
    # "messagingSenderId": "336573451844",

# This configuration was used by this firebase project
config = {
    'apiKey': "AIzaSyAPSKodevh0CayLgqpEUy7wr6aX75BpDtU",
    'authDomain': "pbaypobreza.firebaseapp.com",
    "databaseURL": "https://pbaypobreza-default-rtdb.firebaseio.com/",
    'projectId': "pbaypobreza",
    'storageBucket': "pbaypobreza.appspot.com",
    'messagingSenderId': "508813203469",
    'appId': "1:508813203469:web:0d5249365ea8a8fd441d44",
    'measurementId': "G-PG3RNDVQZV"
}

#We initialize the app and everything tooll that we need 
app  = firebase.initialize_app(config)
auth = app.auth()
database = app.database()
storage = app.storage()
# The comentaries was from the previus project
cred = credentials.Certificate(
     './pbaypobreza-firebase-adminsdk-h1iis-fa6c4dc7fd.json')
    #'./pbay-733d6-firebase-adminsdk-r84zp-e324c11afb.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'pbaypobreza.appspot.com'
    #'storageBucket': 'pbay-733d6.appspot.com'
})
db = firestore.client()

# We connect the firestore with the project
def firestore_connection(col):
    try:
        app = firebase_admin.get_app()

    except ValueError as e:
        cred = credentials.Certificate(
            './pbaypobreza-firebase-adminsdk-h1iis-fa6c4dc7fd.json')
            #'./pbay-733d6-firebase-adminsdk-r84zp-e324c11afb.json')
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    ref = db.collection(col)
    return ref


# This function has the propuse to login in the page
def LogIn_Firebase(email, password):
    # We try to sign in with email and verification the verification email
    try:
        user = auth.sign_in_with_email_and_password(email, password)
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
            return 'NoAuthorized'
    except:
    # If any problem appears we print error
        print("Error")
    return False


# This function has the propuse to signup in the page
def signUp_Firebase(email, password):
    # We try to create a acount with email and send verification to the email
    try:
        user = auth.create_user_with_email_and_password(email, password)
        auth.send_email_verification(user['idToken'])
        return (user)
    # If any problem appears we print error and return false
    except:
        print("Error")
    return False


# This function has the propuse to get user information to desplegate in the page
def infoUser(user):
    # We consulte the database where the id match with the user
    doc = db.collection('users').document(user).get()
    data = doc.to_dict()
    response = [data['name']+" "+data['lastNames'],data['mail'], data['phoneNumber'], data['birthDate']]
    return (response)


# This function has the propuse to get the transactions where the user is the buyer to desplegate in the page
def infoProductoUser(user, action):
    documents = db.collection("transactions").where('buyerId', '==', user["localId"]).get()
    # We iterate each document to get information
    response = []
    for document in documents:
        # We get the document's data
        data = document.to_dict()
        typeSale = data['saleType']
        # Evalute the type sale 
        if typeSale=="True":
            typeSale = "Subasta"
        else:
            typeSale = "Venta Directa"
            
        # We search and take the product image and append the data to the response
        colectionRef = db.collection('products')
        document_id = data['id_prod']
        document2 = colectionRef.document(document_id).get()
        dataImg = document2.to_dict()
        imagePath = "products/" + \
            document2.id+"/"+dataImg['mainImg']
        bucket = st.bucket()
        imageRef = bucket.blob(imagePath)
        expiration = datetime.datetime.now() + datetime.timedelta(minutes=5)
        urlImage = imageRef.generate_signed_url(expiration=int(
            expiration.timestamp()))  
                
        # If no there a filter we append every document to the response
        if action == 0:
            response.append([document.id, typeSale,  data['price'], data['shippingFee'],
                            data['deliveryStatus'],  data['shippingAddress'], urlImage, data['tran_date']])
        # If the filter  is "Subasta" we append every document that are "Subasta" to the response
        if action == 1:
            if typeSale == "Subasta":
                response.append([document.id, typeSale,  data['price'], data['shippingFee'],
                                data['deliveryStatus'],  data['shippingAddress'], urlImage, data['tran_date']])
        # If the filter  is "Venta Directa" we append every document that are "Venta Directa" to the response
        if action == 2:
            # We search and take the product image and append the data to the response
            if typeSale == "Venta Directa":
                response.append([document.id, typeSale,  data['price'], data['shippingFee'],
                                data['deliveryStatus'],  data['shippingAddress'], urlImage, data['tran_date']])
    #We sort by the date
    response = sorted(response, key=lambda x: datetime.datetime.strptime(x[7], '%d/%m/%Y').date())
    return response


# This function has the propuse to get the transactions where the user is the seller to desplegate in the page
def productFiltering(user, action):
    documents = db.collection("products").where('seller_id', '==', user["localId"]).get()
    # We iterate each document to get information
    response = []
    for document in documents:
         # We get the document's data
        data = document.to_dict()
        # Evalute if the product was deleted
        if data.get('Delete') != None:
            continue
        # Evalute the type sale 
        typeSale = data['saleType']
        if typeSale == "True":
            typeSale = "Subasta"
        else:
            typeSale = "Venta Directa"

        # Evalute the condition 
        condition = data['Condition']
        if condition=="True":
            condition = "Nuevo"
        else:
            condition = "Usado"
            
        # We search and take the product image and append the data to the response    
        imagePath = "products/"+document.id+"/"+data['mainImg']
        docId = document.id
        bucket = st.bucket()
        imageRef = bucket.blob(imagePath)
        expiration = datetime.datetime.now() + datetime.timedelta(minutes=5)
        urlImage = imageRef.generate_signed_url(expiration=int(
        expiration.timestamp()))      
        # If no there a filter we append every document to the response    
        if action == 0:
            # We evaluate in what way we return the results according its saleType
            if data['saleType']==True:
                response.append([data['pubDate'], urlImage, docId, data['prodName'], data['category'], data['prodDesc'], data['Brand'],   
                                data['Model'], condition, typeSale, data['initialOffer'], data['minimumOffer'], data['auctionDateEnd'],data['shippingFee']])
            else: 
                response.append([data['pubDate'],urlImage, docId, typeSale, data['prodName'],
                            data['category'], data['retireDate'], data['Price'], data['Stock'], data['saleType']])
        # If the filter  is "Subasta" we append every document that are "Subasta" to the response
        if action == 1:
            if typeSale == "Subasta":
                response.append([data['pubDate'], urlImage, docId, data['prodName'], data['category'], data['prodDesc'], data['Brand'],   
                data['Model'], condition, typeSale, data['initialOffer'], data['minimumOffer'], data['auctionDateEnd'],data['shippingFee']])
         # If the filter  is "Venta Directa" we append every document that are "Venta Directa" to the response
        if action == 2:
            if typeSale == "Venta Directa":
                # We search and take the product image and append the data to the response
                response.append([data['pubDate'],urlImage, docId, typeSale, data['prodName'],
                data['category'], data['retireDate'], data['Price'], data['Stock'], data['saleType']])
     #We sort by the date
    response = sorted(response, key=lambda x: DatetimeWithNanoseconds.rfc3339(x[0]))

    return response


# This function activate the status delete and deactivate the promoStatus and push to the database
def deleteVenta(idDoc):
    result = db.collection('products').document(idDoc).update({
        'Delete': True,
        'promoStatus': False
    })



def infoventas(user, id):
    # We get a document with document
    document = db.collection("products").document(id).get()
    response = []
    
    #  We get the data document
    data = document.to_dict()
    
    #We evaluate the saletype
    typeSale = data['saleType']
    print(typeSale)
    if typeSale == True:
        typeSale = "Subasta"
    else:
        typeSale = "Venta Directa"
        
    #We evaluate the condition
    condition = data['Condition']
    if condition == True:
        condition = "Nuevo"
    else:
        condition = "Usado"
    
    # We search and take the product image and append the data to the response       
    imagePath = "products/"+document.id+"/"+data['mainImg']
    docId = document.id
    bucket = st.bucket()
    imageRef = bucket.blob(imagePath)
    expiration = datetime.datetime.now() + datetime.timedelta(minutes=5)
    urlImage = imageRef.generate_signed_url(expiration=int(
    expiration.timestamp()))  # Caducidad de 5 minutos (300 segundos)
    
    # We evaluate in what way we return the results according its saleType
    if data['saleType']==True:
        response.append([data['prodName'], data['category'], data['prodDesc'], data['Brand'],   
                        data['Model'], condition, typeSale, data['initialOffer'], data['minimumOffer'], data['pubDate'],data['auctionDateEnd'],data['shippingFee'], urlImage, docId])
    else: 
        response.append([data['prodName'], data['category'], data['prodDesc'], data['Brand'],   
                        data['Model'], condition, typeSale, data['Price'], data['Stock'], data['pubDate'], urlImage, docId])
    return response


def infoProductos(id):
    # We get a document with document
    document = db.collection('products').document(id).get()
    
    #  We get the data document
    data = document.to_dict()
    
    #We evaluate the saletype
    typeSale = data['saleType']
    if typeSale == True:
        typeSale = "Subasta"
    else:
        typeSale = "Venta Directa"

    #We evaluate the condition
    condition = data['Condition']
    if condition == True:
        condition = "Nuevo"
    else:
        condition = "Usado"
    
    response = []
    
    # We search and take the product image and append the data to the response
    imagePath = "products/" + document.id + "/" + data['mainImg']
    docId = document.id
    bucket = st.bucket()
    imageRef = bucket.blob(imagePath)
    expiration = datetime.datetime.now() + datetime.timedelta(minutes=5)
    urlImage = imageRef.generate_signed_url(expiration=int(expiration.timestamp()))
    
    # We search and take the product images and append into the array  to the response
    imagePath2 = "products/" + document.id + "/"
    urlImage2 = []
    for image in data['images']:
        imageRef2 = bucket.blob(imagePath2 + image)
        expiration = datetime.datetime.now() + datetime.timedelta(minutes=5)
        urlImage2.append(imageRef2.generate_signed_url(expiration=int(expiration.timestamp())))
        
    # We evaluate in what way we return the results according its saleType
    if typeSale == "Venta Directa":
        response.append([
            data['prodName'], data['category'], data['prodDesc'], data['Brand'],
            data['Model'], condition, typeSale, data['Price'], data['Stock'], data['pubDate'],
            urlImage, docId, data['shippingFee'], urlImage2
        ])
    if typeSale == "Subasta":
        response.append([
            data['prodName'], data['category'], data['prodDesc'], data['Brand'],
            data['Model'], condition, typeSale, data['pubDate'],
            urlImage, docId, data['shippingFee'], data['initialOffer'], data['auctionDateEnd'], urlImage2
        ])

    return response


# Saves user official ID to firebase storage
def storeOfficialID(uid, name):  
    storedID = storage.child('users/' + str(uid) +
                             '/' + name).put("media/" + name)
    return storedID

# Saves user official ID to firebase storage
def storeProductImages(uid, name):  
    storedID = storage.child('products/' + str(uid) +
                             '/' + name).put("media/" + name)
    return storedID

# Returns a list of all the sells made by the user
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
        payment['comission'] = float(payment['price'])*.02

        result.append(payment)

    return result




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
        if data.get('Delete') != None:
            continue
        print(data)
        imagePath = "products/"+doc.id+"/"+data['mainImg']
        bucket = st.bucket()
        imageRef = bucket.blob(imagePath)
        expiration = datetime.datetime.now() + datetime.timedelta(minutes=5)
        urlImage = imageRef.generate_signed_url(expiration=int(
            expiration.timestamp()))  # Caducidad de 5 minutos (300 segundos)
        if data['saleType']:
            response.append([data['prodName'], "Subasta", urlImage, doc.id, data['PromoStatus']])
        else:
            response.append(
                [data['prodName'], '$' + str(data['Price']), urlImage, doc.id, data['PromoStatus']])
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
        if dataitem.get('Delete') != None:
            continue
        imagePath = "products/"+docitem.id+"/"+dataitem['mainImg']
        bucket = st.bucket()
        imageRef = bucket.blob(imagePath)
        expiration = datetime.datetime.now() + datetime.timedelta(minutes=5)
        urlImage = imageRef.generate_signed_url(expiration=int(
            expiration.timestamp()))  # Caducidad de 5 minutos (300 segundos)
        if dataitem['saleType']:
            response.append(
                [dataitem['prodName'], "Subasta", urlImage, docitem.id])
        else:
            response.append([dataitem['prodName'], '$' +
                            str(dataitem['Price']), urlImage, docitem.id])
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
        if data.get('Delete') != None:
            continue
        imagePath = "products/"+doc.id+"/"+data['mainImg']
        bucket = st.bucket()
        imageRef = bucket.blob(imagePath)
        expiration = datetime.datetime.now() + datetime.timedelta(minutes=5)
        urlImage = imageRef.generate_signed_url(expiration=int(
            expiration.timestamp()))  # Caducidad de 5 minutos (300 segundos)
        if bool(data['saleType']):
            response.append([data['prodName'], "Subasta", urlImage, doc.id, data['PromoStatus']])
        else:
            response.append(
                [data['prodName'], '$' + str(data['Price']), urlImage, doc.id, data['PromoStatus']])
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
    try:
        for i in data.keys():
            array.append(i)
    except:
        pass
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
    try:
        documento_ref = db.collection('wishList').document(user["localId"])
        documento_ref.update({
            direction: []
        })
    except:
        documento_ref = db.collection('wishList').document(user["localId"])
        documento_ref.set({
            direction: []
        })
# Obtener datos desde Firebase


def PayDetails(uid):
    # Obtener todas las colecciones de la base de datos
    days = {1:"Enero", 2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",7:"Julio",8:"agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre",}
    colecciones = db.collection('transactions').where(
        'seller_id', '==', uid).get()
    dictionary={}
    years = []
    for coleccion in colecciones:
        data = coleccion.to_dict()
        date = data['tran_date']
        fecha = datetime.datetime.strptime(date, '%d/%m/%Y')
        years.append(fecha.year)
        if dictionary.get(fecha.year)==None:
            dictionary[fecha.year]={1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0}
            dictionary[fecha.year][fecha.month]= float(data['price'])*.98
        else:
            dictionary[fecha.year][fecha.month]= dictionary[fecha.year][fecha.month]+ float(data['price'])*.98
    setyears =  list(set(years))
    years = sorted(setyears, reverse=True)
    array=[]
    for i in years:
        for j in range(12, 0, -1):
            if dictionary[i][j] != 0 :
                subarray=[i,days[j],dictionary[i][j]]
                if j < 10:
                    subarray.append("0"+str(j))
                else:
                    subarray.append(str(j))
                array.append(subarray)
    print(datetime.datetime.now().month)
    actual_month =datetime.datetime.now().month
    return array , days[actual_month]

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
        random_docs = random.sample(doc_list, 30)
    except: 
        random_docs = docs
    response =[]
    for doc in random_docs:
        data = doc.to_dict()
        if data.get('Delete') != None or data.get('listStatus') == False:
            continue
        imagePath = "products/"+doc.id+"/"+data['mainImg']
        bucket = st.bucket()
        imageRef = bucket.blob(imagePath)
        expiration = datetime.datetime.now() + datetime.timedelta(minutes=5)
        urlImage = imageRef.generate_signed_url(expiration=int(
            expiration.timestamp()))  # Caducidad de 5 minutos (300 segundos)
        response.append([data['prodName'], urlImage, doc.id, str(data['saleType'])])
    
    docs = db.collection('transactions').get() 
    products_array = []
    for doc in docs:
        data = doc.to_dict()
        products_array.append(data['id_prod']) 
    frequencies = Counter(products_array)
    sorted_items = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
    result = [item for item, _ in sorted_items]
    try:
        result = result[0:10]
    except:
        pass
    print(result)
    for i in result:
        doc = db.collection('products').document(i).get()
        data = doc.to_dict()
        if data.get('Delete') != None:   
            continue
        imagePath = "products/"+doc.id+"/"+data['mainImg']
        bucket = st.bucket()
        imageRef = bucket.blob(imagePath)
        expiration = datetime.datetime.now() + datetime.timedelta(minutes=5)
        urlImage = imageRef.generate_signed_url(expiration=int(
            expiration.timestamp()))  # Caducidad de 5 minutos (300 segundos)
        response.append([data['prodName'], urlImage, doc.id, str(data['saleType'])])
    
    
    return(response)

def getCart(user):
    snapshot = db.collection('cart').document(user["localId"]).get()
    print(snapshot)
    response = []
    subtotal = 0
    shipping_fee = 0

    if snapshot.exists:
        print('*********ENTRA SNAPSHOT')
        data_snapshot = snapshot.to_dict()
        products = data_snapshot.get('items')
        print('PRINT PRODUCTS')
        print(products)

        if products:
            print('*********ENTRA PRODUCTOS')

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
                
                imagePath = "products/"+item+"/"+datos['mainImg']
                docId = item
                bucket = st.bucket()
                imageRef = bucket.blob(imagePath)
                expiration = datetime.datetime.now() + datetime.timedelta(minutes=5)
                urlImage = imageRef.generate_signed_url(expiration=int(
                expiration.timestamp()))  # Caducidad de 5 minutos (300 segundos)
                # Enviar prodDesc
                response.append([datos['prodName'], datos['Price'] * duplicates[item], duplicates[item], urlImage, docId, datos['shippingFee']])
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

            documento = db.collection('users').document(user["localId"]).get()
            datos = documento.to_dict()
            my_list = list(datos.values())

            return response, prices
        
        else:
            print('NO HAY ELEMENTOS')
            return 0, 0
        
    else:
        print('NO HAY ELEMENTOS')
        return 0, 0


def addWish(product, user, array_name):
    documento_ref = db.collection('wishList').document(user["localId"]).get()
    data = documento_ref.to_dict()
    addC = data.get(array_name, [])  
    addC.append(product)
    data[array_name] = addC
    db.collection('wishList').document(user["localId"]).set(data)
    return True

def getArrayNames(user):
    documento_ref = db.collection('wishList').document(user["localId"]).get()
    data = documento_ref.to_dict()
    return list(data.keys()) if data else []

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

        addressdoc = db.collection('users').document(user["localId"]).get()
        data = addressdoc.to_dict()
        main_address = data['maindirection']

        if products: # Valida que existan productos en carrito
            
            counts = dict(Counter(products))
            duplicates = {key:value for key, value in counts.items() if value > 0} # Identificar elementos duplicados

            print('Entra loop de transaccion')
            for item in duplicates: # Iterar cada producto junto con la cantidad adquirida de cada uno -> prodid : 4, prodid : 1
                print('item:', item)

                productdoc = db.collection('products').document(item).get()
                productdata = productdoc.to_dict()

                new_stock = int(productdata['Stock']) - int(duplicates[item]) # Calcula el nuevo inventario

                transaction = {}
                transaction = {'buyerId' : user["localId"]}
                documento = db.collection('products').document(item).get()
                product = 'id_prod'
                datos = documento.to_dict()

                currenttime = datetime.datetime.now().strftime("%d/%m/%Y")
                transaction.update({product: item,                           # Generar transaccion
                                    'price': str(datos['Price']* duplicates[item]),
                                    'quantity': str(duplicates[item]),
                                    'saleType': str(datos['saleType']),
                                    'seller_id': str(datos['seller_id']),
                                    'shippingAddress': str(data['maindirection']), 
                                    'shippingFee': str(datos['shippingFee'] * duplicates[item]),
                                    'tran_date': str(currenttime),
                                    'deliveryStatus' : 'En espera de envio'
                                    })
                print(transaction)
                db.collection('transactions').add(transaction) # Agregar transaccion en base de datos
                db.collection('products').document(item).update({'Stock': int(new_stock)}) # Actualizar inventario
                db.collection('cart').document(user["localId"]).delete() # Limpiar el carrito


def getimage(p_id,imagename):
    imageroute = 'products/'+ p_id +'/'+imagename
    bucket = st.bucket()
    imgref = bucket.blob(imageroute)
    expiration = datetime.datetime.now()+datetime.timedelta(minutes = 5)
    image_url = imgref.generate_signed_url(expiration =int(expiration.timestamp()))
    return image_url  


    
