# -*- coding: utf-8 -*-
"""HWPX 양식 -> DOCX 재조판 (치수·글꼴·줄높이를 한컴 조판 결과 그대로 옮긴다)."""
import sys, os, xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding="utf-8")
from docx import Document
from docx.shared import Twips, Emu, Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HP="http://www.hancom.co.kr/hwpml/2011/paragraph"; HH="http://www.hancom.co.kr/hwpml/2011/head"
HC="http://www.hancom.co.kr/hwpml/2011/core"; NS={"hp":HP,"hh":HH,"hc":HC}
SRC="x"
U2TW=lambda u:int(round(float(u)/5.0))      # HWPUNIT -> twips
U2PT=lambda u:float(u)/100.0

head=ET.parse(os.path.join(SRC,"Contents/header.xml")).getroot()
fonts={ff.get("lang"):{f.get("id"):f.get("face") for f in ff.findall("hh:font",NS)}
       for ff in head.iter("{%s}fontface"%HH)}
charPr={}
for cp in head.iter("{%s}charPr"%HH):
    fr=cp.find("hh:fontRef",NS); rt=cp.find("hh:ratio",NS); sp=cp.find("hh:spacing",NS)
    ul=cp.find("hh:underline",NS)
    charPr[cp.get("id")]=dict(size=U2PT(cp.get("height")), color=cp.get("textColor") or "#000000",
        hangul=fonts["HANGUL"].get(fr.get("hangul")), latin=fonts["LATIN"].get(fr.get("latin")),
        bold=cp.find("hh:bold",NS) is not None, italic=cp.find("hh:italic",NS) is not None,
        underline=(ul is not None and ul.get("type") not in (None,"NONE")),
        ratio=int(rt.get("hangul")) if rt is not None else 100,
        spacing=int(sp.get("hangul")) if sp is not None else 0)
paraPr={}
for pp in head.iter("{%s}paraPr"%HH):
    al=pp.find("hh:align",NS); ls=pp.find("hh:lineSpacing",NS); mg=pp.find("hh:margin",NS)
    def mv(n):
        if mg is None: return 0
        e=mg.find("hc:%s"%n,NS); return int(e.get("value")) if e is not None else 0
    paraPr[pp.get("id")]=dict(align=al.get("horizontal") if al is not None else "JUSTIFY",
        line=(ls.get("type"),int(ls.get("value"))) if ls is not None else ("PERCENT",160),
        left=mv("left"), right=mv("right"), indent=mv("intent"))
MM2SZ=lambda mm:max(2,int(round(float(mm)/0.352778*8)))
borderFill={}
for bf in head.iter("{%s}borderFill"%HH):
    d={}
    for side,tag in (("left","leftBorder"),("right","rightBorder"),("top","topBorder"),("bottom","bottomBorder")):
        e=bf.find("hh:%s"%tag,NS)
        if e is not None: d[side]=(e.get("type"),MM2SZ(e.get("width").replace(" mm","")),e.get("color"))
    wb=bf.find(".//hc:winBrush",NS); fill=None
    if wb is not None:
        fc=wb.get("faceColor")
        if fc and fc.lower() not in ("none","#ffffffff"): fill=fc.lstrip("#")
    borderFill[bf.get("id")]=dict(sides=d,fill=fill)

sec=ET.parse(os.path.join(SRC,"Contents/section0.xml")).getroot()
pagePr=sec.find(".//hp:pagePr",NS); mar=pagePr.find("hp:margin",NS)

doc=Document()
st=doc.styles["Normal"]; st.font.name="맑은 고딕"; st.font.size=Pt(10)
st.element.rPr.rFonts.set(qn("w:eastAsia"),"맑은 고딕")
st.paragraph_format.space_before=Pt(0); st.paragraph_format.space_after=Pt(0)
s0=doc.sections[0]
s0.page_width=Twips(U2TW(pagePr.get("width"))); s0.page_height=Twips(U2TW(pagePr.get("height")))
s0.left_margin=Twips(U2TW(mar.get("left"))); s0.right_margin=Twips(U2TW(mar.get("right")))
s0.top_margin=Twips(U2TW(mar.get("top")))
# 아래 여백은 표 뒤 마감 문단(1pt)이 들어갈 만큼만 줄인다 — 인쇄 결과는 그대로
s0.bottom_margin=Twips(max(0,U2TW(mar.get("bottom"))-60))
s0.header_distance=Twips(0); s0.footer_distance=Twips(0)

def el(tag,**a):
    e=OxmlElement(tag)
    for k,v in a.items(): e.set(qn(k),str(v))
    return e
ORDER=["w:cnfStyle","w:tcW","w:gridSpan","w:hMerge","w:vMerge","w:tcBorders","w:shd","w:noWrap",
       "w:tcMar","w:textDirection","w:tcFitText","w:vAlign","w:hideMark"]
def tc_put(tc,e):
    tcPr=tc.get_or_add_tcPr(); tag="w:"+e.tag.split("}")[1]
    for old in tcPr.findall(qn(tag)): tcPr.remove(old)
    idx=ORDER.index(tag) if tag in ORDER else len(ORDER); pos=len(tcPr)
    for i,ch in enumerate(tcPr):
        ct="w:"+ch.tag.split("}")[1]
        if (ORDER.index(ct) if ct in ORDER else len(ORDER))>idx: pos=i; break
    tcPr.insert(pos,e)
ALIGN={"LEFT":"left","CENTER":"center","RIGHT":"right","JUSTIFY":"both","DISTRIBUTE":"distribute","DIVISION":"distribute"}

def seg_height(hp_p):
    """한컴이 실제로 흘린 줄 높이(pt)와 줄 수 — <hp:lineseg> 기준"""
    segs=[sg for sg in hp_p.findall("hp:linesegarray/hp:lineseg",NS)]
    if not segs: return None,0
    hs=[(int(sg.get("vertsize"))+int(sg.get("spacing")))/100.0 for sg in segs]
    return max(hs), len(segs)

def style_par(p,ppid,line_pt,fallback_size):
    pr=paraPr.get(ppid,dict(align="JUSTIFY",line=("PERCENT",160),left=0,right=0,indent=0))
    pPr=p._p.get_or_add_pPr()
    pPr.append(el("w:jc",**{"w:val":ALIGN.get(pr["align"],"left")}))
    if line_pt is None: line_pt=fallback_size*pr["line"][1]/100.0
    pPr.append(el("w:spacing",**{"w:before":"0","w:after":"0",
                                 "w:line":str(int(round(line_pt*20))),"w:lineRule":"exact"}))
    if pr["left"] or pr["right"] or pr["indent"]:
        a={"w:left":str(U2TW(pr["left"])),"w:right":str(U2TW(pr["right"]))}
        a["w:firstLine" if pr["indent"]>=0 else "w:hanging"]=str(U2TW(abs(pr["indent"])))
        pPr.append(el("w:ind",**a))
    for t in ("w:autoSpaceDE","w:autoSpaceDN","w:snapToGrid"):   # 한글·숫자 사이 자동 간격 끄기
        pPr.append(el(t,**{"w:val":"0"}))
    return p

def add_run(p,text,cpid):
    c=charPr.get(cpid) or charPr["0"]
    r=p.add_run(text)
    r.font.size=Pt(c["size"]); r.bold=c["bold"]; r.italic=c["italic"]
    if c["underline"]: r.underline=True
    if c["color"] and c["color"]!="#000000":
        try: r.font.color.rgb=RGBColor.from_string(c["color"].lstrip("#"))
        except Exception: pass
    rPr=r._r.get_or_add_rPr(); rf=rPr.find(qn("w:rFonts"))
    if rf is None: rf=el("w:rFonts"); rPr.insert(0,rf)
    for k in ("w:ascii","w:hAnsi","w:cs"): rf.set(qn(k),c["latin"] or c["hangul"])
    rf.set(qn("w:eastAsia"),c["hangul"] or c["latin"])
    if c["spacing"]: rPr.append(el("w:spacing",**{"w:val":str(int(round(c["size"]*c["spacing"]/100.0*20)))}))
    if c["ratio"]!=100: rPr.append(el("w:w",**{"w:val":str(c["ratio"])}))
    return r

def cell_style(tc,bfid,cm,valign):
    bf=borderFill.get(bfid)
    if bf:
        bd=el("w:tcBorders")
        for side in ("top","left","bottom","right"):
            info=bf["sides"].get(side); e=el("w:"+side)
            if not info or info[0]=="NONE": e.set(qn("w:val"),"nil")
            else:
                e.set(qn("w:val"),"single"); e.set(qn("w:sz"),str(info[1]))
                e.set(qn("w:space"),"0"); e.set(qn("w:color"),info[2].lstrip("#"))
            bd.append(e)
        tc_put(tc,bd)
        if bf["fill"]: tc_put(tc,el("w:shd",**{"w:val":"clear","w:color":"auto","w:fill":bf["fill"]}))
    m=el("w:tcMar")        # 좌우 여백만 살리고 위아래는 0 (워드는 위아래 여백이 줄 높이를 밀어낸다)
    m.append(el("w:top",**{"w:w":"0","w:type":"dxa"}))
    m.append(el("w:left",**{"w:w":str(U2TW(cm[0])),"w:type":"dxa"}))
    m.append(el("w:bottom",**{"w:w":"0","w:type":"dxa"}))
    m.append(el("w:right",**{"w:w":str(U2TW(cm[1])),"w:type":"dxa"}))
    tc_put(tc,m)
    tc_put(tc,el("w:vAlign",**{"w:val":{"TOP":"top","CENTER":"center","BOTTOM":"bottom"}.get(valign,"center")}))

from PIL import ImageFont
FONTFILE={"맑은 고딕":"malgun.ttf","굴림":"gulim.ttc","굴림체":"gulim.ttc","바탕":"batang.ttc",
          "돋움":"gulim.ttc","한컴바탕":"batang.ttc","Times New Roman":"times.ttf"}
_fc={}
def text_width(txt,face,size,bold=False):
    """글월 폭(pt) — 표 앞 공백만큼 안쪽 표를 들여쓰기 위해 쓴다"""
    fn=FONTFILE.get(face,"malgun.ttf")
    if bold and fn=="malgun.ttf": fn="malgunbd.ttf"
    key=(fn,)
    if key not in _fc:
        try: _fc[key]=ImageFont.truetype(os.path.join(r"C:\Windows\Fonts",fn),400)
        except Exception: _fc[key]=ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf",400)
    return _fc[key].getlength(txt)/400.0*size

IMGDIR=os.path.join(SRC,"BinData")
def image_path(idref):
    for n in os.listdir(IMGDIR):
        if n.split(".")[0].lower()==idref.lower(): return os.path.join(IMGDIR,n)

def grid_of(tbl):
    rows=tbl.findall("hp:tr",NS); ncol=int(tbl.get("colCnt")); nrow=int(tbl.get("rowCnt"))
    colw={}; rowh={}; spans=[]
    for tr in rows:
        for tc in tr.findall("hp:tc",NS):
            a=tc.find("hp:cellAddr",NS); sp=tc.find("hp:cellSpan",NS); sz=tc.find("hp:cellSz",NS)
            c0,r0=int(a.get("colAddr")),int(a.get("rowAddr")); cs,rs=int(sp.get("colSpan")),int(sp.get("rowSpan"))
            if cs==1: colw.setdefault(c0,int(sz.get("width")))
            else: spans.append((c0,cs,int(sz.get("width"))))
            if rs==1: rowh[r0]=max(rowh.get(r0,0),int(sz.get("height")))
    for _ in range(ncol+2):
        moved=False
        for c0,cs,w in spans:
            miss=[c for c in range(c0,c0+cs) if c not in colw]
            if len(miss)==1:
                colw[miss[0]]=w-sum(colw[c] for c in range(c0,c0+cs) if c in colw); moved=True
        if not moved: break
    assert len(colw)==ncol, [c for c in range(ncol) if c not in colw]
    return nrow,ncol,[colw[c] for c in range(ncol)],[rowh.get(r,0) for r in range(nrow)]

def tbl_height(tbl):
    _,_,_,rowh=grid_of(tbl); return sum(rowh)

def cell_plan(sub, inner_h):
    """문단별 (줄높이, 줄수) 를 구하고, 칸을 넘치면 빈 문단을 줄여 맞춘다."""
    plan=[]
    for hp_p in sub.findall("hp:p",NS):
        tbls=[t for t in hp_p.iter("{%s}tbl"%HP)]
        if tbls:
            th=sum(tbl_height(t) for t in tbls)/100.0
            segs=hp_p.findall("hp:linesegarray/hp:lineseg",NS)
            occupied=sum((int(sg.get("vertsize"))+int(sg.get("spacing")))/100.0 for sg in segs) or th
            plan.append(dict(p=hp_p,kind="tbl",h=th,n=1,empty=False,gap=max(0.0,occupied-th)))
            continue
        lh,n=seg_height(hp_p)
        runs=hp_p.findall("hp:run",NS)
        sizes=[charPr.get(r.get("charPrIDRef"),charPr["0"])["size"] for r in runs] or [10.0]
        has_text=any("".join(t.itertext()).strip() for t in hp_p.findall(".//hp:t",NS)) \
                 or hp_p.findall(".//hp:checkBtn",NS) or hp_p.findall(".//hp:pic",NS)
        if lh is None:
            pr=paraPr.get(hp_p.get("paraPrIDRef")); lh=max(sizes)*(pr["line"][1] if pr else 160)/100.0; n=1
        plan.append(dict(p=hp_p,kind="p",h=lh,n=max(n,1),empty=not has_text,size=max(sizes)))
    total=sum(x["h"]*x["n"] for x in plan)
    over=total-inner_h
    if over>0.05:
        spare=[x for x in plan if x["kind"]=="p" and x["empty"]]
        room=sum(max(0.0,x["h"]-2.0) for x in spare)
        if room>0:
            k=min(1.0,over/room)
            for x in spare: x["h"]=x["h"]-(x["h"]-2.0)*k
    return plan

def build_table(tbl,container,indent_pt=0.0):
    nrow,ncol,colw,rowh=grid_of(tbl)
    t=container.add_table(rows=nrow,cols=ncol); t.autofit=False
    tblPr=t._tbl.tblPr
    tblPr.append(el("w:tblLayout",**{"w:type":"fixed"}))
    tblPr.append(el("w:tblW",**{"w:w":str(U2TW(sum(colw))),"w:type":"dxa"}))
    # 표 왼쪽 선이 쪽 여백선에 맞게 (워드는 셀 왼쪽 여백만큼 표를 왼쪽으로 민다)
    first_left=28
    for tr0 in tbl.findall("hp:tr",NS)[:1]:
        cm0=tr0.find("hp:tc/hp:cellMargin",NS)
        if cm0 is not None: first_left=U2TW(cm0.get("left"))
    tblPr.append(el("w:tblInd",**{"w:w":str(first_left+int(round(indent_pt*20))),"w:type":"dxa"}))
    for gc,w in zip(t._tbl.find(qn("w:tblGrid")).findall(qn("w:gridCol")),colw):
        gc.set(qn("w:w"),str(U2TW(w)))
    need={}
    for tr0 in tbl.findall("hp:tr",NS):
        for tc0 in tr0.findall("hp:tc",NS):
            a0=tc0.find("hp:cellAddr",NS); sp0=tc0.find("hp:cellSpan",NS)
            r0=int(a0.get("rowAddr")); rs0=int(sp0.get("rowSpan"))
            h=sum(x["h"]*x["n"] for x in cell_plan(tc0.find("hp:subList",NS), sum(rowh[r0:r0+rs0])/100.0))
            if rs0==1: need[r0]=max(need.get(r0,0.0),h)
    for r,tr in enumerate(t.rows):
        trPr=tr._tr.get_or_add_trPr()
        rule="exact"   # 한컴 조판 높이 그대로 (atLeast 로 두면 워드가 행을 늘려 2쪽이 된다)
        trPr.append(el("w:trHeight",**{"w:val":str(U2TW(rowh[r])),"w:hRule":rule}))
        trPr.append(el("w:cantSplit"))
    for tr in tbl.findall("hp:tr",NS):
        for tc in tr.findall("hp:tc",NS):
            a=tc.find("hp:cellAddr",NS); sp=tc.find("hp:cellSpan",NS)
            r0,c0=int(a.get("rowAddr")),int(a.get("colAddr")); rs,cs=int(sp.get("rowSpan")),int(sp.get("colSpan"))
            cell=t.cell(r0,c0)
            if rs>1 or cs>1: cell=cell.merge(t.cell(r0+rs-1,c0+cs-1))
            sub=tc.find("hp:subList",NS); cm=tc.find("hp:cellMargin",NS)
            cmv=(cm.get("left"),cm.get("right")) if cm is not None else ("141","141")
            cell_style(cell._tc,tc.get("borderFillIDRef"),cmv,sub.get("vertAlign"))
            tc_put(cell._tc,el("w:tcW",**{"w:w":str(U2TW(int(tc.find("hp:cellSz",NS).get("width")))),"w:type":"dxa"}))
            inner_h=sum(rowh[r0:r0+rs])/100.0
            fill_cell(cell,sub,inner_h)
    return t

def fill_cell(cell,sub,inner_h):
    for p in list(cell.paragraphs): p._p.getparent().remove(p._p)
    plan=cell_plan(sub,inner_h); last_tbl=False
    for item in plan:
        hp_p=item["p"]
        if item["kind"]=="tbl":
            lead=0.0
            for run in hp_p.findall("hp:run",NS):
                done=False
                for node in run:
                    tag=node.tag.split("}")[1]
                    if tag=="tbl": done=True; break
                    if tag=="t":
                        c=charPr.get(run.get("charPrIDRef"),charPr["0"])
                        lead+=text_width("".join(node.itertext()),c["hangul"] or "맑은 고딕",c["size"],c["bold"])
                if done: break
            for it in [x for x in hp_p.iter("{%s}tbl"%HP)]:
                build_table(it,cell,lead)
                # python-docx 가 표 뒤에 붙이는 빈 문단을 없앤다 (한 줄씩 밀려 내려간다)
                tail_ps=[p for p in cell.paragraphs if not p.text.strip()]
                if tail_ps and tail_ps[-1]._p is cell._tc[-1]:
                    cell._tc.remove(tail_ps[-1]._p)
                last_tbl=True
            gap=item.get("gap",0.0)
            if gap>0.3:     # 한컴에서 표가 든 문단은 표 아래에 글줄 하나만큼 자리를 더 쓴다
                g=cell.add_paragraph()
                g._p.get_or_add_pPr().append(el("w:spacing",**{"w:before":"0","w:after":"0",
                                                "w:line":str(int(round(gap*20))),"w:lineRule":"exact"}))
                g.add_run("").font.size=Pt(1)
                last_tbl=False
            continue
        p=cell.add_paragraph(); style_par(p,hp_p.get("paraPrIDRef"),item["h"],item["size"])
        only_chk=bool(hp_p.findall(".//hp:checkBtn",NS)) and not any(
            "".join(t.itertext()).strip() for t in hp_p.findall(".//hp:t",NS))
        if only_chk:
            jc=p._p.get_or_add_pPr().find(qn("w:jc"))
            if jc is not None: jc.set(qn("w:val"),"left")
        last_tbl=False
        for run in hp_p.findall("hp:run",NS):
            cpid=run.get("charPrIDRef")
            for node in run:
                tag=node.tag.split("}")[1]
                if tag=="t":
                    txt="".join(node.itertext())
                    if txt: add_run(p,txt,cpid)
                elif tag=="checkBtn": add_run(p,"□ "+(node.get("caption") or ""),cpid)
                elif tag=="pic":
                    sz=node.find("hp:curSz",NS); img=node.find(".//hc:img",NS)
                    path=image_path(img.get("binaryItemIDRef"))
                    if path: p.add_run().add_picture(path,width=Emu(int(sz.get("width"))*127),
                                                     height=Emu(int(sz.get("height"))*127))
    if last_tbl:
        p=cell.add_paragraph()
        p._p.get_or_add_pPr().append(el("w:spacing",**{"w:before":"0","w:after":"0","w:line":"20","w:lineRule":"exact"}))
        p.add_run("").font.size=Pt(1)

OUT=sys.argv[1] if len(sys.argv)>1 else "wonseo.docx"
build_table([t for t in sec.iter("{%s}tbl"%HP)][0], doc)
if doc.paragraphs and not doc.paragraphs[0].text.strip():
    doc.paragraphs[0]._p.getparent().remove(doc.paragraphs[0]._p)
tail=doc.add_paragraph()
tail._p.get_or_add_pPr().append(el("w:spacing",**{"w:before":"0","w:after":"0","w:line":"20","w:lineRule":"exact"}))
tail.add_run("").font.size=Pt(1)
doc.save(OUT); print("저장:",OUT,os.path.getsize(OUT))
