#!/usr/bin/env python3
"""Rebuild products.json: Excel结构 + workbuddy零售价(严格匹配) + workbuddy图片。缺失=0"""
import json, re, openpyxl
from collections import defaultdict

base = '/sessions/intelligent-upbeat-mccarthy/mnt/hkcctel/data'

# Load workbuddy data
raw_str = open(base+'/cuniq_variants_raw.json').read().strip()
raw_all = json.loads(json.loads(raw_str))
with open(base+'/cuniq_details_full.json') as f: details_list = json.load(f)
with open(base+'/variant_images.json') as f: imgs = json.load(f)
details_map = {str(d['goodsId']): d for d in details_list}
pid_img = {}
for item in imgs: pid_img[str(item['prepaidCardId'])] = item.get('result',{}).get('image','') or ''

def clean(h):
    if not h: return ''
    return re.sub(r'<!DOCTYPE[^>]*>|<html[^>]*>|</html>|<head>[\s\S]*?</head>|<body[^>]*>|</body>','',h).strip()

def find_days(text):
    s = set()
    for m in re.finditer(r'(?<!\d)(\d+)[日]',text): s.add(int(m.group(1)))
    for m in re.finditer(r'(?<!\d)(\d+)[- ]?Day(?!\w)',text,re.IGNORECASE): s.add(int(m.group(1)))
    return s

def replace_days(html, vn):
    if not html or not vn: return html
    vns = str(vn); result = html
    for fd in sorted(find_days(html), reverse=True):
        if fd == vn: continue
        result = re.sub(rf'(?<!\d){fd}日(?!\d)', vns+'日', result)
        result = re.sub(rf'(?<!\d){fd}-Day(?!\w)', vns+'-Day', result, re.IGNORECASE)
        result = re.sub(rf'(?<!\d){fd}\s+Day(?!\w)', vns+' Day', result, re.IGNORECASE)
    return result

tc_sc = {}
pairs = [
    ('網','网'),('數','数'),('據','据'),('電','电'),('聯','联'),('動','动'),('號','号'),('萬','万'),
    ('與','与'),('為','为'),('專','专'),('業','业'),('態','态'),('係','系'),('認','认'),('證','证'),
    ('資','资'),('訊','讯'),('導','导'),('爾','尔'),('羅','罗'),('門','门'),('線','线'),('開','开'),
    ('時','时'),('間','间'),('頭','头'),('機','机'),('話','话'),('務','务'),('設','设'),('計','计'),
    ('劃','划'),('總','总'),('產','产'),('單','单'),('價','价'),('買','买'),('賣','卖'),('購','购'),
    ('選','选'),('擇','择'),('點','点'),('變','变'),('從','从'),('馬','马'),('亞','亚'),('歐','欧'),
    ('優','优'),('內','内'),('後','后'),('對','对'),('應','应'),('達','达'),('過','过'),('還','还'),
    ('這','这'),('東','东'),('華','华'),('國','国'),('臺','台'),('韓','韩'),('會','会'),('區','区'),
    ('條','条'),('級','级'),('經','经'),('結','结'),('統','统'),('續','续'),('護','护'),('謝','谢'),
    ('識','识'),('讀','读'),('歷','历'),('預','预'),('領','领'),('飛','飞'),('紐','纽'),('泰','泰'),
    ('英','英'),('法','法'),('墨','墨'),('阿','阿'),('酋','酋'),('埃','埃'),('及','及'),('巴','巴'),
    ('基','基'),('坦','坦'),('哈','哈'),('薩','萨'),('克','克'),('土','土'),('耳','耳'),('其','其'),
    ('美','美'),('加','加'),('南','南'),('洲','洲'),('沙','沙'),('特','特'),('拉','拉'),('伯','伯'),
    ('越','越'),('印','印'),('尼','尼'),('菲','菲'),('賓','宾'),('柬','柬'),('埔','埔'),('寨','寨'),
    ('老','老'),('撾','挝'),('群','群'),('維','维'),('義','义'),('豐','丰'),('書','书'),('寫','写'),
    ('滿','满'),('邊','边'),('遠','远'),('際','际')
]
for a,b in pairs: tc_sc[a]=b
def to_cn(t):
    if not t: return ''
    r = ''.join(tc_sc.get(ch,ch) for ch in t)
    for o,n in [('南韩','韩国'),('澳纽','澳纽'),('新马泰','新马泰'),('哈萨克','哈萨克斯坦'),
        ('流动数据','移动数据'),('话音','语音'),('短讯','短信'),('公平使用数据','公平使用流量'),
        ('启用','激活'),('增值','充值'),('通话/上网卡','通话上网卡')]:
        r = r.replace(o,n)
    return r

def day_num(dl):
    return int(''.join(c for c in dl if c.isdigit()) or '0')

def area_from_html(h):
    if not h: return ''
    t = re.sub(r'<[^>]+>',' ',h)
    m = re.search(r'(?:Coverage area|覆蓋地區)\s+([^BIVWESUeu基話可啟S]+?)(?:Basic|基本信息|Voice|話音|Whether|可否|Enable|啟用|SIM|User|eSIM|$)',t)
    return m.group(1).strip().rstrip('.').strip() if m else ''

# Classify Excel row
def classify(r):
    cn = str(r[4] or '')+str(r[5] or ''); en = str(r[6] or ''); n = cn+en
    if '英法' in n or 'UK' in n: return '英法意等7國'
    if '日韓' in n: return '日韓'
    if '南韓' in n: return '南韓'
    if '日本' in n: return '日本'
    if '越' in cn: return '越南'
    if '星馬泰' in n: return '星馬泰及印尼'
    if '泰國' in n: return '泰國'
    if '阿聯酋' in n: return '阿聯酋'
    if '中東' in cn or '沙特' in cn: return '中東'
    if '美加墨' in n: return '美加墨'
    if '美墨' in n or '美國及墨西哥' in n: return '美墨'
    if '南美' in n: return '南美'
    if '澳紐' in n: return '澳紐'
    if '澳洲' in n: return '澳洲'
    if '巴基斯坦' in n: return '巴基斯坦'
    if '歐洲' in n: return '歐洲'
    if '法國' in n: return '法國'
    if '東盟' in n: return '東盟'
    if '東南亞' in n: return '東南亞'
    if '亞洲' in n: return '亞洲'
    if '台灣' in n: return '台灣'
    if '俄羅斯' in n: return '其他'
    if '香港' in cn and '澳門' in cn and ('内地' in cn or '內地' in cn): return '内地港澳'
    if ('内地' in cn or '內地' in cn) and '澳門' in cn: return '内地澳門'
    if '香港' in cn and '澳門' in cn: return '港澳'
    if '香港' in cn: return '香港'
    if '澳門' in cn: return '澳門'
    if '馬來西亞' in n: return '星馬泰及印尼'
    return '其他'

wb = openpyxl.load_workbook('/sessions/intelligent-upbeat-mccarthy/mnt/uploads/灿成價格表20260401.xlsx')
ws = wb.active

groups = defaultdict(list)
for row in ws.iter_rows(min_row=2, values_only=True):
    code = row[0]; cn = str(row[4] or row[5] or ''); en = str(row[6] or ''); content = str(row[5] or '')
    if not code: continue
    cat = classify(row)
    dm = re.search(r'(\d+)日', cn+content); dl = dm.group(1)+'日' if dm else ''
    gm = re.search(r'(\d+\s*GB|Daily\s*\d+\s*GB)', cn+en+content); dal = gm.group(1) if gm else ''
    cn_clean = re.sub(r'\s*\$[\d,]+.*','', cn).strip()
    cn_clean = re.sub(r'^5G\s*','', cn_clean).strip()
    groups[cat].append({'code':str(code),'cn':cn_clean,'en':en,'day':dl,'data':dal})

# Split 内地澳門 by day range
mainland = groups.pop('内地澳門', [])
slits = [
    ('内地澳門短中期', [i for i in mainland if day_num(i['day']) <= 90 and i['day']]),
    ('内地澳門180日', [i for i in mainland if day_num(i['day']) == 180]),
    ('内地澳門365日', [i for i in mainland if day_num(i['day']) == 365]),
]
for name, items in slits:
    if items: groups[name] = items

# GID map (for detail HTML)
cat_gid = {
    '澳門':'900778','香港':'1021002','港澳':'1021004','内地澳門短中期':'1021006','内地澳門180日':'1021006',
    '内地澳門365日':'1021006','内地港澳':'1021191','日本':'1021010','日韓':'1021012','南韓':'1021011',
    '越南':'1021013','星馬泰及印尼':'1021016','泰國':'1021014','澳紐':'1021024','澳洲':'1021295',
    '歐洲':'1021023','美加墨':'1021030','阿聯酋':'1021031','法國':'1021033','美墨':'1021123',
    '南美':'1021124','東盟':'1021017','東南亞':'1021018','亞洲':'1021019','英法意等7國':'10200137',
    '巴基斯坦':'10200131','中東':'1021032','台灣':'10200137','其他':'1021033'
}

# Keep manual (CMHK) products
with open(base+'/products.json') as f: old = json.load(f)
manual = [p for p in old if not p.get('_src') or p.get('_src')!='cuniq']
for p in manual:
    for f in ['_src','_gid','_ppid','_oprice','hasVariants','variants']:
        p.pop(f, None)
pid = max(p['id'] for p in manual) + 1 if manual else 1

# Workbuddy index: (name_keyword, dayLabel) → price
kw_list = ['香港','澳門','日本','南韓','越南','泰國','美加墨','美墨','歐洲','澳紐','澳洲',
           '阿聯酋','沙特','巴基斯坦','法國','英法','星馬泰','馬來西亞','台灣','東盟','東南亞',
           '亞洲','南美','俄羅斯','内地','內地','日韓','意大利','UK']
def get_kw(name):
    for k in kw_list:
        if k in name: return k
    return ''

wb_idx = {}
for gid,entries in raw_all.items():
    for e in entries:
        if not e.get('prepaidCardId'): continue
        gn = (e.get('goodsName','') or '').replace(' ','').replace('　','')
        kn = get_kw(gn)
        wb_idx[(kn, e['dayLabel'])] = {'pid':e['prepaidCardId'], 'price':e['realPrice'], 'ori':e.get('oriPrice',0)}

# Build products
cctel = []
order = ['澳門','香港','港澳','内地澳門短中期','内地澳門180日','内地澳門365日','内地港澳',
    '日本','日韓','南韓','越南','星馬泰及印尼','泰國','澳紐','澳洲','歐洲','英法意等7國','法國',
    '美加墨','美墨','阿聯酋','巴基斯坦','中東','亞洲','東盟','東南亞','南美','台灣','其他']

for cat in order:
    items = groups.get(cat, [])
    if not items: continue
    gid = cat_gid.get(cat, '')
    d = details_map.get(gid, {})
    tc_d = d.get('tc',{}) or {}; en_d = d.get('en',{}) or {}

    base_img = tc_d.get('image','') or en_d.get('image_EN','') or ''
    if base_img and base_img.startswith('/'): base_img = 'https://www.cuniq.com'+base_img
    if not base_img:
        for it in items:
            ck = get_kw(it['cn'].replace(' ','').replace('　',''))
            wb_info = wb_idx.get((ck, it['day']))
            if wb_info:
                im = pid_img.get(str(wb_info['pid']), '')
                if im: base_img = im; break

    tc_h = clean(tc_d.get('productDetailHTML','') or '')
    en_h = clean(en_d.get('productDetailHTML_EN','') or tc_h)
    if not tc_h: tc_h = en_h
    if not en_h: en_h = tc_h

    en_base = en_d.get('prepaidCardName_EN','') or tc_d.get('prepaidCardName','') or items[0]['cn']
    en_base = re.sub(r'\s*\$[\d,]+.*$','', en_base).strip()
    area_str = area_from_html(tc_h) or area_from_html(en_h) or cat

    name_tc = items[0]['cn']
    name_en = en_base if en_base else items[0]['en']

    vlist = []
    for it in items:
        dl = it['day']; dal = it['data']
        if not dl: continue
        vd = day_num(dl)
        lb = dl + ' ' + dal if dal else dl

        # STRICT match: keyword + day must both match
        ck = get_kw(it['cn'].replace(' ','').replace('　',''))
        wb_info = wb_idx.get((ck, dl))
        rp = wb_info['price'] if wb_info else 0
        pid_w = wb_info['pid'] if wb_info else ''
        vi = pid_img.get(str(pid_w), '') if pid_w else base_img
        if not vi: vi = base_img

        v_tc = replace_days(tc_h, vd)
        v_en = replace_days(en_h, vd)

        vn_tc = '{} {}'.format(name_tc, lb)
        if rp > 0: vn_tc += ' HK${}'.format(rp)
        vn_cn = to_cn(vn_tc)
        vn_en = '{} {}'.format(en_base, lb)
        vn_en = re.sub(r'(\d+)日','\\1 Day',vn_en).replace('每日','Daily').strip().replace('（','(').replace('）',')')
        if rp > 0: vn_en += ' HK${}'.format(rp)

        ih = '<p><img src="{}" alt="{}" style="max-width:350px;width:100%;height:auto;"></p>\n'.format(vi, lb) if vi else ''
        d_tc = '<div class="product-desc-html">\n<div class="desc-section">\n{}{}\n</div>\n</div>'.format(ih, v_tc)
        d_en = '<div class="product-desc-html">\n<div class="desc-section">\n{}{}\n</div>\n</div>'.format(ih, v_en)

        vlist.append({"shortLabel":lb.strip(),"price":rp,"image":vi,
            "name":vn_tc,"nameCn":vn_cn,"nameEn":vn_en,
            "description":d_tc,"descriptionEn":d_en,"descriptionCn":d_tc,
            "prepaidCardId":pid_w, "originalPrice":wb_info['ori'] if wb_info else 0})

    if not vlist: continue
    vlist.sort(key=lambda v: v['price'] if v['price']>0 else 999999)
    prices = [v['price'] for v in vlist if v['price'] > 0]
    display_price = min(prices) if prices else 0

    sp = [area_str] if area_str else []
    if len(vlist) > 1 and display_price > 0: sp.append('{} plans'.format(len(vlist)))
    summary = ' | '.join(sp) if sp else name_tc

    cctel.append({"id":pid,"name":name_tc,"nameEn":name_en,"nameCn":to_cn(name_tc),
        "summary":summary[:200],"summaryEn":('{} | Multiple plans'.format(area_str))[:200] if len(vlist)>1 else summary[:200],
        "summaryCn":to_cn(summary)[:200],
        "description":vlist[0]['description'] if vlist else '',
        "descriptionEn":vlist[0]['descriptionEn'] if vlist else '',
        "descriptionCn":vlist[0]['description'] if vlist else '',
        "price":display_price,"image":base_img,"featured":False,"active":True,"createdAt":"2026-06-13T00:00:00.000Z",
        "hasVariants":len(vlist)>1,"variants":vlist if len(vlist)>1 else [],
        "_src":"cuniq","_gid":gid})
    pid += 1

all_p = manual + cctel; all_p.sort(key=lambda p: p['id'])
with open(base+'/products.json','w') as f:
    json.dump(all_p, f, indent=2, ensure_ascii=False)

print('Manual:{} CUniq:{} Total:{}'.format(len(manual), len(cctel), len(all_p)))
total_v = sum(len(p.get('variants',[])) for p in cctel)
prod_v = sum(1 for p in cctel if len(p.get('variants',[]))>1)
zero_p = sum(1 for p in cctel if p.get('price',0)==0)
no_img = sum(1 for p in all_p if not p.get('image'))
print('With variants: {}, Total options: {}, Zero price: {}, No img: {}'.format(prod_v, total_v, zero_p, no_img))

for p in cctel:
    vs = p.get('variants',[])
    vc = ' | {} SKUs'.format(len(vs)) if vs else ''
    pr = p.get('price', 0)
    zero = ' [0]' if pr == 0 else ''
    print('[{:2d}] {:.40s} HK${}{}{}'.format(p['id'], p['name'], pr, vc, zero))
    for v in vs[:3]:
        img = 'Y' if v.get('image') else 'N'
        print('    [{:25s}] HK${:<5d} img={}'.format(v['shortLabel'], v['price'], img))
    if len(vs) > 3: print('    ... +{} more'.format(len(vs)-3))
