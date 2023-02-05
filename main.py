from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import Query
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials

config = {
  "type": "service_account",
  "project_id": "moneyapp-f3a82",
  "private_key_id": "94ccf78707acfe49f01a311ed6237c505726fe08",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDjVlNvAin4Dxlo\nXqCUiMQzGC8DYCApU+4ZGjXtqbXI03kV/TBgERCJtB+Q1xNsHLQBsWx0poobyrlV\n/sR4C8xRbb9jQSlmWWRTsuxrlQplEr/KCRI8+9uwrFJK08x9cyDESkkq7n2fKUrp\np1svKGO20sTCD5dGGB1p2cEFxECSDT6jdFz9ZN+8xTHWmyms0l9LuhDjWWZdTlXB\nyJ6bvatCKhit477p49rVdJr/OoPAq6az4pRRC5HVSY89qEAa6uqjj/G1LoVKpjmB\nMCjsr76NviuO1/aV+EKR3RQJA8dOfoqgf5+zpg/lZKGmj0wY0+TZiNrYyq+p/Gos\n+wIIw/ZPAgMBAAECggEAGzBR3i7mEhLMOR1IGzuYK3wy8zZl4kt1aG8oD/qCETip\nfKXBSVwBHFb8h3gRjJaKOMGddP4N+nDuZYiIusq+buavQxGh/+mlBBWcDOnQSnJJ\nmcIn+j8s8R5K4UQfasmAG7m+snG/eG+Z1AP99c/gzRa8DXGL6AguTGCMo0HrbwwI\nwtv9n1mw+m4x6nsXPbHaTgXb6M4SaM1aZDAZRJQvOdOJYKEZkdtXe4vT3U+O44iX\nmKoSYSDBW0iXut3FYhwmu73aH+L/wV1Ici8uDIdwuWtgcEmmeGc/wXiFHgp1bxLW\nqhFL7XpTi2n5e5NYTw/6D1yuz49NWWru9LhOByx8EQKBgQDzT/19VOAcinxuI38c\nGDbfOqeY+wlkBZpWHozCw/WXd1J9kGNL6HnR/XtYXm7lxrp2SXqmStN4L5qzZk30\n6f7W8JDaOdQTII1KTGt5mv8EVG+khNYKLCwjBOxW/DKWQpL8xLOJ7D78+Xvp0lfA\nME/H8SvovAUXI1zcJ8YP/kl9ywKBgQDvMRR7WBA3RWKvsFVI7unByRTBxA8anTbd\n0L9vxuF+h4jq/+Ua604pzXqvF5IxHOgjPqaKTXMBaULY2qKZD0vQBz5k1SKsB0/P\nzaLGUn2rXhSGhwhM5K2+MjKx/gCyyvr6l2fQk6if5YXrtb/hArOAJ5I+Vg5mqTwv\nxVhkLUdZDQKBgQDElfGSzPvSM5Y7itSNh4b2L7bwJIw+00QSptZGGvwYKCFvMDT6\nRNgAcVSyXoIthrZrEg1VxIk9xwCwSE1eP51WXsI6f5S464kc6cfAVhoLjokxnN4v\nE+eJV9X4pgXdX+bQ8cC6BDYUQSL8FaYusxoSyuoWPavDOSAzBLPDgkowpwKBgQDh\nSFrAKZtsU1+1leFdxhhIurlgHucS7AwnM1t7TdhIsiMVI1uH1SRTXwM0MoEw3McP\nmwyEqpmtNJUPZi1K+AsxrgDoO45idKiJUmcDX+KZKw0t/7Sjp6a0wtbYqiHCREfL\nChtvagOiRi2yagaFSWQDSkIFkEwUCUV0wOyVvce7aQKBgHCEP6Udcgi5yVfLQPWP\nzrG/YYpZ9QXfNzqB12OHmSAhf6BefufxVc0Lz8TM1BGVV3bHvdc4qvhT+8Vhty5Z\nO+hr2ebsxovHL1bnY600T0yE54DTeYZn0qVUuPvJU+VSROCYklFr9OFSibtUWRMB\nq5T8CegUAcahY4jmZy9z92WO\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-cuo23@moneyapp-f3a82.iam.gserviceaccount.com",
  "client_id": "110960060264860021759",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-cuo23%40moneyapp-f3a82.iam.gserviceaccount.com"
}


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
    movimientos = []
    docs = db.collection(u'movimientos').stream()

    for i in docs:
        movimiento = {'doc_id':''}
        movimiento['doc_id']=i.id
        
        for k,v in i.to_dict().items():
            movimiento[k]=v
        movimientos.append(movimiento)

    subcategorias = []
    docs = db.collection(u'subcategoriasEgresos').stream()

    for i in docs:
        movimiento = {'doc_id':''}
        movimiento['doc_id']=i.id
        
        for k,v in i.to_dict().items():
            movimiento[k]=v
        subcategorias.append(movimiento)
    
    subs=[]
    for i in subcategorias:
        subs.append(i['subcategoria'])
    
    for s in subcategorias:
        total = sum([m['monto'] for m in movimientos if (m['tipo']=='Egreso')and (m['subcategoria']==subs[0])])
        db.collection('subcategoriasEgresos').document(s['doc_id']).set({'gastado':total},merge=True)
        subs.pop(0)
    
    return f"Gastado actualizado"

@app.get("/mensualidad")
async def gastado(nombre:str = Query(), mesdemensualidad:str = Query()):
    docs = db.collection(u'alumnos').stream()
    alumnos = []

    for i in docs:
        alumno = {'doc_id':''}
        alumno['doc_id']=i.id
        
        for k,v in i.to_dict().items():
            alumno[k]=v
        alumnos.append(alumno)

        for i in alumnos:
            if nombre == i['nombre']:
                listamensualidades = i['mensualidades']
                listamensualidades.append(mesdemensualidad)
        
        db.collection('alumnos').document(i['doc_id']).set({'mensualidades':listamensualidades}, merge=True)
    
    return f"Mensualidad de {mesdemensualidad} añadida a {nombre}"