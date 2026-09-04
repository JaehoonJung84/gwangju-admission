# -*- coding: utf-8 -*-
"""HWP(OLE 복합문서) 쓰기 — 컨테이너는 Windows 자체 API 가 만들게 한다."""
import olefile, pythoncom, pywintypes, os
from win32com.storagecon import (STGM_CREATE, STGM_READWRITE, STGM_SHARE_EXCLUSIVE,
                                 STGM_WRITE, STGM_DIRECT)

MODE = STGM_CREATE | STGM_READWRITE | STGM_SHARE_EXCLUSIVE | STGM_DIRECT


def read_all(path):
    """원본의 모든 스트림을 {'경로': bytes} 로 읽고, 루트 CLSID 도 돌려준다."""
    ole = olefile.OleFileIO(path)
    out = {}
    for e in ole.listdir(streams=True, storages=False):
        out['/'.join(e)] = ole.openstream(e).read()
    clsid = ole.root.clsid
    ole.close()
    return out, clsid


def write_all(path, streams, clsid=None):
    """{'경로': bytes} 를 그대로 OLE 복합문서로 쓴다."""
    if os.path.exists(path):
        os.remove(path)
    root = pythoncom.StgCreateDocfile(path, MODE, 0)
    if clsid:
        try:
            root.SetClass(pywintypes.IID('{' + str(clsid) + '}'))
        except Exception:
            pass
    subs = {}

    def storage(parts):
        """중간 저장소(폴더)를 필요한 만큼 만든다."""
        cur, key = root, ''
        for p in parts:
            key = key + '/' + p
            if key not in subs:
                subs[key] = cur.CreateStorage(p, MODE, 0, 0)
            cur = subs[key]
        return cur

    for name in sorted(streams):
        parts = name.split('/')
        parent = storage(parts[:-1]) if len(parts) > 1 else root
        stm = parent.CreateStream(parts[-1], MODE, 0, 0)
        stm.Write(streams[name])
        stm.Commit(0)
        del stm
    for k in sorted(subs, reverse=True):
        subs[k].Commit(0)
    subs.clear()
    root.Commit(0)
    del root


def verify(path, expect):
    """다시 읽어 원하던 내용과 한 바이트도 다르지 않은지 확인한다."""
    got, _ = read_all(path)
    ok = set(got) == set(expect)
    diff = []
    if not ok:
        diff.append('스트림 목록 불일치: 없음=%s 남음=%s'
                    % (sorted(set(expect) - set(got)), sorted(set(got) - set(expect))))
    for k in sorted(set(got) & set(expect)):
        if got[k] != expect[k]:
            diff.append('내용 다름: %s (%d != %d)' % (k, len(got[k]), len(expect[k])))
    return (not diff), diff


if __name__ == '__main__':
    import sys
    src = sys.argv[1]
    dst = sys.argv[2]
    s, c = read_all(src)
    print('원본 스트림 %d개, 루트 CLSID %s' % (len(s), c))
    write_all(dst, s, c)
    ok, diff = verify(dst, s)
    print('복제 검증:', 'PASS — 모든 스트림 바이트 동일' if ok else 'FAIL')
    for d in diff:
        print('  ', d)
    print('원본 크기 %d / 새 파일 크기 %d' % (os.path.getsize(src), os.path.getsize(dst)))
