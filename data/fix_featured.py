import json
d = json.load(open('/sessions/intelligent-upbeat-mccarthy/mnt/hkcctel/data/products.json'))
d[8]['featured'] = True
json.dump(d, open('/sessions/intelligent-upbeat-mccarthy/mnt/hkcctel/data/products.json', 'w'), indent=2, ensure_ascii=False)
print(f'[{d[8]["id"]}] {d[8]["name"]} → FEATURED')
