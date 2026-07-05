#!/usr/bin/env python3
import json, re
base = '/sessions/intelligent-upbeat-mccarthy/mnt/hkcctel/data'

with open(base+'/all_sku_complete.json') as f: all_sku = json.load(f)
with open(base+'/cuniq_details_full.json') as f: dl = json.load(f)
dm = {str(d['goodsId']): d for d in dl}

def ch(h):
    if not h: return ''
    return re.sub(r'<!DOCTYPE[^>]*>|<html[^>]*>|</html>|<head>[\s\S]*?</head>|<body[^>]*>|</body>','',h).strip()

def fd_all(text):
    s = set()
    for m in re.finditer(r'(?<!\d)(\d+)[日]',text): s.add(int(m.group(1)))
    for m in re.finditer(r'(?<!\d)(\d+)[- ]?Day(?!\w)',text,re.IGNORECASE): s.add(int(m.group(1)))
    return s

def rd(html, vn):
    if not html or not vn: return html
    vs = str(vn); r = html
    for fv in sorted(fd_all(html), reverse=True):
        if fv == vn: continue
        r = re.sub(rf'(?<!\d){fv}日(?!\d)', vs+'日', r)
        r = re.sub(rf'(?<!\d){fv}-Day(?!\w)', vs+'-Day', r, re.IGNORECASE)
        r = re.sub(rf'(?<!\d){fv}\s+Day(?!\w)', vs+' Day', r, re.IGNORECASE)
    return r

ts = {}
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
for a, b in pairs: ts[a] = b

def t2c(t):
    if not t: return ''
    r = ''.join(ts.get(ch, ch) for ch in t)
    for o, n in [('南韩','韩国'),('新马泰','新马泰'),('哈萨克','哈萨克斯坦'),
        ('流动数据','移动数据'),('话音','语音'),('短讯','短信'),
        ('公平使用数据','公平使用流量'),('启用','激活'),('增值','充值'),
        ('通话/上网卡','通话上网卡')]:
        r = r.replace(o, n)
    return r

# Keep manual CMHK products
with open(base+'/products.json') as f: old = json.load(f)
manual = [p for p in old if not p.get('_src') or p.get('_src') != 'cuniq']
for p in manual:
    for fl in ['_src', '_gid', '_ppid', '_oprice', 'hasVariants', 'variants']:
        p.pop(fl, None)
pid = max(p['id'] for p in manual) + 1 if manual else 1

cctel = []
for g in all_sku:
    gid = g['goodsId']; skus = g['skus']
    if not skus: continue

    d = dm.get(str(gid), {})
    td = d.get('tc', {}) or {}
    ed = d.get('en', {}) or {}
    th = ch(td.get('productDetailHTML', '') or '')
    eh = ch(ed.get('productDetailHTML_EN', '') or th)
    if not th: th = eh
    if not eh: eh = th

    ename = d.get('goodsName', '') or td.get('prepaidCardName', '') or str(gid)
    en_base = ed.get('prepaidCardName_EN', '') or td.get('prepaidCardName', '') or ename
    en_base = re.sub(r'\s*\$[\d,]+.*$', '', en_base).strip()

    # Deduplicate by (day, price)
    seen = {}
    for s in skus:
        k = (s['day'], s['price'])
        if k not in seen: seen[k] = s

    vlist = []
    for s in seen.values():
        dl = s['day'] + '日'
        vd = int(s['day'])
        lb = dl
        da = str(s.get('data', ''))
        if da and da != 'None': lb = dl + ' ' + da

        vt = rd(th, vd)
        ve = rd(eh, vd)
        vi = s.get('img', '')

        vnt = '{} {} HK${}'.format(ename, lb, s['price'])
        vnc = t2c(vnt)
        vne = '{} {} HK${}'.format(en_base, dl.replace('日', ' Day'), s['price'])

        ih = ''
        if vi:
            ih = '<p><img src="{}" alt="{}" style="max-width:350px;width:100%;height:auto;"></p>\n'.format(vi, lb)

        dtc = '<div class="product-desc-html">\n<div class="desc-section">\n{}{}\n</div>\n</div>'.format(ih, vt)
        den = '<div class="product-desc-html">\n<div class="desc-section">\n{}{}\n</div>\n</div>'.format(ih, ve)

        vlist.append({
            "shortLabel": lb.strip(), "price": s['price'], "image": vi,
            "name": vnt, "nameCn": vnc, "nameEn": vne,
            "description": dtc, "descriptionEn": den, "descriptionCn": dtc,
            "prepaidCardId": s['pcid'], "originalPrice": s.get('oriPrice', 0)
        })

    vlist.sort(key=lambda v: v['price'])
    prices = [v['price'] for v in vlist]
    dp = min(prices) if prices else 0

    ntc = ename if ename else 'P-{}'.format(gid)
    nen = en_base if en_base else ntc

    sp = [str(len(vlist)) + ' plans'] if len(vlist) > 1 else []
    summary = ' | '.join(sp) if sp else ntc

    p = {
        "id": pid, "name": ntc, "nameEn": nen, "nameCn": t2c(ntc),
        "summary": summary[:200], "summaryEn": ('Multiple plans')[:200] if len(vlist) > 1 else summary[:200],
        "summaryCn": t2c(summary)[:200],
        "description": vlist[0]['description'] if vlist else '',
        "descriptionEn": vlist[0]['descriptionEn'] if vlist else '',
        "descriptionCn": vlist[0]['description'] if vlist else '',
        "price": dp, "image": vlist[0]['image'] if vlist else '',
        "featured": False, "active": True, "createdAt": "2026-06-13T00:00:00.000Z",
        "hasVariants": len(vlist) > 1, "variants": vlist if len(vlist) > 1 else [],
        "_src": "cuniq", "_gid": str(gid)
    }
    cctel.append(p)
    pid += 1

all_p = manual + cctel
all_p.sort(key=lambda p: p['id'])
with open(base + '/products.json', 'w') as f:
    json.dump(all_p, f, indent=2, ensure_ascii=False)

print('Manual:{} CUniq:{} Total:{}'.format(len(manual), len(cctel), len(all_p)))
tv = sum(len(p.get('variants', [])) for p in cctel)
print('Total variants: {}'.format(tv))
for p in cctel:
    vs = p.get('variants', [])
    vl = len(vs)
    print('[{}] gid={} {:.35s} HK${} | {} SKUs'.format(p['id'], p['_gid'], p['name'], p['price'], vl))
    for v in vs[:4]:
        print('    {:15s} HK${} pid={}'.format(v['shortLabel'], v['price'], v['prepaidCardId']))
    if vl > 4:
        print('    ... +{} more'.format(vl - 4))
