from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import Query
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

app = FastAPI()

class Msg(BaseModel):
    msg: str


@app.get("/")
async def root():
    return "FastAPI MoneyApp"


@app.get("/home")
async def home():
    movimientos = []
    docs = db.collection(u'movimientos').stream()

    for i in docs:
        movimiento = {'doc_id':''}
        movimiento['doc_id']=i.id
        for k,v in i.to_dict().items():
            movimiento[k]=v
        movimientos.append(movimiento)

    cuentas = {'BanortePlatinum':'Banorte Platinum','BanorteClasica':'Banorte Clásica','Efectivo':'Efectivo','Banamex':'Banamex','BanamexRewards':'Banamex Rewards','Nu':'Nu','BBVA':'BBVA'}

    TotalPorCuenta ={}
    for k,v in cuentas.items():
        total = (sum([i['monto'] for i in movimientos if (i['tipo']=='Ingreso')and(i['cuenta']==v)]))-(sum([i['monto'] for i in movimientos if (i['tipo']=='Egreso')and(i['cuenta']==v)]))+(sum([i['monto'] for i in movimientos if ('transcuentaingreso' in i)and(i['transcuentaingreso']==v)]))-(sum([i['monto'] for i in movimientos if ('transcuentaegreso' in i)and(i['transcuentaegreso']==v)]))
        TotalPorCuenta[k]=total

    TotalIngresos=sum([i['monto'] for i in movimientos if (i['tipo']=='Ingreso') and (i['subcategoria']!='Transferencia')])
    TotalEgresos=sum([i['monto'] for i in movimientos if (i['tipo']=='Egreso') and (i['subcategoria']!='Transferencia')])
    GranTotal = TotalIngresos-TotalEgresos    

    db.collection('home').document('d7x71RhHQede3VxMuMgN').set(TotalPorCuenta)
    db.collection('home').document('d7x71RhHQede3VxMuMgN').set({'TotalIngresos':TotalIngresos,'TotalEgresos':TotalEgresos,'GranTotal':GranTotal}, merge=True)

    return "Datos del Home actualizados"


@app.get("/gastado")
async def gastado():
    today = datetime.datetime.today()
    firstday = datetime.datetime(today.year, today.month, 1)
    firstday = datetime.datetime(2023,2,1)
    
    docs = db.collection('movimientos').where('fecha', '>=', firstday).stream()
    egresos_por_subcategoria={}
    for i in docs:
        if i.to_dict()['tipo'] =='Egreso':
            if i.to_dict()['subcategoria'] in egresos_por_subcategoria:
                egresos_por_subcategoria[i.to_dict()['subcategoria']]+=i.to_dict()['monto']
            else:
                egresos_por_subcategoria[i.to_dict()['subcategoria']]=i.to_dict()['monto']


    docs = db.collection('subcategoriasEgresos').stream()

    for doc in docs:
        if doc.to_dict()['subcategoria'] not in egresos_por_subcategoria:
            doc_ref = db.collection('subcategoriasEgresos').document(doc.id)
            doc_ref.set({'gastado': 0}, merge=True)

    for k, v in egresos_por_subcategoria.items():
        for doc in docs:
            if doc.to_dict()['subcategoria'] == k:
                doc_ref = db.collection('subcategoriasEgresos').document(doc.id)
                doc_ref.set({'gastado': v}, merge=True)

    
    return egresos_por_subcategoria

@app.get("/ingresado")
async def ingresado():
    today = datetime.datetime.today()
    firstday = datetime.datetime(today.year, today.month, 1)

    docs = db.collection('movimientos').where('fecha', '>=', firstday).stream()
    ingresos_por_subcategoria={}
    for i in docs:
        if i.to_dict()['tipo'] =='Ingreso':
            if i.to_dict()['subcategoria'] in ingresos_por_subcategoria:
                ingresos_por_subcategoria[i.to_dict()['subcategoria']]+=i.to_dict()['monto']
            else:
                ingresos_por_subcategoria[i.to_dict()['subcategoria']]=i.to_dict()['monto']

    docs = db.collection('subcategoriasIngresos').stream()

    for doc in docs:
        if doc.to_dict()['subcategoria'] not in ingresos_por_subcategoria:
            doc_ref = db.collection('subcategoriasIngresos').document(doc.id)
            doc_ref.set({'ingresado': 0}, merge=True)


    for k, v in ingresos_por_subcategoria.items():
        for doc in docs:
            if doc.to_dict()['subcategoria'] == k:
                doc_ref = db.collection('subcategoriasIngresos').document(doc.id)
                doc_ref.set({'ingresado': v}, merge=True)

    return f"Ingresado actualizado"





@app.get("/mensualidad")
async def mensualidad(nombre:str = Query(), mesdemensualidad:str = Query()):
    docs = db.collection(u'alumnos').stream()
    alumnos = []

    for i in docs:
        alumno = {'doc_id':''}
        alumno['doc_id']=i.id
        
        for k,v in i.to_dict().items():
            alumno[k]=v
        alumnos.append(alumno)

    for i in alumnos:
        if i['nombre']==nombre:
            listamensualidades = i['mensualidades']
            listamensualidades.append(mesdemensualidad)
            db.collection('alumnos').document(i['doc_id']).set({'mensualidades':listamensualidades}, merge=True)
    
    return f"Mensualidad de {mesdemensualidad} añadida a {nombre}"