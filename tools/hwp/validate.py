# -*- coding: utf-8 -*-
"""만든 HWP 가 한글에서 열릴 수 있는 상태인지 전수 검사한다.
지난번엔 '내 파서로 읽힌다'만 보고 통과시켰다가 한글이 거부했다. 이번엔 규격을 직접 본다."""
import struct, sys, collections
import hwpread as H

PATH = sys.argv[1] if len(sys.argv) > 1 else '시나리오.hwp'
TPL = r'C:/Users/user/Desktop/★국제협력처/0. 회의/2. 학처장회의/교무위원회의(20260812)-국제협력처.hwp'

bad = 0


def err(msg):
    global bad
    bad += 1
    print('  ★ ' + msg)


doc, secs, comp = H.sections(PATH)
tdoc, tsecs, _ = H.sections(TPL)
sec = secs[0]

print('① 문단마다 선언값과 실제 레코드가 맞는가')
paras = []
cur = None
for tag, lvl, p, ho, po in H.records(sec):
    if tag == H.T_PARA_HEADER:
        cur = {'h': p, 'lvl': lvl, 't': None, 'cs': None, 'ls': None, 'ctrl': 0}
        paras.append(cur)
    elif cur is None:
        continue
    elif tag == H.T_PARA_TEXT:
        cur['t'] = p
    elif tag == H.T_PARA_CHAR_SHAPE:
        cur['cs'] = p
    elif tag == H.T_PARA_LINE_SEG:
        cur['ls'] = p
    elif tag == H.T_CTRL_HEADER:
        cur['ctrl'] += 1

for i, r in enumerate(paras):
    if len(r['h']) != 24:
        err('%d문단 PARA_HEADER 크기 %d (24여야 함)' % (i, len(r['h'])))
        continue
    nCh = struct.unpack_from('<I', r['h'], 0)[0]
    last = bool(nCh & 0x80000000)
    nCh &= 0x7FFFFFFF
    cmask = struct.unpack_from('<I', r['h'], 4)[0]
    ps, st, ct, nCS, nRT, nLS = struct.unpack_from('<HBBHHH', r['h'], 8)
    tl = len(r['t']) // 2 if r['t'] is not None else 0
    if r['t'] is not None and nCh != tl:
        err('%d문단 nChars=%d 인데 글자 %d개' % (i, nCh, tl))
    if r['t'] is None and nCh not in (0, 1):
        err('%d문단 PARA_TEXT 없는데 nChars=%d' % (i, nCh))
    if nCS != (len(r['cs']) // 8 if r['cs'] else 0):
        err('%d문단 nCharShapes 불일치' % i)
    if nLS != (len(r['ls']) // 36 if r['ls'] else 0):
        err('%d문단 nLineSegs 불일치' % i)
    if last and i != len(paras) - 1:
        err('%d문단에 마지막 표시가 붙어 있음' % i)
    if i == len(paras) - 1 and not last:
        err('마지막 문단에 마지막 표시가 없음')
    # 조종문자와 controlMask 가 어긋나면 한글이 손상으로 본다
    has_ctrl = False
    if r['t'] is not None:
        k, n = 0, tl
        while k < n:
            c = struct.unpack_from('<H', r['t'], k * 2)[0]
            if c in H.CH_INLINE or c in H.CH_EXT:
                has_ctrl = True
                k += 8
            else:
                # 0x0A(문단 안 줄바꿈) 같은 글자조종문자도 controlMask 비트를 세운다
                if c < 32 and c != 13:
                    has_ctrl = True
                k += 1
    if has_ctrl and cmask == 0:
        err('%d문단 조종문자가 있는데 controlMask=0' % i)
    if (not has_ctrl) and cmask != 0:
        err('%d문단 controlMask=0x%X 인데 조종문자가 없음' % (i, cmask))
    if r['ctrl'] and not has_ctrl:
        err('%d문단 CTRL_HEADER %d개인데 글월에 조종문자 없음' % (i, r['ctrl']))
print('   문단 %d개 검사' % len(paras))

print('② 첫 문단(구역 정의)이 양식과 구조적으로 같은가')
t0 = next(p for tag, l, p, _, _ in H.records(tsecs[0]) if tag == H.T_PARA_TEXT)
m0 = paras[0]['t']
tu = [struct.unpack_from('<H', t0, k * 2)[0] for k in range(len(t0) // 2)]
mu = [struct.unpack_from('<H', m0, k * 2)[0] for k in range(len(m0) // 2)]
if len(tu) != len(mu):
    err('첫 문단 글자 수가 다름 %d vs %d' % (len(tu), len(mu)))
else:
    kk = 0
    while kk < len(tu):
        c = tu[kk]
        if c in H.CH_INLINE or c in H.CH_EXT:
            if tu[kk:kk + 8] != mu[kk:kk + 8]:
                err('첫 문단 조종문자(%d번째)가 바뀜' % kk)
            kk += 8
        else:
            kk += 1
    print('   조종문자 그대로 · 글자 수 동일')

print('③ 본문에 몰래 들어간 제어문자가 있는가 (줄바꿈이 글에 섞이면 깨진다)')
found = collections.Counter()
for i, r in enumerate(paras[1:], 1):
    if r['t'] is None:
        continue
    n = len(r['t']) // 2
    for k in range(n - 1):                     # 마지막 문단끝 표시는 제외
        c = struct.unpack_from('<H', r['t'], k * 2)[0]
        if c < 32 and c not in (10, 13):      # 10=문단 안 줄바꿈, 13=문단 끝 — 정상
            found[c] += 1
            if sum(found.values()) <= 5:
                err('%d문단 %d번째에 제어문자 0x%02X' % (i, k, c))
print('   ' + ('없음' if not found else '★ %s' % dict(found)))

print('④ 서식 번호가 실제로 있는가')
cnt = collections.Counter(t for t, _, _, _, _ in H.records(doc))
idm = next(p for t, l, p, _, _ in H.records(doc) if t == H.TAG + 1)
v = struct.unpack_from('<18i', idm, 0)
if v[9] != cnt[H.T_CHAR_SHAPE]:
    err('글자모양 선언 %d / 실제 %d' % (v[9], cnt[H.T_CHAR_SHAPE]))
if v[13] != cnt[H.TAG + 9]:
    err('문단모양 선언 %d / 실제 %d' % (v[13], cnt[H.TAG + 9]))
if v[14] != cnt[H.TAG + 10]:
    err('스타일 선언 %d / 실제 %d' % (v[14], cnt[H.TAG + 10]))
psu = set(); csu = set()
for r in paras:
    psu.add(struct.unpack_from('<H', r['h'], 8)[0])
    if r['cs']:
        for k in range(len(r['cs']) // 8):
            csu.add(struct.unpack_from('<II', r['cs'], k * 8)[1])
if max(psu) >= cnt[H.TAG + 9]:
    err('없는 문단모양 %d 사용' % max(psu))
if max(csu) >= cnt[H.T_CHAR_SHAPE]:
    err('없는 글자모양 %d 사용' % max(csu))
print('   문단모양 %s · 글자모양 %s' % (sorted(psu), sorted(csu)))

print('⑤ 레코드 경계가 정확히 맞아떨어지는가')
tot = 0
for tag, lvl, p, ho, po in H.records(sec):
    tot = po + len(p)
if tot != len(sec):
    err('구역 끝이 %d 인데 자료는 %d 바이트' % (tot, len(sec)))
else:
    print('   구역0 %d 바이트 정확히 소진' % tot)

print()
print('문제 %d건' % bad if bad else '문제 없음 — 한글에서 열릴 수 있는 상태')
