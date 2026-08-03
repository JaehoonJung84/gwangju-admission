# -*- coding: utf-8 -*-
"""
2026-2학기 외국인 유학생 초대장(LETTER OF INVITATION) PDF 생성
- 초대장_docx생성.py 템플릿과 동일한 디자인(레터헤드·직인·녹색 톤)을 HTML로 재현
- 학생별 국문/영문 페이지 → Edge headless 로 PDF 2종 생성
  1) 초대장(한글+영문)_....pdf : 학생별 [국문, 영문] 페이지
  2) 초대장(영문)_....pdf     : 학생별 [영문] 페이지
실행:  python 초대장_pdf생성.py
"""
import os, base64, subprocess, tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO = os.path.join(BASE, '로고_국영문_full.png')
SEAL = os.path.join(BASE, '국제협력처장직인.png')
OUT_DIR = r'C:\Users\user\Desktop\★국제협력처\1. 학부\2026-2학기\초대장'

ISSUE_KO = '2026. 7. 27.'
ISSUE_EN = 'July 27, 2026'

STUDENTS = [
    dict(
        name_en='DANG THI DIEU LINH', name_ko='당티디에우린',
        birth_ko='1994. 10. 31.', birth_en='Oct. 31, 1994',
        nat_ko='베트남', nat_en='Vietnam',
        passport='E03959074',
        dept_ko='한국어문화교육콘텐츠학과', dept_en='Korean Language, Culture Education and Contents',
        prog_ko='박사과정 · 신입학', prog_en="Doctoral (Ph.D.) · Freshman",
        sem_ko='2026학년도 후기 (2026. 9.)', sem_en='Fall Semester 2026 (Sep. 2026)',
        period_ko='2026. 9. 1. ~ 2028. 8. 31.', period_en='Sep. 1, 2026 ~ Aug. 31, 2028',
    ),
    dict(
        name_en='LUU NHUE BANG', name_ko='류예방',
        birth_ko='1996. 9. 24.', birth_en='Sep. 24, 1996',
        nat_ko='베트남', nat_en='Vietnam',
        passport='C3574968',
        dept_ko='한국어문화교육콘텐츠학과', dept_en='Korean Language, Culture Education and Contents',
        prog_ko='박사과정 · 신입학', prog_en="Doctoral (Ph.D.) · Freshman",
        sem_ko='2026학년도 후기 (2026. 9.)', sem_en='Fall Semester 2026 (Sep. 2026)',
        period_ko='2026. 9. 1. ~ 2028. 8. 31.', period_en='Sep. 1, 2026 ~ Aug. 31, 2028',
    ),
]


def data_uri(path):
    with open(path, 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()

LOGO_URI = data_uri(LOGO)
SEAL_URI = data_uri(SEAL)

CSS = """
  @page { size: A4; margin: 0; }
  * { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  html,body { margin:0; padding:0; font-family:'Malgun Gothic','맑은 고딕',sans-serif; color:#1c1c1c; }
  .page { width:210mm; height:297mm; padding:16mm 19mm 14mm; position:relative; page-break-after:always; }
  .page:last-child { page-break-after:auto; }
  .head { display:flex; align-items:center; gap:14px; border-bottom:2px solid #1b6b3a; padding-bottom:8px; }
  .head .logo { width:64px; height:auto; flex:0 0 auto; }
  .head .org .ko { font-size:16px; font-weight:800; color:#1b6b3a; letter-spacing:0.5px; }
  .head .org .en { font-size:12.5px; font-weight:700; color:#20402b; margin-top:1px; }
  .head .org .addr { font-size:10px; color:#5a6b60; margin-top:4px; line-height:1.4; }
  .title { text-align:center; margin:52px 0 14px; }
  .title .main { font-size:29px; font-weight:800; color:#12331f; }
  .title .main.ko { letter-spacing:12px; }
  .title .main.en { letter-spacing:3px; }
  .title .sub { font-size:12px; font-weight:700; color:#7d947f; margin-top:4px; }
  .title .sub.ko { letter-spacing:8px; }
  .title .sub.en { letter-spacing:2px; }
  .dest { font-size:13.5px; font-weight:700; color:#20402b; margin-top:34px; }
  .body { font-size:13px; line-height:1.8; margin-top:20px; }
  .sec { font-size:13px; font-weight:800; color:#1b6b3a; margin:26px 0 8px; }
  table { width:100%; border-collapse:collapse; table-layout:fixed; }
  td { border:1px solid #cfe2d5; padding:10px 12px; font-size:12.5px; vertical-align:middle; word-break:keep-all; }
  td.k { background:#eaf4ec; color:#2c5a3c; font-weight:700; text-align:center; }
  .foot { position:absolute; left:0; right:0; bottom:30mm; text-align:center; }
  .foot .date { font-size:14px; color:#33463a; letter-spacing:1px; }
  .foot .sign-ko { font-size:25px; font-weight:800; letter-spacing:5px; color:#12331f; margin-top:16px; }
  .foot .sign-en { font-size:15px; font-weight:700; color:#33463a; margin-top:12px; }
  .page.pg-en .title { margin:36px 0 12px; }
  .page.pg-en .dest { margin-top:24px; }
  .page.pg-en .sec { margin:20px 0 7px; }
  .sealwrap { position:relative; letter-spacing:0; }
  .seal { position:absolute; left:54%; top:44%; transform:translate(-50%,-50%); width:56px; height:56px; object-fit:contain; opacity:0.92; }
"""


def head(addr):
    return f"""
  <div class='head'>
    <img class='logo' src='{LOGO_URI}' alt='광주대학교'/>
    <div class='org'>
      <div class='ko'>광주대학교 국제협력처</div>
      <div class='en'>Office of International Affairs, Gwangju University</div>
      <div class='addr'>{addr}</div>
    </div>
  </div>"""


def page_ko(s):
    return f"""
<div class='page'>
  {head('(61743) 전남광주통합특별시 남구 효덕로 277 · Tel. +82-62-670-2288 · Fax. +82-62-670-2733 · jhjung@gwangju.ac.kr')}
  <div class='title'>
    <div class='main ko'>초 대 장</div>
    <div class='sub en'>LETTER OF INVITATION</div>
  </div>
  <div class='dest'>주 베트남 대한민국대사관 영사과 귀중</div>
  <div class='body'>광주대학교는 아래 학생이 <b>2026학년도 후기(2학기) 외국인 특별전형</b>에 최종 합격하여 본교에서 정규 학업을
    수행할 예정임을 확인하며, 학업 수행을 위하여 아래와 같이 대한민국으로 정식 초청합니다.</div>

  <div class='sec'>■ 피초청인 (초청 대상 학생)</div>
  <table>
    <colgroup><col style='width:26mm'><col style='width:60mm'><col style='width:26mm'><col style='width:60mm'></colgroup>
    <tr><td class='k'>성명</td><td>{s['name_en']} ({s['name_ko']})</td><td class='k'>생년월일</td><td>{s['birth_ko']}</td></tr>
    <tr><td class='k'>국적</td><td>{s['nat_ko']}</td><td class='k'>여권번호</td><td>{s['passport']}</td></tr>
    <tr><td class='k'>지원학과</td><td>{s['dept_ko']}</td><td class='k'>과정 · 구분</td><td>{s['prog_ko']}</td></tr>
    <tr><td class='k'>입학학기</td><td>{s['sem_ko']}</td><td class='k'>초청기간</td><td>{s['period_ko']}</td></tr>
  </table>

  <div class='sec'>■ 초청인 (초청기관)</div>
  <table>
    <colgroup><col style='width:26mm'><col style='width:60mm'><col style='width:26mm'><col style='width:60mm'></colgroup>
    <tr><td class='k'>초청기관</td><td>광주대학교 (Gwangju University)</td><td class='k'>초청인</td><td>광주대학교 국제협력처장</td></tr>
    <tr><td class='k'>주소</td><td>(61743) 전남광주통합특별시 남구 효덕로 277</td><td class='k'>연락처</td><td>Tel. +82-62-670-2288 · jhjung@gwangju.ac.kr</td></tr>
  </table>

  <div class='body'>위 학생의 입국 목적은 본교에서의 정규 학업 수행에 한정되며, 본교는 학생의 입국 후 학업·출결 및
    체류자격 준수 여부를 성실히 관리·감독할 것을 확인합니다. 위 학생에 대한 사증 발급을 긍정적으로 검토하여
    주시기를 정중히 요청드립니다.</div>

  <div class='foot'>
    <div class='date'>{ISSUE_KO}</div>
    <div class='sign-ko'>광주대학교 국제협력처<span class='sealwrap'>장<img class='seal' src='{SEAL_URI}' alt='직인'/></span></div>
    <div class='sign-en'>Director of International Affairs, Gwangju University</div>
  </div>
</div>"""


def page_en(s):
    return f"""
<div class='page pg-en'>
  {head('277, Hyodeok-ro, Nam-gu, Gwangju 61743, Rep. of Korea · Tel. +82-62-670-2288 · jhjung@gwangju.ac.kr')}
  <div class='title'>
    <div class='main en'>LETTER OF INVITATION</div>
    <div class='sub ko'>초 대 장</div>
  </div>
  <div class='dest'>Consular Section, Embassy of the Republic of Korea in Vietnam</div>
  <div class='body'>On behalf of Gwangju University, Republic of Korea, we hereby confirm that the student listed below
    has been officially admitted through the <b>Special Admission for International Students, Fall Semester 2026</b>,
    and formally invite the student to the Republic of Korea for full-time academic study at our university.</div>

  <div class='sec'>■ Invitee (Student)</div>
  <table>
    <colgroup><col style='width:28mm'><col style='width:58mm'><col style='width:28mm'><col style='width:58mm'></colgroup>
    <tr><td class='k'>Name</td><td>{s['name_en']}</td><td class='k'>Date of Birth</td><td>{s['birth_en']}</td></tr>
    <tr><td class='k'>Nationality</td><td>{s['nat_en']}</td><td class='k'>Passport No.</td><td>{s['passport']}</td></tr>
    <tr><td class='k'>Department</td><td>{s['dept_en']}</td><td class='k'>Program</td><td>{s['prog_en']}</td></tr>
    <tr><td class='k'>Semester</td><td>{s['sem_en']}</td><td class='k'>Period</td><td>{s['period_en']}</td></tr>
  </table>

  <div class='sec'>■ Inviter (Host Institution)</div>
  <table>
    <colgroup><col style='width:28mm'><col style='width:58mm'><col style='width:28mm'><col style='width:58mm'></colgroup>
    <tr><td class='k'>Institution</td><td>Gwangju University</td><td class='k'>Inviter</td><td>Director of International Affairs, Gwangju University</td></tr>
    <tr><td class='k'>Address</td><td>277, Hyodeok-ro, Nam-gu, Gwangju 61743, Rep. of Korea</td><td class='k'>Contact</td><td>Tel. +82-62-670-2288 · jhjung@gwangju.ac.kr</td></tr>
  </table>

  <div class='body'>We confirm that the sole purpose of the student's entry into the Republic of Korea is to pursue
    full-time academic study at Gwangju University. The university will faithfully supervise the student's academic
    performance, attendance, and compliance with visa regulations throughout the period of study. We respectfully
    request your favorable consideration for the issuance of a visa for the above-mentioned student.</div>

  <div class='foot'>
    <div class='date'>{ISSUE_EN}</div>
    <div class='sign-ko'>광주대학교 국제협력처<span class='sealwrap'>장<img class='seal' src='{SEAL_URI}' alt='직인'/></span></div>
    <div class='sign-en'>Director of International Affairs, Gwangju University</div>
  </div>
</div>"""


def build_html(pages):
    return ("<!doctype html><html lang='ko'><head><meta charset='utf-8'><style>"
            + CSS + "</style></head><body>" + ''.join(pages) + "</body></html>")


def find_edge():
    for p in (r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
              r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'):
        if os.path.exists(p):
            return p
    raise SystemExit('Edge not found')


def html_to_pdf(html, out_pdf):
    edge = find_edge()
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html)
        tmp = f.name
    try:
        subprocess.run([edge, '--headless', '--disable-gpu', '--no-pdf-header-footer',
                        f'--print-to-pdf={out_pdf}', 'file:///' + tmp.replace('\\', '/')],
                       check=True, timeout=120)
    finally:
        os.unlink(tmp)
    print('생성:', out_pdf)


if __name__ == '__main__':
    os.makedirs(OUT_DIR, exist_ok=True)
    tag = '_'.join(s['name_en'].replace(' ', '_') for s in STUDENTS)

    pages_koen = []
    for s in STUDENTS:
        pages_koen += [page_ko(s), page_en(s)]
    html_to_pdf(build_html(pages_koen), os.path.join(OUT_DIR, f'초대장(한글+영문)_{tag}.pdf'))

    pages_en = [page_en(s) for s in STUDENTS]
    html_to_pdf(build_html(pages_en), os.path.join(OUT_DIR, f'초대장(영문)_{tag}.pdf'))
