import datetime
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
import datetime
import base64
import json
import os


firebase_config_base64 = os.environ.get('firebase64')
json_data = base64.b64decode(firebase_config_base64).decode('utf-8')
firebase_config = json.loads(json_data)

config = firebase_config


cred = credentials.Certificate(config)
try:
    firebase_admin.initialize_app(cred)
except:
    pass
db = firestore.client()


def gastado():

    today = datetime.datetime.today()
    firstday = datetime.datetime(today.year, today.month, 1)

    docs = db.collection('movimientos').where('fecha', '>=', firstday).stream()
    egresos_por_subcategoria = {}
    for i in docs:
        if i.to_dict()['tipo'] == 'Egreso':
            if i.to_dict()['subcategoria'] in egresos_por_subcategoria:
                egresos_por_subcategoria[i.to_dict()['subcategoria']] += i.to_dict()['monto']
            else:
                egresos_por_subcategoria[i.to_dict()['subcategoria']] = i.to_dict()[
                    'monto']

    docs = db.collection('subcategoriasEgresos').stream()

    for doc in docs:
        if doc.to_dict()['subcategoria'] not in egresos_por_subcategoria:
            doc_ref = db.collection('subcategoriasEgresos').document(doc.id)
            doc_ref.set({'gastado': 0}, merge=True)

    for k, v in egresos_por_subcategoria.items():
        for doc in db.collection('subcategoriasEgresos').stream():
            if doc.to_dict()['subcategoria'] == k:
                doc_ref = db.collection('subcategoriasEgresos').document(doc.id)
                doc_ref.set({'gastado': v}, merge=True)

    return egresos_por_subcategoria
