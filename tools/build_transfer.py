# -*- coding: utf-8 -*-
"""2026학년도 후기 편입학 모집결과 자료 작성 (광주대학교, 정원외 외국인)."""
import warnings, datetime, re, shutil, os
warnings.filterwarnings('ignore')
import openpyxl
from copy import copy
from openpyxl.worksheet.cell_range import CellRange

BASE = r'C:\Users\user\Desktop\★국제협력처'
FORM = os.path.join(BASE, r'1. 학부\2026-2학기\편입학 모집결과 제출\(붙임1-별첨2) 2026학년도 편입학 모집결과 자료 작성서식.xlsx')
OUT  = os.path.join(BASE, r'1. 학부\2026-2학기\편입학 모집결과 제출\(붙임1-별첨2) 2026학년도 편입학 모집결과 자료(광주대학교).xlsx')
STAT = os.path.join(BASE, r'0. 유학생 통계\2026-2학기 학위 과정 유학생 현황\★20260911 기준 외국인 유학생 재학생 통계(학번 기재)_작업.xlsx')
PRIOR1 = os.path.join(BASE, r'0. 유학생 통계\강향옥\2026.8.26(강향옥).xlsx')
PRIOR2 = os.path.join(BASE, r'1. 학부\2026-2학기\합격자 발표(전산 입력)\전산입력\2차\(신입편입대학원)2026-2학기 중국 유학생 지원자 현황(2차).xlsx')

# ── 1. 등록 편입생 54명 (학적 시스템 9/11 기준) ────────────────────────────
wb = openpyxl.load_workbook(STAT, data_only=True)
roster = []
for r in wb['학위 재학생(신편입 포함) 명단'].iter_rows(min_row=2):
    v = [c.value for c in r]
    if v[1] == '학부' and str(v[14] or '').startswith('2026-09') and '편입' in str(v[13]):
        roster.append(dict(이름=str(v[7]).strip(), 학번=v[5], 학년=str(v[3]), 학과=v[4], 국적=v[11]))
assert len(roster) == 54, len(roster)

# ── 2. 전적대학(학교명·연제·졸업전공) 붙이기 ──────────────────────────────
SCHOOL = re.compile(r'(대학|학원|학교|전문)')
def scan(path, sheet, name_col):
    out = {}
    w = openpyxl.load_workbook(path, data_only=True)[sheet]
    for r in w.iter_rows(min_row=3):
        v = [c.value for c in r]
        nm = str(v[name_col] or '').strip()
        if not nm:
            continue
        school = yeon = major = None
        for i in range(9, min(len(v), 22)):
            x = v[i]
            if isinstance(x, str) and SCHOOL.search(x) and '/' not in x:
                school = x.strip()
                rest = [y for y in v[i+1:i+5]]
                for j, y in enumerate(rest):
                    if isinstance(y, (int, float)) and 1 <= y <= 4:
                        yeon = y
                        nxt = rest[j+1] if j+1 < len(rest) else None
                        if isinstance(nxt, str):
                            major = nxt.strip()
                        break
                break
        if school is None:
            # 협약대학(중경과창 등)은 학교명이 비고(B)열에 있고 전공만 기재돼 있다
            hint = v[1] if isinstance(v[1], str) else None
            for i in range(11, min(len(v), 18)):
                x = v[i]
                if isinstance(x, str) and not re.search(r'\d{4}|/|졸업', x) and len(x) <= 20:
                    major = x.strip()
                    break
            if hint and major:
                school = hint.strip() + '(협약)'
        if school and nm not in out:
            out[nm] = dict(전적대학=school, 연제=yeon, 전공=major)
    return out

prior = {}
prior.update(scan(PRIOR2, '2차 신입생명단', 3))
for k, v in scan(PRIOR1, '2026-2학기 신입생 명단', 3).items():
    prior.setdefault(k, v)

# 왕월은 동명이인(교환학생)이 있어 편입생 기록을 명시 지정
prior['왕월'] = dict(전적대학='치치하얼고등사범전문대학', 연제=3, 전공='수학')
# 중국 지원자 현황에 없는 2명 — 담당자 확인분(2026.9.22)
prior['다니야노바 굴누르'] = dict(전적대학='오시국립대학교', 연제=None, 전공='국제관계외교')
prior['레티옥'] = dict(전적대학='사이공문화예술관광대', 연제=None, 전공='한국어')

for s in roster:
    s.update(prior.get(s['이름'], dict(전적대학=None, 연제=None, 전공=None)))

# ── 3. 전적대학 계열 분류 (KEDI 7대계열) ──────────────────────────────────
# 전공을 하나씩 확인해 배정한다(키워드 추정 금지 — '기술'·'공정' 같은 말이 계열을 가르지 못한다)
MAJOR_GROUP = {
    '응용한국어': '어문', '한국어': '어문',
    '국제관계외교': '법정',
    '관관경영': '상경', '국제경제와무역': '상경', '마케팅': '상경', '온라인마케팅': '상경',
    '빅데이터와회계': '상경', 'BigDataandAccounting': '상경', '회계학': '상경',
    '현대물류관리': '상경', '스마트물류기술': '상경', '인력자원관리': '상경', '인적자원관리': '상경',
    '수학': '이학',
    '이동통신': '공학', '건축공학': '공학', '건축공정': '공학', '건축장식공정기술': '공학',
    '메카트로닉스기술': '공학', '비행물체스마트제조': '공학', '비행물체제조': '공학',
    '스마트제어기술': '공학', '시정공정기술': '공학',
    '컴퓨터': '공학', '컴퓨터공학': '공학', '컴퓨터공학과': '공학', '컴퓨터응용기술': '공학',
    'IntellectualProductsDevelopmentandApplication': '공학',
    '원예(조경)기술': '농수산해양기타',
    '간호': '의약간호', '임상의학': '의약간호',
    '미술': '예체능', '디지털매체': '예체능', 'E스포츠': '예체능',
    '체육교육': '사범', '아동학': '사범',
}
unknown = set()
for s in roster:
    key = (s['전공'] or '').replace(' ', '')
    s['전적계열'] = MAJOR_GROUP.get(key)
    if key and not s['전적계열']:
        unknown.add(s['전공'])
assert not unknown, f'분류표에 없는 전공: {unknown}'

# 모집학과 → 모집계열(2-4 행)
DEPT_GROUP = {
    '경영학과': '상경', '회계세무학과': '상경', '무역유통학과': '상경',
    '기계자동차공학부': '공학', '컴퓨터공학과': '공학',
    '호텔조리제과제빵학과': '이학',
    '뷰티미용학과': '예체능', '시각영상디자인학과': '예체능', '스포츠과학부': '예체능',
}

# ── 4. 검증 출력 ──────────────────────────────────────────────────────────
from collections import Counter, defaultdict
print('등록 편입생', len(roster), Counter(s['학년'] for s in roster))
by_dept = defaultdict(lambda: Counter())
for s in roster:
    by_dept[s['학과']][s['학년']] += 1
for d in sorted(by_dept):
    print(f"  {d}: 3학년 {by_dept[d]['3']}, 4학년 {by_dept[d]['4']}, 계 {sum(by_dept[d].values())}")
print('미분류:', [(s['이름'], s['학과'], s['전공']) for s in roster if not s['전적계열']])

# ── 5. 서식 채우기 ────────────────────────────────────────────────────────
wbf = openpyxl.load_workbook(FORM)
s22 = wbf['2-2.편입학 모집결과(정원외편입학)']

DEPTS = sorted(by_dept, key=lambda d: (-sum(by_dept[d].values()), d))
n = len(DEPTS)                       # 9개 학과
first, last_form = 6, 12             # 서식 기본 데이터 행
extra = n - (last_form - first + 1)  # 추가로 필요한 행 수 = 2

merges = [str(m) for m in s22.merged_cells.ranges]
if extra > 0:
    s22.insert_rows(last_form + 1, extra)
    for m in merges:                                   # 병합 영역 수동 보정
        rng = CellRange(m)
        if rng.min_row >= last_form + 1:
            s22.unmerge_cells(m)
            s22.merge_cells(start_row=rng.min_row + extra, end_row=rng.max_row + extra,
                            start_column=rng.min_col, end_column=rng.max_col)
    for r in range(last_form + 1, last_form + 1 + extra):   # 새 행 서식 = 6행 서식
        s22.row_dimensions[r].height = s22.row_dimensions[first].height
        for c in range(1, 49):
            src = s22.cell(row=first, column=c)
            dst = s22.cell(row=r, column=c)
            dst._style = copy(src._style)

last = first + n - 1
total_row = last + 1

COL = {'계획': {'2': 9, '3': 10, '4': 11},      # I~K 모집계획인원
       '지원': {'2': 12, '3': 13, '4': 14},     # L~N 지원자수
       '합격': {'2': 15, '3': 16, '4': 17},     # O~Q 합격현황
       '등록': {'2': 18, '3': 19, '4': 20}}     # R~T 총등록현황
for i, dept in enumerate(DEPTS):
    r = first + i
    cnt = by_dept[dept]
    s22.cell(row=r, column=1, value='광주대학교')
    s22.cell(row=r, column=2, value='광주')
    s22.cell(row=r, column=3, value='재외국민 및 외국인')
    s22.cell(row=r, column=4, value=dept)
    s22.cell(row=r, column=7, value=sum(cnt.values()))          # G 선발인원
    for blk in ('계획', '지원', '합격', '등록'):
        for yr in ('2', '3', '4'):
            if cnt.get(yr):
                s22.cell(row=r, column=COL[blk][yr], value=cnt[yr])
    s22.cell(row=r, column=28, value=sum(cnt.values()))         # AB 외국대학
    s22.cell(row=r, column=32, value=f'=SUM(U{r}:AE{r})')       # AF 출신대학 계
    s22.cell(row=r, column=39, value=f'=SUM(AG{r}:AL{r})')      # AM 일반대 소재지 소계
    s22.cell(row=r, column=46, value=f'=SUM(AN{r}:AS{r})')      # AT 전문대 소재지 소계
    s22.cell(row=r, column=47, value=f'=AM{r}=(U{r}+V{r})')
    s22.cell(row=r, column=48, value=f'=AT{r}=W{r}')

s22.cell(row=total_row, column=1, value='계')
for c in range(5, 47):                                          # E~AT 합계
    col = openpyxl.utils.get_column_letter(c)
    s22.cell(row=total_row, column=c, value=f'=SUM({col}{first}:{col}{last})')

# 2-3 전형방법
s23 = wbf['2-3.편입학전형방법']
vals = ['광주대학교', '광주', '정원외(학사제외)', 'X', 100, 0, 0, 0, 0, 0]
for j, v in enumerate(vals):
    s23.cell(row=6, column=j + 1, value=v)
s23.cell(row=6, column=11).value = None                         # K 기타
for r in (7, 8):                                                # 서식 예시 행 삭제
    for c in range(1, 12):
        s23.cell(row=r, column=c).value = None

# 2-4 계열별 모집현황 (기타 블록 33~44행, '대학' 열)
s24 = wbf['2-4.계열별모집현황']
ROW = {'어문': 33, '인문': 34, '법정': 35, '상경': 36, '사회': 37,
       '이학': 38, '공학': 39, '농수산해양기타': 40,
       '의약간호': 41, '예체능': 42, '사범': 43, '통합': 44}
CIDX = {'어문': 5, '인문': 8, '법정': 11, '상경': 14, '사회': 17,
        '이학': 20, '공학': 23, '농수산해양기타': 26,
        '의약간호': 29, '예체능': 32, '사범': 35, '통합': 38}   # '대학' 열
matrix = defaultdict(int)
for s in roster:
    if s['전적계열']:
        matrix[(DEPT_GROUP[s['학과']], s['전적계열'])] += 1
s24.cell(row=7, column=1, value='광주대학교')
for (모집, 전적), v in matrix.items():
    s24.cell(row=ROW[모집], column=CIDX[전적], value=v)
print('2-4 합계', sum(matrix.values()))

# ── 6. 제출 전 검산 ───────────────────────────────────────────────────────
# 학생별 근거는 별도 파일(전적대학·계열 매칭표)에 있으므로 제출본에는 시트를 두지 않는다.
assert sum(matrix.values()) == len(roster), f'2-4 총계 {sum(matrix.values())} ≠ {len(roster)}'
tot22 = sum(s22.cell(row=r, column=7).value or 0 for r in range(first, last + 1))
assert tot22 == len(roster), f'2-2 선발인원 합계 {tot22} ≠ {len(roster)}'
for yr, col in (('3', 19), ('4', 20)):                       # S·T 총등록현황
    got = sum(s22.cell(row=r, column=col).value or 0 for r in range(first, last + 1))
    want = sum(1 for s in roster if s['학년'] == yr)
    assert got == want, f'{yr}학년 등록 {got} ≠ {want}'
print(f'검산 OK — 2-2 선발 {tot22}명, 2-4 계열 배정 {sum(matrix.values())}명')

wbf.save(OUT)
print('저장:', OUT)
