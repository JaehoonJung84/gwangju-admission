# -*- coding: utf-8 -*-
"""마크다운 작업일지를 노션 페이지로 업로드 (갱신 지원).

사용: python notion_upload.py <markdown파일> [페이지제목]
설정: C:\\projects\\tools\\autosave-config.json 의 notionToken / notionParentPageId

동작:
- 파일 내용 해시가 지난 업로드와 같으면 SKIP (아무것도 안 함) → 매시간 호출해도 안전
- 바뀌었으면 기존 페이지를 보관(archive)하고 새 페이지를 만들어 교체 (제목·위치 동일)
- 페이지 id·해시는 notion_pages.json 에 기억. 모르는 페이지는 제목 검색으로 찾아 보관 처리
- 100블록 초과分은 append API로 나눠 올림 (긴 일지도 전체 업로드)
"""
import hashlib
import json
import os
import re
import sys
import urllib.request

CFG = r"C:\projects\tools\autosave-config.json"
STATE = r"C:\projects\tools\notion_pages.json"
API = "https://api.notion.com/v1"


def _req(method, path, token, body=None):
    req = urllib.request.Request(
        API + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {token}",
                 "Notion-Version": "2022-06-28", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


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


def load_state():
    if os.path.exists(STATE):
        try:
            with open(STATE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_state(st):
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)


def archive(token, page_id):
    try:
        _req("PATCH", f"/pages/{page_id}", token, {"archived": True})
        return True
    except Exception:
        return False


def find_pages_by_title(token, title, parent_id):
    """제목이 같고 부모가 같은 기존 페이지를 찾는다 (상태 파일에 없던 옛 업로드 정리용)."""
    try:
        res = _req("POST", "/search", token,
                   {"query": title, "filter": {"value": "page", "property": "object"}})
    except Exception:
        return []
    out = []
    pid_norm = parent_id.replace("-", "")
    for r in res.get("results", []):
        try:
            t = "".join(x["plain_text"] for x in r["properties"]["title"]["title"])
            par = (r.get("parent") or {}).get("page_id", "").replace("-", "")
            if t.strip() == title.strip() and par == pid_norm and not r.get("archived"):
                out.append(r["id"])
        except Exception:
            continue
    return out


def main():
    if len(sys.argv) < 2:
        print("usage: notion_upload.py <md파일> [제목]"); sys.exit(2)
    with open(CFG, encoding="utf-8") as f:
        cfg = json.load(f)
    token, parent = cfg["notionToken"], cfg["notionParentPageId"]
    path = sys.argv[1]
    with open(path, encoding="utf-8-sig") as f:
        raw = f.read()
    md = strip_md_inline(raw)
    title = sys.argv[2] if len(sys.argv) > 2 else None
    if not title:
        m = re.search(r"^#\s+(.+)$", md, re.M)
        title = m.group(1).strip() if m else os.path.basename(path)

    key = os.path.basename(path)
    digest = hashlib.md5(raw.encode("utf-8")).hexdigest()
    st = load_state()
    ent = st.get(key) or {}
    if ent.get("hash") == digest:
        print("SKIP unchanged"); return

    # 이전 버전 페이지 보관 처리 (알고 있는 id + 제목 검색으로 찾은 것)
    olds = set()
    if ent.get("page_id"):
        olds.add(ent["page_id"])
    olds.update(find_pages_by_title(token, title, parent))
    for pid in olds:
        archive(token, pid)

    blocks = md_to_blocks(md)
    body = {"parent": {"page_id": parent},
            "properties": {"title": {"title": rich(title)}},
            "children": blocks[:100]}
    try:
        res = _req("POST", "/pages", token, body)
        page_id = res["id"]
        rest = blocks[100:]
        while rest:
            _req("PATCH", f"/blocks/{page_id}/children", token, {"children": rest[:100]})
            rest = rest[100:]
        st[key] = {"page_id": page_id, "hash": digest, "title": title}
        save_state(st)
        print("OK", res.get("url", ""))
    except urllib.error.HTTPError as e:
        print("FAIL", e.code, e.read().decode()[:300]); sys.exit(1)


if __name__ == "__main__":
    main()
