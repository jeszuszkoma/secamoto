"""One-off import: scraped secamoto.hu data + photos -> data/catalog.json and img/ (WebP).

Source: C:/Claude/Repos/_media/secamoto (catalog.json + img/), pulled 2026-10-19 with the
owner's permission. Needs Pillow (dev only; the site itself has no dependencies).
Run: python tools/import_media.py
"""
import json
import pathlib
import re

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
MEDIA = pathlib.Path("C:/Claude/Repos/_media/secamoto")

# shop URL segment -> (our slug, display name, group)
CATEGORIES = {
    "Borruha": ("ferfi-borruha", "Bőrruha", "ferfi"),
    "Bornadrag": ("ferfi-nadrag", "Motoros nadrág", "ferfi"),
    "Borkabat": ("ferfi-borkabat", "Bőrkabát", "ferfi"),
    "Textil-kabat": ("ferfi-textilkabat", "Textil kabát", "ferfi"),
    "Kesztyu": ("ferfi-kesztyu", "Kesztyű", "ferfi"),
    "Cipo-Csizma": ("ferfi-csizma", "Cipő, csizma", "ferfi"),
    "Polok": ("polo", "Póló", "ferfi"),
    "Borruha-Motoros-Borkabat": ("noi-borkabat", "Bőrkabát", "noi"),
    "Noi-Textil-Motoros-Kabat": ("noi-textilkabat", "Textil kabát", "noi"),
    "Motoros-Nadrag-Bor-Textil-Farmer": ("noi-nadrag", "Nadrág", "noi"),
    "Noi-Motoros-kesztyuk": ("noi-kesztyu", "Kesztyű", "noi"),
    "Noi-Cipo-Csizma": ("noi-csizma", "Cipő, csizma", "noi"),
    "Kiegeszitok": ("kiegeszitok", "Kiegészítők", "egyeb"),
    "Protektorok-D3O": ("protektorok", "Protektorok D3O", "egyeb"),
}


def save_webp(src, dst, width, quality=80):
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src)
    im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(dst, "WEBP", quality=quality, method=6)
    return im.size


def stock(text):
    text = text or ""
    m = re.search(r"Raktáron \((\d+) db\)", text)
    if m:
        return True, int(m.group(1))
    if text.startswith("Nincs"):
        return False, 0
    return True, None


raw = json.loads((MEDIA / "catalog.json").read_text(encoding="utf-8"))
out = {"source": raw["source"], "fetched": raw["fetched"], "categories": [], "products": []}
seen = set()
for c in raw["categories"]:
    seg = c["url"].rstrip("/").split("/")[-1]
    slug, name, group = CATEGORIES[seg]
    ids = []
    for p in c["products"]:
        pslug = pathlib.Path(p["image_file"]).stem
        assert pslug not in seen, pslug
        seen.add(pslug)
        src = MEDIA / p["image_file"]
        w, h = save_webp(src, ROOT / f"img/p/{pslug}.webp", 900)
        save_webp(src, ROOT / f"img/p/{pslug}-s.webp", 420, 78)
        ok, qty = stock(p.get("stock"))
        out["products"].append({
            "slug": pslug,
            "name": p["name"].strip(),
            "sku": p.get("sku"),
            "category": slug,
            "price": p.get("price_gross_huf"),
            "in_stock": ok,
            "qty": qty,
            "sizes": p.get("sizes") or [],
            "sizes_in_stock": p.get("sizes_in_stock") or [],
            "colors": p.get("colors") or [],
            "features": p.get("features") or [],
            "desc": p.get("desc") or "",
            "shop_url": p["url"],
            "img_w": w, "img_h": h,
        })
        ids.append(pslug)
    out["categories"].append({"slug": slug, "name": name, "group": group, "shop_url": c["url"], "products": ids})

for f, width in [("hero-2.jpg", 1600), ("hero-3.jpg", 1600), ("hero-4.jpg", 1600)]:
    stem = pathlib.Path(f).stem
    save_webp(MEDIA / "img/banners" / f, ROOT / f"img/hero/{stem}.webp", width, 78)
    save_webp(MEDIA / "img/banners" / f, ROOT / f"img/hero/{stem}-m.webp", 900, 76)
for f in (MEDIA / "img/tiles").glob("*.jpg"):
    save_webp(f, ROOT / f"img/tiles/{f.stem.lower()}.webp", 700, 82)
save_webp(MEDIA / "img/logo.png", ROOT / "img/seca-logo.webp", 281, 90)
(ROOT / "img/seca-logo.png").write_bytes((MEDIA / "img/logo.png").read_bytes())

(ROOT / "data/catalog.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(out["categories"]), "categories,", len(out["products"]), "products")
