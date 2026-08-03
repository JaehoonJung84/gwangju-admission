# -*- coding: utf-8 -*-
"""마크다운 작업일지를 노션 페이지로 업로드.
사용: python notion_upload.py <markdown파일> [페이지제목]
설정: C:\\projects\\tools\\autosave-config.json 의 notionToken / notionParentPageId
"""
import json, re, sys, urllib.request

CFG = r"C:\projects\tools\autosave-config.json"
API = "https://api.notion.com/v1/pages"

def rich(text):
    return [{"type": "text", "text": {"content": text[:2000]}}]

def md_to_blocks(md):
    blocks, lines, i = [], md.splitlines(), 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s or s in ("---", "***"):
            i += 1; continue
        if s.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i+1].strip()):
            rows = []
            rows.append([c.strip() for c in s.strip("|").split("|")])
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            width = max(len(r) for r in rows)
            table = {"object": "block", "type": "table", "table": {
                "table_width": width, "has_column_header": True, "has_row_header": False,
                "children": []}}
            for r in rows:
                cells = [rich(c) if c else rich(" ") for c in (r + [""] * (width - len(r)))[:width]]
                table["table"]["children"].append({"object": "block", "type": "table_row",
                                                   "table_row": {"cells": cells}})
            blocks.append(table)
            continue
        m = re.match(r"^(#{1,3})\s+(.*)", s)
        if m:
            lvl = min(len(m.group(1)), 3)
            blocks.append({"object": "block", "type": f"heading_{lvl}",
                           f"heading_{lvl}": {"rich_text": rich(m.group(2))}})
        elif s.startswith(">"):
            blocks.append({"object": "block", "type": "quote",
                           "quote": {"rich_text": rich(s.lstrip("> ").strip())}})
        elif re.match(r"^[-*]\s+", s) or re.match(r"^\d+\.\s+", s):
            txt = re.sub(r"^([-*]|\d+\.)\s+", "", s)
            blocks.append({"object": "block", "type": "bulleted_list_item",
                           "bulleted_list_item": {"rich_text": rich(txt)}})
        else:
            blocks.append({"object": "block", "type": "paragraph",
                           "paragraph": {"rich_text": rich(s)}})
        i += 1
    return blocks

def strip_md_inline(md):
    return re.sub(r"\*\*(.+?)\*\*|`(.+?)`", lambda m: m.group(1) or m.group(2), md)

def main():
    if len(sys.argv) < 2:
        print("usage: notion_upload.py <md파일> [제목]"); sys.exit(2)
    with open(CFG, encoding="utf-8") as f:
        cfg = json.load(f)
    with open(sys.argv[1], encoding="utf-8-sig") as f:
        md = strip_md_inline(f.read())
    title = sys.argv[2] if len(sys.argv) > 2 else None
    if not title:
        m = re.search(r"^#\s+(.+)$", md, re.M)
        title = m.group(1).strip() if m else sys.argv[1]
    blocks = md_to_blocks(md)[:100]  # Notion 1회 생성 한도
    body = {"parent": {"page_id": cfg["notionParentPageId"]},
            "properties": {"title": {"title": rich(title)}},
            "children": blocks}
    req = urllib.request.Request(API, data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {cfg['notionToken']}",
                 "Notion-Version": "2022-06-28", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            res = json.load(r)
        print("OK", res.get("url", ""))
    except urllib.error.HTTPError as e:
        print("FAIL", e.code, e.read().decode()[:300]); sys.exit(1)

if __name__ == "__main__":
    main()
