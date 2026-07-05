import json
d=json.load(open('/sessions/intelligent-upbeat-mccarthy/mnt/hkcctel/data/products.json'))
for p in d:
    n=p.get('name','')
    if '日本' in n and '韓' not in n and 'Korea' not in n:
        print('[{}] gid={} {}'.format(p['id'],p.get('_gid',''),n[:60]))
        for v in p.get('variants',[]):
            print('    {} HK${} pid={}'.format(v['shortLabel'],v['price'],v.get('prepaidCardId','?')))
        print()
print('---')
# Also check workbuddy raw data for Japan-only
with open('/sessions/intelligent-upbeat-mccarthy/mnt/hkcctel/data/all_sku_complete.json') as f:
    all_sku=json.load(f)
for g in all_sku:
    gid=g['goodsId']
    if gid=='1021010':
        print('all_sku 1021010 (Japan):')
        for s in g['skus']:
            print('  day={} data={} price={} pid={}'.format(s['day'],s.get('data',''),s['price'],s['pcid']))
