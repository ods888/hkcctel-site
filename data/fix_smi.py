import json
d=json.load(open('/sessions/intelligent-upbeat-mccarthy/mnt/hkcctel/data/products.json'))
p=next((p for p in d if p['id']==15), None)
if p:
    old=len(p['variants'])
    p['variants']=[v for v in p['variants'] if '2GB' not in v['shortLabel']]
    new=len(p['variants'])
    for v in p['variants']:
        if '8日' in v['shortLabel']:
            p['price']=v['price']; p['image']=v['image']
            p['description']=v['description']; p['descriptionEn']=v['descriptionEn']; p['descriptionCn']=v['descriptionCn']
    print('{}->{} SKUs'.format(old,new))
    for v in p['variants']:
        print('  [{0}] HK${1}'.format(v['shortLabel'],v['price']))
    json.dump(d,open('/sessions/intelligent-upbeat-mccarthy/mnt/hkcctel/data/products.json','w'),indent=2,ensure_ascii=False)
