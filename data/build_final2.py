#!/usr/bin/env python3
"""
Final rebuild: Excel structure + workbuddy retail prices + per-category display SKUs
Rule 1: Product content = Excel structure
Rule 2: Prices = CUniq website retail (from workbuddy all_sku_complete)
Rule 3: No online data -> skip product
Rule 4: Specified display SKU per category
"""
import json
import re
import openpyxl
from collections import defaultdict

BASE = '/sessions/intelligent-upbeat-mccarthy/mnt/hkcctel/data'

# ---- LOAD SOURCES ----
with open(BASE + '/all_sku_complete.json') as f:
    all_sku = json.load(f)
with open(BASE + '/cuniq_details_full.json') as f:
    details_list = json.load(f)

details = {str(d['goodsId']): d for d in details_list}

# Build filler: (goodsId, day) -> {pid, price, img, data}
filler = {}
for g in all_sku:
    gid = str(g['goodsId'])
    for s in g['skus']:
        filler[(gid, str(s['day']))] = s

# ---- HELPERS ----
def clean_html(h):
    if not h:
        return ''
    return re.sub(r'<!DOCTYPE[^>]*>|<html[^>]*>|</html>|<head>[\s\S]*?</head>|<body[^>]*>|</body>', '', h).strip()

def find_days(text):
    s = set()
    for m in re.finditer(r'(?<!\d)(\d+)[日日]', text):
        s.add(int(m.group(1)))
    for m in re.finditer(r'(?<!\d)(\d+)[- ]?Day(?!\w)', text, re.IGNORECASE):
        s.add(int(m.group(1)))
    return s

def replace_days(html, vn):
    if not html or not vn:
        return html
    vs = str(vn)
    r = html
    for fv in sorted(find_days(html), reverse=True):
        if fv == vn:
            continue
        r = re.sub(rf'(?<!\d){fv}日(?!\d)', vs + '日', r)
        r = re.sub(rf'(?<!\d){fv}-Day(?!\w)', vs + '-Day', r, re.IGNORECASE)
        r = re.sub(rf'(?<!\d){fv}\s+Day(?!\w)', vs + ' Day', r, re.IGNORECASE)
    return r

def extract_gb(data_label):
    """Extract GB number from data label like '5GB', '5+3 GB', 'Daily 3GB', '8+3GB FUP'"""
    if not data_label: return 0
    # Handle "X+Y" → take Y (the upgraded amount)
    m = re.search(r'(\d+)\+(\d+)', data_label)
    if m: return int(m.group(1)) + int(m.group(2))
    m = re.search(r'Daily\s+(\d+)', data_label)
    if m: return int(m.group(1))
    m = re.search(r'(\d+)\s*GB', data_label)
    if m: return int(m.group(1))
    return 0

def replace_gb(html, data_label):
    """Replace GB amounts in detail HTML to match the variant"""
    if not html or not data_label: return html
    target_gb = extract_gb(data_label)
    if target_gb <= 0: return html

    # Find all GB numbers in the HTML
    found_gb = set()
    for m in re.finditer(r'(?<!\d)(\d+)\s*GB(?!\d)', html, re.IGNORECASE):
        found_gb.add(int(m.group(1)))
    for m in re.finditer(r'(?<!\d)(\d+)\s*gb(?!\d)', html, re.IGNORECASE):
        found_gb.add(int(m.group(1)))

    if not found_gb: return html

    r = html
    for fg in sorted(found_gb, reverse=True):
        if fg == target_gb: continue
        r = re.sub(rf'(?<!\d){fg}\s*GB(?!\d)', str(target_gb) + 'GB', r, re.IGNORECASE)
        r = re.sub(rf'(?<!\d){fg}\s*gb(?!\d)', str(target_gb) + 'GB', r, re.IGNORECASE)
    return r

# TC->SC map
tc_sc = {
    '網': '网', '數': '数', '據': '据', '電': '电', '聯': '联', '動': '动', '號': '号', '萬': '万',
    '與': '与', '為': '为', '專': '专', '業': '业', '態': '态', '係': '系', '認': '认', '證': '证',
    '資': '资', '訊': '讯', '導': '导', '爾': '尔', '羅': '罗', '門': '门', '線': '线', '開': '开',
    '時': '时', '間': '间', '頭': '头', '機': '机', '話': '话', '務': '务', '設': '设', '計': '计',
    '劃': '划', '總': '总', '產': '产', '單': '单', '價': '价', '買': '买', '賣': '卖', '購': '购',
    '選': '选', '擇': '择', '點': '点', '變': '变', '從': '从', '馬': '马', '亞': '亚', '歐': '欧',
    '優': '优', '內': '内', '後': '后', '對': '对', '應': '应', '達': '达', '過': '过', '還': '还',
    '這': '这', '東': '东', '華': '华', '國': '国', '臺': '台', '韓': '韩', '會': '会', '區': '区',
    '條': '条', '級': '级', '經': '经', '結': '结', '統': '统', '續': '续', '護': '护', '謝': '谢',
    '識': '识', '讀': '读', '歷': '历', '預': '预', '領': '领', '飛': '飞', '紐': '纽', '泰': '泰',
    '英': '英', '法': '法', '墨': '墨', '阿': '阿', '酋': '酋', '埃': '埃', '及': '及', '巴': '巴',
    '基': '基', '坦': '坦', '哈': '哈', '薩': '萨', '克': '克', '土': '土', '耳': '耳', '其': '其',
    '美': '美', '加': '加', '南': '南', '洲': '洲', '沙': '沙', '特': '特', '拉': '拉', '伯': '伯',
    '越': '越', '印': '印', '尼': '尼', '菲': '菲', '賓': '宾', '柬': '柬', '埔': '埔', '寨': '寨',
    '老': '老', '撾': '挝', '群': '群', '維': '维', '義': '义', '豐': '丰', '書': '书', '寫': '写',
    '滿': '满', '邊': '边', '遠': '远', '際': '际'
}

def to_cn(t):
    if not t:
        return ''
    r = ''.join(tc_sc.get(ch, ch) for ch in t)
    fixes = [('南韩', '韩国'), ('新马泰', '新马泰'),
             ('哈萨克', '哈萨克斯坦'),
             ('流动数据', '移动数据'),
             ('话音', '语音'), ('短讯', '短信'),
             ('公平使用数据', '公平使用流量'),
             ('启用', '激活'), ('增值', '充值'),
             ('通话/上网卡', '通话上网卡')]
    for o, n in fixes:
        r = r.replace(o, n)
    return r

def day_num(dl):
    return int(''.join(c for c in dl if c.isdigit()) or '0')

# ---- EXCEL CLASSIFICATION ----
def classify(row):
    cn = str(row[4] or '') + str(row[5] or '')
    en = str(row[6] or '')
    n = cn + en
    if '韩' in cn:
        return 'kr'
    if '日韩' in n:
        return 'jpk'
    if '日本' in n:
        return 'jp'
    if '越' in cn:
        return 'vn'
    if '星马泰' in n:
        return 'smi'
    if '泰国' in n:
        return 'th'
    if '阿联酋' in n:
        return 'ae'
    if '沙特' in cn:
        return 'me'
    if '美加墨' in n:
        return 'ucm'
    if '美墨' in n or '美國及墨西哥' in n:
        return 'umx'
    if '澳紐' in n:
        return 'anz'
    if '澳洲' in n:
        return 'au'
    if '巴基斯坦' in n:
        return 'pk'
    if '英法' in n:
        return 'e7'
    if '歐洲' in n:
        return 'eu'
    if '法國' in n:
        return 'fr'
    if '東盟' in n:
        return 'an'
    if '東南亞' in n:
        return 'sea'
    if '亞洲' in n:
        return 'asia'
    if '香港' in cn and '澳門' in cn and ('内地' in cn or '內地' in cn):
        return 'cnhkmo'
    if ('内地' in cn or '內地' in cn) and '澳門' in cn:
        return 'cnmo'
    if '香港' in cn and '澳門' in cn:
        return 'hkmo'
    if '香港' in cn:
        return 'hk'
    if '澳門' in cn:
        return 'mo'
    if '馬來西亞' in n:
        return 'smi'
    return 'other'


wb = openpyxl.load_workbook('/sessions/intelligent-upbeat-mccarthy/mnt/uploads/灿成價格表20260401.xlsx')
ws = wb.active

# ---- BUILD EXCEL STRUCTURE ----
groups = defaultdict(list)
for row in ws.iter_rows(min_row=2, values_only=True):
    cd = row[0]
    if not cd:
        continue
    cat = classify(row)
    cn = str(row[4] or row[5] or '')
    en = str(row[6] or '')
    ct = str(row[5] or '')
    dm_ = re.search(r'(\d+)日', cn + ct)
    dl = dm_.group(1) + '日' if dm_ else ''
    gm_ = re.search(r'(\d+\s*GB|Daily\s*\d+\s*GB)', cn + en + ct)
    dal = gm_.group(1) if gm_ else ''
    cnc = re.sub(r'\s*\$[\d,]+.*', '', cn).strip()
    cnc = re.sub(r'^5G\s*', '', cnc).strip()
    groups[cat].append({'code': str(cd), 'cn': cnc, 'en': en, 'day': dl, 'data': dal})

# Split cnmo
cnmo = groups.pop('cnmo', [])
for nm, it in [('cnmo_s', [i for i in cnmo if day_num(i['day']) <= 90 and i['day']]),
               ('cnmo_180', [i for i in cnmo if day_num(i['day']) == 180]),
               ('cnmo_365', [i for i in cnmo if day_num(i['day']) == 365])]:
    if it:
        groups[nm] = it

# ---- CATEGORY METADATA ----
cat_gid = {
    'mo': '900778', 'hk': '1021002', 'hkmo': '1021004',
    'cnmo_s': '1021006', 'cnmo_180': '1021006', 'cnmo_365': '1021006',
    'cnhkmo': '1021191', 'jp': '1021010', 'jpk': '1021012', 'kr': '1021011',
    'vn': '1021013', 'smi': '1021016', 'th': '1021014', 'anz': '1021024',
    'au': '1021295', 'eu': '1021023', 'ucm': '1021030', 'ae': '1021031',
    'fr': '1021033', 'umx': '1021123', 'pk': '10200131', 'me': '1021032',
    'an': '1021017', 'sea': '1021018', 'asia': '1021019', 'e7': '10200137'
}

# Chinese names
cat_name = {
    'mo': '澳門上網卡',
    'hk': '香港上網卡',
    'hkmo': '香港及澳門上網卡',
    'cnmo_s': '中國內地及澳門上網卡',
    'cnmo_180': '中國內地及澳門180日上網卡',
    'cnmo_365': '中國內地及澳門365日上網卡',
    'cnhkmo': '內地、香港及澳門365日上網卡',
    'jp': '日本多日上網卡',
    'jpk': '日韓多日通話/上網卡',
    'kr': '南韓多日通話/上網卡',
    'vn': '越南多日上網卡',
    'smi': '星馬泰及印尼多日通話/上網卡',
    'th': '泰國上網卡',
    'anz': '澳紐多日通話/上網卡',
    'au': '澳洲上網卡',
    'eu': '歐洲多日上網卡',
    'ucm': '美加墨上網卡',
    'ae': '阿聯酋上網卡',
    'fr': '法國上網卡',
    'umx': '美墨上網卡',
    'pk': '中南亞多地上網卡',
    'me': '中東上網卡',
    'an': '東盟上網卡',
    'sea': '東南亞上網卡',
    'asia': '亞洲多日上網卡',
    'e7': '英法意等7國上網卡'
}

# English names
en_name = {
    'mo': 'Macau Prepaid SIM', 'hk': 'Hong Kong Prepaid SIM', 'hkmo': 'HK & Macau Prepaid SIM',
    'cnmo_s': 'China Mainland & Macau SIM', 'cnmo_180': 'China Mainland & Macau 180-Day SIM',
    'cnmo_365': 'China Mainland & Macau 365-Day SIM', 'cnhkmo': 'Mainland, HK & Macau 365-Day SIM',
    'jp': 'Japan Prepaid SIM', 'jpk': 'Japan & Korea Voice/Data SIM',
    'kr': 'South Korea Voice/Data SIM', 'vn': 'Vietnam Prepaid SIM',
    'smi': 'Singapore, Malaysia, Thailand & Indonesia SIM', 'th': 'Thailand Prepaid SIM',
    'anz': 'Australia & NZ Voice/Data SIM', 'au': 'Australia 90-Day SIM', 'eu': 'Europe Prepaid SIM',
    'ucm': 'USA, Canada & Mexico SIM', 'ae': 'UAE Prepaid SIM', 'fr': 'France Voice/Data SIM',
    'umx': 'USA & Mexico SIM', 'pk': 'Central & South Asia SIM', 'me': 'Middle East SIM',
    'an': 'ASEAN 8-Day SIM', 'sea': 'SE Asia 8-Day SIM', 'asia': 'Asia Multi-Day SIM',
    'e7': 'UK, France & Italy SIM'
}

# ---- DISPLAY SKU RULES (Rule 4) ----
# (category, day, data_label) -> what shows as main SKU
display_sku = {
    'cnmo_s': ('2日', '2GB'),
    'cnmo_180': ('180日', '21GB+3GB'),
    'cnmo_365': ('365日', '15GB'),
    'smi': ('5日', 'Daily 3GB'),
    'mo': ('1日', 'Daily 3GB'),
    'anz': ('10日', '12GB'),
    'eu': ('10日', None),  # no 10-day in data, fallback
    'th': ('5日', '5GB'),
    'kr': ('5日', 'Daily 3GB'),
    'hk': None,   # default = lowest day
    'hkmo': None,  # default = lowest day
    'jp': ('8日', '11GB'),
    'vn': ('8日', '15GB'),
    'ucm': ('30日', 'Daily 1GB'),
}

# ---- KEEP MANUAL CMHK ----
with open(BASE + '/products.json') as f:
    old = json.load(f)
manual = [p for p in old if not p.get('_src') or p.get('_src') != 'cuniq']
for p in manual:
    for fl in ['_src', '_gid', '_ppid', '_oprice', 'hasVariants', 'variants']:
        p.pop(fl, None)
next_pid = max(p['id'] for p in manual) + 1 if manual else 1

# ---- BUILD ----
cctel = []
order = ['mo', 'hk', 'hkmo', 'cnmo_s', 'cnmo_180', 'cnmo_365', 'cnhkmo',
         'jp', 'jpk', 'kr', 'vn', 'smi', 'th', 'anz', 'au', 'eu', 'e7', 'fr',
         'ucm', 'umx', 'ae', 'pk', 'me', 'asia', 'an', 'sea']

for cat in order:
    items = groups.get(cat, [])
    if not items:
        continue

    gid = cat_gid.get(cat, '')
    d = details.get(gid, {})
    td = d.get('tc', {}) or {}
    ed = d.get('en', {}) or {}

    th = clean_html(td.get('productDetailHTML', '') or '')
    eh = clean_html(ed.get('productDetailHTML_EN', '') or '')
    if not th:
        th = eh
    if not eh:
        eh = th

    ntc = cat_name.get(cat, cat)
    nen = en_name.get(cat, cat)
    ncn = to_cn(ntc)

    # ---- BUILD VARIANTS FROM FILLER ----
    vlist = []
    filler_days_available = {}

    # First, collect all days available in filler for this gid
    all_matched = []
    for it in items:
        dl = it['day']
        dal = it['data']
        if not dl:
            continue
        vd = day_num(dl)
        sku = filler.get((str(gid), str(vd)))
        if sku and sku.get('price', 0) > 0:
            filler_days_available[vd] = sku
            all_matched.append({'it': it, 'sku': sku, 'vd': vd})

    # Rule 3: No online data -> skip product
    if not all_matched:
        print('SKIP [{}] {} - no online data'.format(cat, ntc))
        continue

    # Build variant list from matched data
    for am in all_matched:
        it = am['it']
        sku = am['sku']
        vd = am['vd']
        dl = it['day']
        dal = it['data']

        lb = dl + ' ' + dal if dal else dl
        rp = sku['price']
        vi = sku.get('img', '')
        pw = sku['pcid']

        vt = replace_days(th, vd)
        ve = replace_days(eh, vd)

        vnt = '{} {} HK${}'.format(ntc, lb, rp)
        vnc = to_cn(vnt)
        vne = '{} {} HK${}'.format(nen, dl.replace('日', ' Day'), rp)

        ih = ''
        if vi:
            ih = '<p><img src="{}" alt="{}" style="max-width:350px;width:100%;height:auto;"></p>\n'.format(vi, lb)

        dtc = '<div class="product-desc-html">\n<div class="desc-section">\n{}{}\n</div>\n</div>'.format(ih, vt)
        den = '<div class="product-desc-html">\n<div class="desc-section">\n{}{}\n</div>\n</div>'.format(ih, ve)

        vlist.append({
            "shortLabel": lb.strip(), "price": rp, "image": vi,
            "name": vnt, "nameCn": vnc, "nameEn": vne,
            "description": dtc, "descriptionEn": den, "descriptionCn": dtc,
            "prepaidCardId": pw, "originalPrice": 0
        })

    vlist.sort(key=lambda v: v['price'])

    # ---- DETERMINE DISPLAY PRICE (Rule 4) ----
    ds_rule = display_sku.get(cat)
    display_variant_idx = 0  # default = first (lowest price) variant

    if ds_rule:
        target_day, target_data = ds_rule
        for idx, v in enumerate(vlist):
            sl = v['shortLabel']
            if target_day in sl:
                if target_data is None or target_data in sl:
                    display_variant_idx = idx
                    break

    display_var = vlist[display_variant_idx]

    # ---- PRODUCT ENTRY ----
    summaries = []
    if len(vlist) > 1:
        summaries.append(str(len(vlist)) + ' plans')
    summary = ' | '.join(summaries) if summaries else ''

    en_summary = 'Multiple plans' if len(vlist) > 1 else ''

    cctel.append({
        "id": next_pid, "name": ntc, "nameEn": nen, "nameCn": ncn,
        "summary": summary, "summaryEn": en_summary,
        "summaryCn": to_cn(summary),
        "description": display_var['description'],
        "descriptionEn": display_var['descriptionEn'],
        "descriptionCn": display_var['description'],
        "price": display_var['price'],
        "image": display_var['image'],
        "featured": False, "active": True,
        "createdAt": "2026-06-13T00:00:00.000Z",
        "hasVariants": len(vlist) > 1,
        "variants": vlist if len(vlist) > 1 else [],
        "_src": "cuniq", "_gid": str(gid)
    })
    next_pid += 1

    # Print
    vl = len(vlist)
    print('[{}] {:.35s} HK${} | {} SKUs | display: {}'.format(
        next_pid - 1, ntc, display_var['price'], vl, display_var['shortLabel']))
    for v in vlist:
        mark = ' <-- display' if v == display_var else ''
        print('    {:20s} HK${:<6d}{}'.format(v['shortLabel'], v['price'], mark))

# ---- MERGE & SAVE ----
all_p = manual + cctel
all_p.sort(key=lambda p: p['id'])
with open(BASE + '/products.json', 'w') as f:
    json.dump(all_p, f, indent=2, ensure_ascii=False)

print('')
print('Total: {} products ({} manual + {} CUniq)'.format(len(all_p), len(manual), len(cctel)))
print('Total SKUs: {}'.format(sum(len(p.get('variants', [])) for p in cctel)))": display_var['image'],
        "featured": False, "active": True,
        "createdAt": "2026-06-13T00:00:00.000Z",
        "hasVariants": len(vlist) > 1,
        "variants": vlist if len(vlist) > 1 else [],
        "_src": "cuniq", "_gid": str(gid)
    })
    next_pid += 1

    # Print
    vl = len(vlist)
    print('[{}] {:.35s} HK${} | {} SKUs | display: {}'.format(
        next_pid - 1, ntc, display_var['price'], vl, display_var['shortLabel']))
    for v in vlist:
        mark = ' <-- display' if v == display_var else ''
        print('    {:20s} HK${:<6d}{}'.format(v['shortLabel'], v['price'], mark))

# ---- MERGE & SAVE ----
all_p = manual + cctel
all_p.sort(key=lambda p: p['id'])
with open(BASE + '/products.json', 'w') as f:
    json.dump(all_p, f, indent=2, ensure_ascii=False)

print('\nTotal: {} products ({} manual + {} CUniq)'.format(len(all_p), len(manual), len(cctel)))
print('Total SKUs: {}'.format(sum(len(p.get('variants', [])) for p in cctel)))
