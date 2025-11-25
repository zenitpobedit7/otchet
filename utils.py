import pandas as pd

COLUMN_CANDIDATES = {
    'turnover': ['сумма заказа','сумма','amount','order total','total','продажи','sales','revenue','итого'],
    'commission': ['комиссия','commission','fee'],
    'logistics': ['логистика','доставка','logistics','shipping','delivery'],
    'cost': ['себестоимость','cost','cost price'],
    'other': ['прочие','other','tax','налог'],
    'brand': ['бренд','brand','manufacturer'],
    'category': ['категория','category','section','раздел'],
    'date': ['дата','date','order date','дата заказа','created at'],
    'qty': ['количество','qty','quantity','units']
}

def find_key(keys, candidates):
    keys_low = [str(k).lower() for k in keys]
    for c in candidates:
        for i,k in enumerate(keys_low):
            if c in k:
                return keys[i]
    return None

def detect_and_normalize(df: pd.DataFrame):
    keys = list(df.columns)
    mapping = {}
    for field,candidates in COLUMN_CANDIDATES.items():
        mapping[field] = find_key(keys, candidates)

    rows = []
    for _, r in df.iterrows():
        def get_val(col):
            if col is None:
                return 0
            v = r.get(col, 0)
            if pd.isna(v):
                return 0
            return v
        date_val = None
        if mapping.get('date'):
            d = r.get(mapping['date'])
            try:
                if pd.isna(d):
                    date_val = None
                else:
                    date_val = pd.to_datetime(d).strftime('%Y-%m-%d')
            except Exception:
                date_val = None
        try:
            row = {
                'turnover': float(get_val(mapping['turnover']) or 0),
                'commission': float(get_val(mapping['commission']) or 0),
                'logistics': float(get_val(mapping['logistics']) or 0),
                'cost': float(get_val(mapping['cost']) or 0),
                'other': float(get_val(mapping['other']) or 0),
                'brand': str(get_val(mapping['brand']) or '').strip(),
                'category': str(get_val(mapping['category']) or '').strip(),
                'date': date_val
            }
            rows.append(row)
        except Exception:
            continue

    keys_concat = ' '.join([str(k).lower() for k in keys])
    if 'ozon' in keys_concat or (mapping['turnover'] and 'сумма заказа' in str(mapping['turnover']).lower()):
        marketplace = 'ozon'
    elif 'wildberries' in keys_concat or 'wb' in keys_concat:
        marketplace = 'wildberries'
    else:
        marketplace = 'unknown'

    return {'rows': rows, 'marketplace': marketplace, 'mapping': mapping}

def build_report(rows):
    agg = {'turnover':0,'commission':0,'logistics':0,'cost':0,'other':0}
    byBrand = {}
    byCategory = {}
    byDate = {}
    for r in rows:
        agg['turnover'] += r.get('turnover',0)
        agg['commission'] += r.get('commission',0)
        agg['logistics'] += r.get('logistics',0)
        agg['cost'] += r.get('cost',0)
        agg['other'] += r.get('other',0)
        if r.get('brand'):
            byBrand[r['brand']] = byBrand.get(r['brand'],0) + r.get('turnover',0)
        if r.get('category'):
            byCategory[r['category']] = byCategory.get(r['category'],0) + r.get('turnover',0)
        if r.get('date'):
            byDate[r['date']] = byDate.get(r['date'],0) + r.get('turnover',0)

    profit = agg['turnover'] - (agg['commission'] + agg['logistics'] + agg['cost'] + agg['other'])
    topBrands = sorted([{'brand':k,'sum':v} for k,v in byBrand.items()], key=lambda x:-x['sum'])
    topCats = sorted([{'category':k,'sum':v} for k,v in byCategory.items()], key=lambda x:-x['sum'])
    series = [{'date':d,'turnover':v} for d,v in sorted(byDate.items())]
    chart = [
        {'name':'Комиссия','value':agg['commission']},
        {'name':'Логистика','value':agg['logistics']},
        {'name':'Себестоимость','value':agg['cost']},
        {'name':'Другие','value':agg['other']},
    ]
    return {'rows':rows,'aggregates':agg,'profit':profit,'topBrands':topBrands,'topCats':topCats,'series':series,'chart':chart}
