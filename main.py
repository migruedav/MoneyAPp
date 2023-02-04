from fastapi import FastAPI
from pydantic import BaseModel
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials

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
    return {"message": "Hello World. Welcome to FastAPI!"}


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
        total = (sum([i['monto'] for i in movimientos if ('cuenta' in i)and(i['tipo']=='Ingreso')and(i['cuenta']==v)]))-(sum([i['monto'] for i in movimientos if ('cuenta' in i)and(i['tipo']=='Egreso')and(i['cuenta']==v)]))+(sum([i['monto'] for i in movimientos if ('transcuentaingreso' in i)and(i['transcuentaingreso']==v)]))-(sum([i['monto'] for i in movimientos if ('transcuentaegreso' in i)and(i['transcuentaegreso']==v)]))
        TotalPorCuenta[k]=total

    TotalIngresos=sum([i['monto'] for i in movimientos if i['tipo']=='Ingreso'])
    TotalEgresos=sum([i['monto'] for i in movimientos if i['tipo']=='Egreso'])
    GranTotal = TotalIngresos-TotalEgresos    

    db.collection('home').document('d7x71RhHQede3VxMuMgN').set(TotalPorCuenta)
    db.collection('home').document('d7x71RhHQede3VxMuMgN').set({'TotalIngresos':TotalIngresos,'TotalEgresos':TotalEgresos,'GranTotal':GranTotal}, merge=True)

    return "datos del home actualizados"
