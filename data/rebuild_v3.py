#!/usr/bin/env python3
"""
Final rebuild v3: Excel priority, image-gated, only 6 featured.
Rule 1: Excel structure defines products & prices
Rule 2: Variants must have image (workbuddy CDN or local) to be included
Rule 3: Whole product skipped if zero variants have images
Rule 4: Only 6 featured: CMHK 3 + JP 8-day + SMI 8-day + CNMO 365 15GB
"""
import json, re, openpyxl, os
from collections import defaultdict

BASE = '/sessions/intelligent-upbeat-mccarthy/mnt/hkcctel'
DATA = os.path.join(BASE, 'data')

# ====== LOAD SOURCES ======
with open(os.path.join(DATA, 'all_sku_complete.json')) as f: all_sku = json.load(f)
with open(os.path.join(DATA, 'cuniq_details_full.json')) as f: details_list = json.load(f)
details = {str(d['goodsId']): d for d in details_list}

# Build workbuddy index: (gid, day_num) → {pcid, price, img}
filler = {}
for g in all_sku:
    gid = str(g['goodsId'])
    for s in g['skus']:
        filler[(gid, str(s['day']))] = s

# Scan local images
static_dir = os.path.join(BASE, 'static/picture')
local_files = set(f for f in os.listdir(static_dir) if f.lower().endswith(('.png','.jpg','.jpeg')))

# Build local image matcher (category, day) → filename
def build_local_map():
    m = {}
    for fname in sorted(local_files):
        fn = os.path.splitext(fname)[0].replace(' (1)', '')
        fnl = fn.lower()

        # P-code: P0000461
        pm = re.match(r'^P0*(\d+)', fn, re.I)
        if pm: m[('P', pm.group(1))] = fname; continue

        # Macau: zh.png
        if fnl == 'zh': m[('mo','1日')] = fname; continue

        # Vietnam digits
        if re.match(r'^\d+$', fn):
            m[('vn', fn+'日')] = fname; continue
        if 'yn8' in fnl and '15' in fnl: m[('vn','8日_15GB')] = fname; continue

        # China cnN-chi
        cnm = re.match(r'^cn(\d+)', fn, re.I)
        if cnm:
            d = cnm.group(1)
            m[('cnmo', d+'日')] = fname
            m[('cnmo_s', d+'日')] = fname
            continue
        if 'cnmc-90day-50' in fnl: m[('cnmo_s','90日_50GB')] = fname; continue
        if 'cnmc-90day-100' in fnl: m[('cnmo_s','90日_100GB')] = fname; continue
        if 'cnmc-180day-100' in fnl: m[('cnmo','180日_100GB')] = fname; continue
        if 'cnh-&-mo-180(33' in fnl: m[('cnmo_180','180日_33GB')] = fname; continue
        if 'cnh-&-mo-180(50' in fnl: m[('cnmo_180','180日_50GB')] = fname; continue
        if '内地澳门365天15g' in fnl: m[('cnmo_365','365日_15GB')] = fname; continue
        if '内地澳门365天30g' in fnl: m[('cnmo_365','365日_30GB')] = fname; continue

        # AU/NZ
        if re.match(r'^au\d', fn, re.I):
            dm = re.search(r'au(\d+)', fn, re.I)
            m[('anz', dm.group(1)+'日')] = fname; continue
        if 'au-90-50gb-chi' in fnl: m[('anz','90日_50GB')] = fname; continue

        # Japan
        if 'jp3-chi' in fnl: m[('jp','3日')] = fname; continue
        if 'jp30' in fnl: m[('jp','30日')] = fname; continue

        # JPKR
        jpk = re.match(r'^jpkr(\d+)', fn, re.I)
        if jpk: m[('jpk', jpk.group(1)+'日')] = fname; continue

        # Korea
        if 'southkorea5' in fnl: m[('kr','5日')] = fname; continue
        if 'southkorea8' in fnl: m[('kr','8日')] = fname; continue
        if 'korea30' in fnl: m[('kr','30日')] = fname; continue

        # Thailand
        th = re.match(r'^thai(\d+)', fn, re.I)
        if th: m[('th', th.group(1)+'日')] = fname; continue
        if 'thailand30' in fnl: m[('th','30日')] = fname; continue
        if 'thailand8' in fnl: m[('th','8日')] = fname; continue

        # Europe
        eu = re.match(r'^eu(\d+)', fn, re.I)
        if eu and 'eu7' not in fnl: m[('eu', eu.group(1)+'日')] = fname; continue
        if 'eu-90-100gb' in fnl: m[('eu','90日_100GB')] = fname; continue
        if 'eu-90-50gb' in fnl: m[('eu','90日_50GB')] = fname; continue

        # EU7
        eu7 = re.match(r'^eu7-(\d+)', fn, re.I)
        if eu7: m[('e7', eu7.group(1)+'日')] = fname; continue

        # Asia
        asm = re.match(r'^asia(\d+)', fn, re.I)
        if asm: m[('asia', asm.group(1)+'日')] = fname; continue

        # HK
        if 'hk3' in fnl: m[('hk','3日')] = fname; continue
        if 'hk7' in fnl: m[('hk','7日')] = fname; continue
        if 'hk30day' in fnl: m[('hk','30日')] = fname; continue
        if 'hk365-100gb' in fnl: m[('hk','365日_100GB')] = fname; continue
        if 'hk365-200gb' in fnl: m[('hk','365日_200GB')] = fname; continue

        # HKMO
        if 'hkmc4' in fnl: m[('hkmo','4日')] = fname; continue
        if 'hkmc7' in fnl: m[('hkmo','7日')] = fname; continue
        if 'hkmadin50' in fnl: m[('hkmo','180日_50GB')] = fname; continue

        # Malaysia
        if 'malaysia5' in fnl: m[('smi','5日')] = fname; continue

        # UAE
        if 'uae-4gb' in fnl: m[('ae','30日_4GB')] = fname; continue
        if 'uae-6gb' in fnl: m[('ae','30日_6GB')] = fname; continue

        # US/Mexico
        if 'usamexico-60' in fnl: m[('umx','60日')] = fname; continue
        if 'usamexico-90' in fnl: m[('umx','90日')] = fname; continue
        if 'mjm-60' in fnl: m[('umx','60日')] = fname; continue
        if 'mjm-90' in fnl: m[('umx','90日')] = fname; continue
        if 'mm25' in fnl: m[('umx','30日_25GB')] = fname; continue

        # US/Canada/Mexico
        if 'uscamexco30' in fnl: m[('ucm','30日')] = fname; continue
        if 'mjm12' in fnl: m[('ucm','30日_12GB')] = fname; continue

        # Middle Asia
        if 'middleasia-30-4gb' in fnl: m[('pk','30日_4GB')] = fname; continue
        if 'middleasia-30-6gb' in fnl: m[('pk','30日_6GB')] = fname; continue
        if 'middleasia-30-10gb' in fnl: m[('pk','30日_10GB')] = fname; continue

        # Middle East
        if '沙特10gb' in fnl: m[('me','30日_10GB')] = fname; continue
        if '沙特3010' in fnl: m[('me','30日_6GB')] = fname; continue

        # SE Asia
        if fnl == 'sea.jpg': m[('sea','8日')] = fname; continue
        if 'southeast1' in fnl: m[('an','8日')] = fname; continue

    return m

local_img = build_local_map()

# ====== HELPERS ======
def ch(h):
    if not h: return ''
    return re.sub(r'<!DOCTYPE[^>]*>|<html[^>]*>|</html>|<head>[\s\S]*?</head>|<body[^>]*>|</body>','',h).strip()

def find_days(text):
    s = set()
    for m in re.finditer(r'(?<!\d)(\d+)[日]',text): s.add(int(m.group(1)))
    for m in re.finditer(r'(?<!\d)(\d+)[- ]?Day(?!\w)',text,re.IGNORECASE): s.add(int(m.group(1)))
    return s

def rd(html, vn):
    if not html or not vn: return html
    vs = str(vn); r = html
    for fv in sorted(find_days(html), reverse=True):
        if fv == vn: continue
        r = re.sub(rf'(?<!\d){fv}日(?!\d)', vs+'日', r)
        r = re.sub(rf'(?<!\d){fv}-Day(?!\w)', vs+'-Day', r, re.IGNORECASE)
        r = re.sub(rf'(?<!\d){fv}\s+Day(?!\w)', vs+' Day', r, re.IGNORECASE)
    return r

def extract_gb(dl):
    if not dl: return 0
    m = re.search(r'(\d+)\+(\d+)', dl)
    if m: return int(m.group(1)) + int(m.group(2))
    m = re.search(r'Daily\s+(\d+)', dl)
    if m: return int(m.group(1))
    m = re.search(r'(\d+)\s*GB', dl)
    if m: return int(m.group(1))
    return 0

def rg(html, dl):
    if not html or not dl: return html
    tg = extract_gb(dl)
    if tg <= 0: return html
    fg = set()
    for m in re.finditer(r'(?<!\d)(\d+)\s*GB(?!\d)', html, re.IGNORECASE):
        fg.add(int(m.group(1)))
    if not fg: return html
    r = html
    for f in sorted(fg, reverse=True):
        if f == tg: continue
        r = re.sub(rf'(?<!\d){f}\s*GB(?!\d)', str(tg)+'GB', r, re.IGNORECASE)
    return r

ts = {}
for a,b in [('網','网'),('數','数'),('據','据'),('電','电'),('聯','联'),('動','动'),
    ('號','号'),('萬','万'),('與','与'),('為','为'),('專','专'),('業','业'),
    ('態','态'),('係','系'),('認','认'),('證','证'),('資','资'),('訊','讯'),
    ('導','导'),('爾','尔'),('羅','罗'),('門','门'),('線','线'),('開','开'),
    ('時','时'),('間','间'),('頭','头'),('機','机'),('話','话'),('務','务'),
    ('設','设'),('計','计'),('劃','划'),('總','总'),('產','产'),('單','单'),
    ('價','价'),('買','买'),('賣','卖'),('購','购'),('選','选'),('擇','择'),
    ('點','点'),('變','变'),('從','从'),('馬','马'),('亞','亚'),('歐','欧'),
    ('優','优'),('內','内'),('後','后'),('對','对'),('應','应'),('達','达'),
    ('過','过'),('還','还'),('這','这'),('東','东'),('華','华'),('國','国'),
    ('臺','台'),('韓','韩'),('會','会'),('區','区'),('條','条'),('級','级'),
    ('經','经'),('結','结'),('統','统'),('續','续'),('護','护'),('謝','谢'),
    ('識','识'),('讀','读'),('歷','历'),('預','预'),('領','领'),('飛','飞'),
    ('紐','纽'),('泰','泰'),('英','英'),('法','法'),('墨','墨'),('阿','阿'),
    ('酋','酋'),('埃','埃'),('及','及'),('巴','巴'),('基','基'),('坦','坦'),
    ('哈','哈'),('薩','萨'),('克','克'),('土','土'),('耳','耳'),('其','其'),
    ('美','美'),('加','加'),('南','南'),('洲','洲'),('沙','沙'),('特','特'),
    ('拉','拉'),('伯','伯'),('越','越'),('印','印'),('尼','尼'),('菲','菲'),
    ('賓','宾'),('柬','柬'),('埔','埔'),('寨','寨'),('老','老'),('撾','挝'),
    ('群','群'),('維','维'),('義','义'),('豐','丰'),('書','书'),('寫','写'),
    ('滿','满'),('邊','边'),('遠','远'),('際','际')]:
    ts[a]=b

def t2c(t):
    if not t: return ''
    r = ''.join(ts.get(ch,ch) for ch in t)
    for o,n in [('南韩','韩国'),('新马泰','新马泰'),('哈萨克','哈萨克斯坦'),
        ('流动数据','移动数据'),('话音','语音'),('短讯','短信'),
        ('公平使用数据','公平使用流量'),('启用','激活'),('增值','充值'),
        ('通话/上网卡','通话上网卡')]:
        r = r.replace(o,n)
    return r

def dn(dl):
    return int(''.join(c for c in dl if c.isdigit()) or '0')

def classify(r):
    cn = str(r[4]or'')+str(r[5]or''); en = str(r[6]or''); n = cn+en
    if '日韓' in n: return 'jpk'
    if '南韓' in n: return 'kr'
    if '日本' in n: return 'jp'
    if '越' in cn: return 'vn'
    if '星馬泰' in n or '馬來西亞' in n or '印尼' in n: return 'smi'
    if '泰國' in n: return 'th'
    if '阿聯酋' in n: return 'ae'
    if '沙特' in cn: return 'me'
    if '美加墨' in n: return 'ucm'
    if '美墨' in n or '美國及墨西哥' in n: return 'umx'
    if '澳紐' in n: return 'anz'
    if '澳洲' in n: return 'au'
    if '巴基斯坦' in n: return 'pk'
    if '英法' in n or '意大利' in n: return 'e7'
    if '歐洲' in n: return 'eu'
    if '法國' in n: return 'fr'
    if '東盟' in n: return 'an'
    if '東南亞' in n: return 'sea'
    if '亞太' in n or '亞洲' in n: return 'asia'
    if '香港' in cn and '澳門' in cn and ('内地' in cn or '內地' in cn): return 'cnhkmo'
    if ('内地' in cn or '內地' in cn) and '澳門' in cn: return 'cnmo'
    if '香港' in cn and '澳門' in cn: return 'hkmo'
    if '香港' in cn: return 'hk'
    if '澳門' in cn: return 'mo'
    return 'other'

# ====== READ EXCEL ======
wb = openpyxl.load_workbook('/sessions/intelligent-upbeat-mccarthy/mnt/uploads/灿成價格表20260401.xlsx')
ws = wb.active

groups = defaultdict(list)
for row in ws.iter_rows(min_row=2, values_only=True):
    cd = row[0]; cn = str(row[4]or row[5]or''); en = str(row[6]or''); ct = str(row[5]or'')
    if not cd: continue
    cat = classify(row)
    dm_ = re.search(r'(\d+)日',cn+ct); dl = dm_.group(1)+'日' if dm_ else ''
    gm = re.search(r'\(([^)]*\d+\s*GB[^)]*)\)',cn+ct)
    dal = gm.group(1) if gm else ''
    if not dal:
        gm = re.search(r'(\d+\+?\d*\s*GB\s*FUP)',cn+ct)
        dal = gm.group(1) if gm else ''
    if not dal:
        gm = re.search(r'\(Daily\s*\d+\s*GB\)',cn+ct)
        dal = gm.group(0) if gm else ''
    pm = re.search(r'\$(\d+)',cn+ct)
    retail = int(pm.group(1)) if pm else 0
    cnc = re.sub(r'\s*\$[\d,]+.*','',cn).strip()
    cnc = re.sub(r'^5G\s*','',cnc).strip()
    groups[cat].append({'code':str(cd),'cn':cnc,'en':en,'day':dl,'data':dal,'retail':retail})

cnmo = groups.pop('cnmo',[])
for nm,it in [('cnmo_s',[i for i in cnmo if dn(i['day'])<=90 and i['day']]),
             ('cnmo_180',[i for i in cnmo if dn(i['day'])==180]),
             ('cnmo_365',[i for i in cnmo if dn(i['day'])==365])]:
    if it: groups[nm] = it

# ====== METADATA ======
cat_gid = {'mo':'900778','hk':'1021002','hkmo':'1021004',
    'cnmo_s':'1021006','cnmo_180':'1021006','cnmo_365':'1021006','cnhkmo':'1021191',
    'jp':'1021010','jpk':'1021012','kr':'1021011','vn':'1021013','smi':'1021016',
    'th':'1021014','anz':'1021024','au':'1021295','eu':'1021023','ucm':'1021030',
    'ae':'1021031','fr':'1021033','umx':'1021123','pk':'10200131','me':'1021032',
    'an':'1021017','sea':'1021018','asia':'1021019','e7':'10200137'}

cat_tc = {'mo':'澳門上網卡','hk':'香港上網卡','hkmo':'香港及澳門上網卡',
    'cnmo_s':'中國內地及澳門上網卡','cnmo_180':'中國內地及澳門180日上網卡',
    'cnmo_365':'中國內地及澳門365日上網卡','cnhkmo':'內地、香港及澳門365日上網卡',
    'jp':'日本多日上網卡','jpk':'日韓多日上網卡','kr':'南韓多日上網卡',
    'vn':'越南多日上網卡','smi':'新馬泰印尼多日上網卡','th':'泰國上網卡',
    'anz':'澳紐多日上網卡','au':'澳洲上網卡','eu':'歐洲多日上網卡',
    'ucm':'美加墨上網卡','ae':'阿聯酋上網卡','fr':'法國上網卡','umx':'美墨上網卡',
    'pk':'中南亞多地上網卡','me':'中東上網卡','an':'東盟上網卡','sea':'東南亞上網卡',
    'asia':'亞洲多日上網卡','e7':'英法意等7國上網卡'}

cat_en = {'mo':'Macau Prepaid SIM','hk':'Hong Kong Prepaid SIM','hkmo':'HK & Macau Prepaid SIM',
    'cnmo_s':'China Mainland & Macau SIM','cnmo_180':'China Mainland & Macau 180-Day SIM',
    'cnmo_365':'China Mainland & Macau 365-Day SIM','cnhkmo':'Mainland, HK & Macau 365-Day SIM',
    'jp':'Japan Prepaid SIM','jpk':'Japan & Korea SIM','kr':'South Korea SIM',
    'vn':'Vietnam Prepaid SIM','smi':'SG, MY, TH & ID SIM','th':'Thailand Prepaid SIM',
    'anz':'Australia & NZ SIM','au':'Australia SIM','eu':'Europe Prepaid SIM',
    'ucm':'USA, Canada & Mexico SIM','ae':'UAE Prepaid SIM','fr':'France SIM',
    'umx':'USA & Mexico SIM','pk':'Central & South Asia SIM','me':'Middle East SIM',
    'an':'ASEAN 8-Day SIM','sea':'SE Asia 8-Day SIM','asia':'Asia Multi-Day SIM','e7':'UK, France & Italy SIM'}

display_sku = {'jp':('8日','8+3GB'), 'smi':('8日','3GB'), 'cnmo_365':('365日','15GB'),
    'cnmo_s':('2日',None), 'mo':('1日',None), 'anz':('10日',None),
    'th':('5日',None), 'kr':('5日','3GB'), 'vn':('8日',None), 'ucm':('30日',None)}

# ONLY these 6 are featured
featured_ids = set()  # Will be set after build

# ====== KEEP CMHK MANUAL ======
with open(os.path.join(DATA, 'products.json')) as f: old = json.load(f)
manual = [p for p in old if not p.get('_src') or p.get('_src')!='cuniq']
for p in manual:
    for fl in ['_src','_gid','_ppid','_oprice','hasVariants','variants']:
        p.pop(fl, None)
    p['featured'] = True  # CMHK 3 = always featured
next_pid = max(p['id'] for p in manual) + 1 if manual else 1

# ====== BUILD PRODUCTS ======
cctel = []
order = ['mo','hk','hkmo','cnmo_s','cnmo_180','cnmo_365','cnhkmo',
    'jp','jpk','kr','vn','smi','th','anz','au','eu','fr','ucm',
    'umx','ae','pk','me','asia','an']

for cat in order:
    items = groups.get(cat, [])
    if not items: continue
    gid = cat_gid.get(cat, '')
    d = details.get(gid, {})
    td = d.get('tc',{}) or {}; ed = d.get('en',{}) or {}
    th = ch(td.get('productDetailHTML','') or '')
    eh = ch(ed.get('productDetailHTML_EN','') or '')
    if not th: th = eh
    if not eh: eh = th

    ntc = cat_tc.get(cat, cat)
    nen = cat_en.get(cat, cat)

    # Match Excel rows to images
    matched = []
    for it in items:
        dl = it['day']
        if not dl: continue
        vd = dn(dl)
        vds = str(vd)

        # Find image: local first, then workbuddy CDN
        local = local_img.get((cat, dl))  # (cat, 'X日')
        if not local:
            local = local_img.get((cat, dl + '_' + it.get('data',''))) if it.get('data') else None

        sku = filler.get((str(gid), vds))
        wb_img = sku.get('img','') if sku else ''
        wb_pid = sku['pcid'] if sku else ''

        # Image resolution: local > workbuddy CDN
        vi = '/static/picture/' + local if local else wb_img

        # Rule 1: variant must have image
        if not vi: continue

        # Price: Excel retail first, workbuddy fallback
        rp = it['retail'] if it['retail'] > 0 else (sku['price'] if sku else 0)

        matched.append((it, vd, rp, vi, wb_pid))

    # Rule 3: skip entire product if no variants have images
    if not matched: continue

    # Build variants
    vlist = []
    for it, vd, rp, vi, pw in matched:
        dl = it['day']; dal = it['data']
        lb = dl + ' ' + dal if dal else dl

        vt = rd(th, vd); vt = rg(vt, dal)
        ve = rd(eh, vd); ve = rg(ve, dal)

        vnt = ntc + ' ' + lb + ' HK$' + str(rp)
        vnc = t2c(vnt)
        vne = nen + ' ' + dl.replace('日',' Day') + ' HK$' + str(rp)

        ih = '<p><img src="' + vi + '" alt="' + lb + '" style="max-width:350px;width:100%;height:auto;"></p>\n' if vi else ''
        dtc = '<div class="product-desc-html">\n<div class="desc-section">\n' + ih + vt + '\n</div>\n</div>'
        den = '<div class="product-desc-html">\n<div class="desc-section">\n' + ih + ve + '\n</div>\n</div>'

        vlist.append({"shortLabel":lb.strip(),"price":rp,"image":vi,"name":vnt,"nameCn":vnc,"nameEn":vne,
            "description":dtc,"descriptionEn":den,"descriptionCn":dtc,"prepaidCardId":pw,"originalPrice":0})

    vlist.sort(key=lambda v: v['price'])

    # Display SKU
    di = 0
    ds = display_sku.get(cat)
    if ds:
        td_day, td_data = ds
        for idx_v, v in enumerate(vlist):
            sl = v['shortLabel']
            if td_day in sl:
                if td_data is None or td_data in sl:
                    di = idx_v; break
    dv = vlist[di]
    vl = len(vlist)

    # Featured: only these specific products
    featured = False
    if cat == 'jp' and '8日' in dv['shortLabel']: featured = True
    elif cat == 'smi' and '8日' in dv['shortLabel']: featured = True
    elif cat == 'cnmo_365': featured = True

    cctel.append({
        "id": next_pid, "name": ntc, "nameEn": nen, "nameCn": t2c(ntc),
        "summary": (str(vl)+' plans' if vl>1 else ''),
        "summaryEn": ('Multiple plans' if vl>1 else ''),
        "summaryCn": (str(vl)+'个方案' if vl>1 else ''),
        "description": dv['description'],
        "descriptionEn": dv['descriptionEn'],
        "descriptionCn": dv['description'],
        "price": dv['price'],
        "image": dv['image'],
        "featured": featured, "active": True,
        "createdAt": "2026-06-13T00:00:00.000Z",
        "hasVariants": vl > 1,
        "variants": vlist if vl > 1 else [],
        "_src": "cuniq", "_gid": str(gid)
    })
    next_pid += 1

    print('[{id}] {name:.35s} HK${pr} | {n}v | feat={f} | display: {ds}'.format(
        id=next_pid-1, name=ntc, pr=dv['price'], n=vl, f=featured, ds=dv['shortLabel']))
    for v in vlist[:3]:
        mark = ' ←' if v == dv else ''
        loc = 'L' if v['image'].startswith('/static/') else 'C'
        print('    {:25s} HK${:<6d} {}{}'.format(v['shortLabel'], v['price'], loc, mark))

# ====== MERGE & SAVE ======
all_p = manual + cctel
all_p.sort(key=lambda p: p['id'])
with open(os.path.join(DATA, 'products.json'), 'w') as f:
    json.dump(all_p, f, indent=2, ensure_ascii=False)

print('\n=== FINAL ===')
print('Manual:{} CUniq:{} Total:{}'.format(len(manual), len(cctel), len(all_p)))
print('Featured: {}'.format([p['id'] for p in all_p if p.get('featured')]))
total_v = sum(len(p.get('variants',[])) for p in cctel)
print('Total variants: {}'.format(total_v))

loc = sum(1 for p in cctel for v in p.get('variants',[]) if v.get('image','').startswith('/static/'))
cuniq = sum(1 for p in cctel for v in p.get('variants',[]) if 'cuniq.com' in v.get('image',''))
print('Images: {} local + {} CUNIQ = {}'.format(loc, cuniq, loc+cuniq))
