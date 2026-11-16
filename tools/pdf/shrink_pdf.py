import fitz, os, sys, glob, io
from PIL import Image

SRC = r"C:\Users\user\Desktop\★국제협력처\8. 모집요강\2027학년도 모집요강\최종본\디자인 후"

def collect_display(doc):
    """max display size (pt) per image xref"""
    disp = {}
    for p in doc:
        for info in p.get_image_info(xrefs=True):
            xr = info["xref"]
            if xr <= 0: continue
            r = fitz.Rect(info["bbox"])
            w, h = disp.get(xr, (0, 0))
            disp[xr] = (max(w, r.width), max(h, r.height))
    return disp

def mask_xrefs(doc):
    out = set()
    for x in range(1, doc.xref_length()):
        for k in ("SMask", "Mask"):
            v = doc.xref_get_key(x, k)
            if v[0] == "xref":
                out.add(int(v[1].split()[0]))
    return out

def shrink(src, dst, dpi=150, q=72, min_bytes=40000, verbose=False):
    doc = fitz.open(src)
    disp = collect_display(doc)
    masks = mask_xrefs(doc)
    saved = 0
    for xr in range(1, doc.xref_length()):
        if doc.xref_get_key(xr, "Subtype")[1] != "/Image": continue
        if xr in masks: continue                       # leave soft masks alone (tiny)
        if doc.xref_get_key(xr, "ImageMask")[1] == "true": continue
        try: raw = len(doc.xref_stream_raw(xr) or b"")
        except Exception: continue
        if raw < min_bytes: continue
        W = int(doc.xref_get_key(xr, "Width")[1]); H = int(doc.xref_get_key(xr, "Height")[1])
        dw, dh = disp.get(xr, (0, 0))
        if dw <= 0 or dh <= 0:                         # unused / undetectable -> cap at 150dpi of page
            dw, dh = 436.0, 612.0
        tw = max(1, min(W, int(round(dw / 72.0 * dpi))))
        th = max(1, min(H, int(round(dh / 72.0 * dpi))))
        # keep aspect: scale by the stricter factor
        f = min(tw / W, th / H, 1.0)
        nw, nh = max(1, int(round(W * f))), max(1, int(round(H * f)))
        try:
            pm = fitz.Pixmap(doc, xr)
        except Exception as e:
            if verbose: print("  skip", xr, e)
            continue
        if pm.alpha:                                   # alpha lives in the SMask, not here
            pm = fitz.Pixmap(pm, 0)
        gray = pm.colorspace and pm.colorspace.n == 1
        if pm.colorspace is None: continue
        if pm.colorspace.n not in (1, 3):              # CMYK / other -> RGB
            pm = fitz.Pixmap(fitz.csRGB, pm)
        mode = "L" if pm.n == 1 else "RGB"
        img = Image.frombytes(mode, (pm.width, pm.height), pm.samples)
        if (nw, nh) != (pm.width, pm.height):
            img = img.resize((nw, nh), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=q, optimize=True, progressive=True, subsampling=1)
        new = buf.getvalue()
        if len(new) >= raw:                            # no gain -> leave original
            continue
        doc.update_stream(xr, new, new=True, compress=False)
        doc.xref_set_key(xr, "Width", str(nw))
        doc.xref_set_key(xr, "Height", str(nh))
        doc.xref_set_key(xr, "ColorSpace", "/DeviceGray" if mode == "L" else "/DeviceRGB")
        doc.xref_set_key(xr, "BitsPerComponent", "8")
        doc.xref_set_key(xr, "Filter", "/DCTDecode")
        doc.xref_set_key(xr, "DecodeParms", "null")
        doc.xref_set_key(xr, "Decode", "null")
        doc.xref_set_key(xr, "Interpolate", "true")
        saved += raw - len(new)
        if verbose: print("   xref %d %dx%d -> %dx%d  %.2f -> %.2f MB" % (xr, W, H, nw, nh, raw/1e6, len(new)/1e6))
    try: doc.subset_fonts(verbose=False)
    except Exception: pass
    doc.save(dst, garbage=4, deflate=True, deflate_images=True, deflate_fonts=True, clean=True, use_objstms=1)
    doc.close()
    return os.path.getsize(dst)

if __name__ == "__main__":
    dpi = int(sys.argv[1]); q = int(sys.argv[2])
    out = os.path.join(SRC, sys.argv[3])
    os.makedirs(out, exist_ok=True)
    files = sys.argv[4:] or sorted(glob.glob(os.path.join(SRC, "*.pdf")))
    tot_a = tot_b = 0
    for f in files:
        base = os.path.basename(f)
        n = shrink(f, os.path.join(out, base), dpi, q, verbose=("-v" in os.environ.get("V","")))
        a = os.path.getsize(f); tot_a += a; tot_b += n
        print("%6.1fMB -> %5.2fMB  %s" % (a/1e6, n/1e6, base))
    print("TOTAL %.1fMB -> %.2fMB" % (tot_a/1e6, tot_b/1e6))
