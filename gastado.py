def gastado():
    
    today = datetime.datetime.today()
    firstday = datetime.datetime(today.year, today.month, 1)
    
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

    docs = db.collection('subcategoriasEgresos').stream()

    for k, v in egresos_por_subcategoria.items():
        for doc in docs:
            if doc.to_dict()['subcategoria'] == k:
                doc_ref = db.collection('subcategoriasEgresos').document(doc.id)
                doc_ref.set({'gastado': v}, merge=True)

    
    return egresos_por_subcategoria