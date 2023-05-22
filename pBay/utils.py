# Importo Firebase Admin SDK 
import firebase_admin
 
# Hacemos uso de credenciales que nos permitirán usar Firebase Admin SDK 
from firebase_admin import credentials
 
# Importo el Servicio Firebase Realtime Database 
from firebase_admin import db

def fb_connection(data):
    try:
        app = firebase_admin.get_app()
        # Iniciamos los servicios de Firebase con las credenciales y el nombre de mi proyecto en Firebase 
    except ValueError as e:
        cred = credentials.Certificate('./pbay-733d6-firebase-adminsdk-r84zp-e324c11afb.json')
        firebase_admin.initialize_app(cred, { 'databaseURL':'https://pbay-733d6-default-rtdb.firebaseio.com/'})
		# Accedo a la base de datos, específicamente a la tabla 'postres' 
    ref = db.reference(data) 
    return ref
	#print(ref.get())