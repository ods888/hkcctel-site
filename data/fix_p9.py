import json, re, os

DATA='/sessions/intelligent-upbeat-mccarthy/mnt/hkcctel/data'
static='/sessions/intelligent-upbeat-mccarthy/mnt/hkcctel/static/picture'

with open(os.path.join(DATA, 'products.json')) as f:
    products = json.load(f)

with open(os.path.join(DATA, 'all_sku_complete.json')) as f:
    all_sku = json.load(f)
with open(os.path.join(DATA, 'cuniq_details_full.json')) as f:
    details = json.load(f)
dm = {str(d['goodsId']): d for d in details}

filler = {}
for g in all_sku:
    gid = str(g['goodsId'])
    for s in g['skus']:
        filler[(gid, str(s['day']))] = s

def ch(h):
    if not h: return ''
    return re.sub(r'<!DOCTYPE[^>]*>|<html[^>]*>|</html>|<head>[\s\S]*?</head>|<body[^>]*>|</body>', '', h).strip()

def find_days(text):
    s = set()
    for m in re.finditer(r'(?<!\d)(\d+)[日]', text): s.add(int(m.group(1)))
    for m in re.finditer(r'(?<!\d)(\d+)[- ]?Day(?!\w)', text, re.IGNORECASE): s.add(int(m.group(1)))
    return s

def rd(html, vn):
    if not html or not vn: return html
    vs = str(vn)
    r = html
    for fv in sorted(find_days(html), reverse=True):
        if fv == vn: continue
        r = re.sub(rf'(?<!\d){fv}日(?!\d)', vs+'日', r)
        r = re.sub(rf'(?<!\d){fv}-Day(?!\w)', vs+'-Day', r, re.IGNORECASE)
        r = re.sub(rf'(?<!\d){fv}\s+Day(?!\w)', vs+' Day', r, re.IGNORECASE)
    return r

def rg(html, dl):
    if not html or not dl: return html
    m = re.search(r'(\d+)\s*GB', dl)
    tg = int(m.group(1)) if m else 0
    if tg <= 0: return html
    fg = set()
    for m2 in re.finditer(r'(?<!\d)(\d+)\s*GB(?!\d)', html, re.IGNORECASE):
        fg.add(int(m2.group(1)))
    if not fg: return html
    r = html
    for f in sorted(fg, reverse=True):
        if f == tg: continue
        r = re.sub(rf'(?<!\d){f}\s*GB(?!\d)', str(tg)+'GB', r, re.IGNORECASE)
    return r

d = dm.get('1021006', {})
td = d.get('tc', {}) or {}
ed = d.get('en', {}) or {}
th = ch(td.get('productDetailHTML', '') or '')
eh = ch(ed.get('productDetailHTML_EN', '') or '')
if not th: th = eh
if not eh: eh = th

sku365 = filler.get(('1021006', '365'))
wb_pid = sku365['pcid'] if sku365 else ''

variants_def = [
    ('365日 15GB', 198, '/static/picture/内地澳门365天15G.png'),
    ('365日 30GB', 298, '/static/picture/内地澳门365天30G.png'),
]

vlist = []
for lb, rp, vi in variants_def:
    vt = rd(th, 365)
    vt = rg(vt, lb)
    ve = rd(eh, 365)
    ve = rg(ve, lb)
    vnt = '中國內地及澳門365日上網卡 ' + lb + ' HK$' + str(rp)
    vne = 'China Mainland & Macau 365-Day SIM ' + lb.replace('日', ' Day') + ' HK$' + str(rp)
    ih = '<p><img src="' + vi + '" alt="' + lb + '" style="max-width:350px;width:100%;height:auto;"></p>\n'
    dtc = '<div class="product-desc-html">\n<div class="desc-section">\n' + ih + vt + '\n</div>\n</div>'
    den_ = '<div class="product-desc-html">\n<div class="desc-section">\n' + ih + ve + '\n</div>\n</div>'
    vlist.append({
        "shortLabel": lb.strip(), "price": rp, "image": vi,
        "name": vnt, "nameCn": vnt, "nameEn": vne,
        "description": dtc, "descriptionEn": den_, "descriptionCn": dtc,
        "prepaidCardId": wb_pid, "originalPrice": 0
    })

p9 = next((p for p in products if p['id'] == 9), None)
if p9:
    p9['variants'] = vlist
    p9['hasVariants'] = True
    p9['price'] = 198
    p9['image'] = vlist[0]['image']
    p9['description'] = vlist[0]['description']
    p9['descriptionEn'] = vlist[0]['descriptionEn']
    p9['descriptionCn'] = vlist[0]['descriptionCn']
    print('Product 9 fixed: {} variants, image={}'.format(len(vlist), p9['image']))

# Check ALL products for disk-existence
missing = []
for p in products:
    img = p.get('image', '')
    if img.startswith('/static/'):
        disk_path = '/sessions/intelligent-upbeat-mccarthy/mnt/hkcctel' + img
        if not os.path.exists(disk_path):
            missing.append('  [{0}] {1:.25s} main: {2}'.format(p['id'], p['name'], img))
    for v in p.get('variants', []):
        vi = v.get('image', '')
        if vi.startswith('/static/'):
            disk_path = '/sessions/intelligent-upbeat-mccarthy/mnt/hkcctel' + vi
            if not os.path.exists(disk_path):
                missing.append('  [{0}] {1:.25s} {2}: {3}'.format(p['id'], p['name'], v['shortLabel'], vi))

if missing:
    print('\nMISSING on disk:')
    for m in missing:
        print(m)
else:
    print('\nAll images exist on disk OK')

with open(os.path.join(DATA, 'products.json'), 'w') as f:
    json.dump(products, f, indent=2, ensure_ascii=False)
print('Saved')
