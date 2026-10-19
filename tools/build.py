"""Build the Secamoto demo site from data/*.json. Python 3 stdlib only.

Writes index.html, kategoria/<slug>.html, mod/<id>.html, termek/<slug>.html, robots.txt.
Run after any change in data/, css/ or js/:  python tools/build.py
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSET_VERSION = 4

site = json.loads((ROOT / "data/site.json").read_text(encoding="utf-8"))
cat = json.loads((ROOT / "data/catalog.json").read_text(encoding="utf-8"))
modes = json.loads((ROOT / "data/modes.json").read_text(encoding="utf-8"))["modes"]

products = {p["slug"]: p for p in cat["products"]}
cats = {c["slug"]: c for c in cat["categories"]}
GROUPS = {"ferfi": "Férfi", "noi": "Női", "egyeb": "Kiegészítők és védelem"}
COLORS = {
    "black": "fekete", "white": "fehér", "grey": "szürke", "gray": "szürke", "titanium": "titán",
    "fluo yellow": "fluo sárga", "fluo red": "fluo piros", "red": "piros", "blue": "kék", "brown": "barna",
    "khaki": "khaki", "green": "zöld", "pink": "rózsaszín", "camo": "terepmintás", "orange": "narancs",
    "neon": "neon", "fluo": "fluo", "yellow": "sárga", "silver": "ezüst", "navy": "sötétkék", "beige": "bézs",
}

# ---------- helpers ----------
e = lambda s: html.escape(str(s), quote=True)


def huf(n):
    return f"{n:,}".replace(",", " ") + " Ft" if n is not None else "Ár a webshopban"


def short(name):
    return re.sub(r"^Seca\s+", "", name).strip()


def color_hu(c):
    return COLORS.get(c.lower().strip(), c)


for m in modes:
    rx = re.compile(m["match"], re.I)
    m["products"] = [
        p["slug"] for p in cat["products"]
        if rx.search(p["name"].lower() + (" " + " ".join(p["features"]).lower() if m.get("match_features") else ""))
    ]
for p in cat["products"]:
    p["modes"] = [m["id"] for m in modes if p["slug"] in m["products"]]
    p["cat"] = cats[p["category"]]

LEANS = [-3, 2.5, -2, 3, -2.5, 2]  # tilt (deg) of product cards on hover, by position


def card(p, pre, i):
    lean = LEANS[i % len(LEANS)]
    stock = (f'<span class="st st-on">Raktáron{f" ({p["qty"]} db)" if p["qty"] else ""}</span>'
             if p["in_stock"] else '<span class="st st-off">Elfogyott</span>')
    return (
        f'<li class="card" style="--lean:{lean}deg" data-i="{i}" data-price="{p["price"] or 0}" '
        f'data-stock="{1 if p["in_stock"] else 0}" data-modes="{" ".join(p["modes"])}" data-group="{p["cat"]["group"]}">'
        f'<a href="{pre}termek/{p["slug"]}.html">'
        f'<span class="card-img"><img src="{pre}img/p/{p["slug"]}-s.webp" alt="" loading="lazy" width="420" height="{round(420 * p["img_h"] / p["img_w"])}"></span>'
        f'<span class="card-body"><span class="card-name">{e(short(p["name"]))}</span>'
        f'<span class="card-row"><b class="price">{huf(p["price"])}</b>{stock}</span></span></a></li>'
    )


def grid(items, pre, gid="grid"):
    return f'<ul class="grid" id="{gid}">' + "".join(card(p, pre, i) for i, p in enumerate(items)) + "</ul>"


ICON = {
    "warn": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 2 21h20L12 3Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M12 10v5M12 17.5v.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>',
    "fb": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 8h3V4h-3a4 4 0 0 0-4 4v2H7v4h3v8h4v-8h3l1-4h-4V8Z" fill="currentColor"/></svg>',
    "ig": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.5" cy="6.5" r="1.2" fill="currentColor"/></svg>',
}


def header(pre, active=""):
    def group_links(g):
        return "".join(
            f'<a href="{pre}kategoria/{c["slug"]}.html"{" aria-current=\"page\"" if c["slug"] == active else ""}>{e(c["name"])}</a>'
            for c in cat["categories"] if c["group"] == g
        )
    mode_links = "".join(
        f'<a class="pill pill-{m["id"]}" href="{pre}mod/{m["id"]}.html"{" aria-current=\"page\"" if m["id"] == active else ""}>{m["label"]}</a>'
        for m in modes
    )
    promo = site["promo"]
    promo_html = (
        f'<div class="promo"><div class="in">{ICON["warn"]}<span>{e(promo["text"])} · kupon: <b>{e(promo["code"])}</b></span>'
        f'<span class="promo-demo">Dizájn demó · vásárlás a <a href="{site["shop_url"]}">{site["domain"]}</a> webshopban</span></div></div>'
        if promo["on"] else ""
    )
    return f"""<a class="skip" href="#main">Ugrás a tartalomra</a>
{promo_html}
<header class="hdr">
  <div class="in hdr-in">
    <a class="logo" href="{pre}index.html"><img src="{pre}img/seca-logo.webp" alt="Seca – secamoto.hu" width="141" height="30"></a>
    <nav class="nav" id="nav" aria-label="Fő menü">
      <details class="dd"><summary>Férfi</summary><div class="dd-panel">{group_links("ferfi")}</div></details>
      <details class="dd"><summary>Női</summary><div class="dd-panel">{group_links("noi")}</div></details>
      <a href="{pre}kategoria/kiegeszitok.html"{" aria-current=\"page\"" if active == "kiegeszitok" else ""}>Kiegészítők</a>
      <a href="{pre}kategoria/protektorok.html"{" aria-current=\"page\"" if active == "protektorok" else ""}>Protektorok</a>
      <details class="dd dd-modes"><summary>Módok</summary><div class="dd-panel">{mode_links}</div></details>
    </nav>
    <a class="hdr-tel" href="tel:{site["phone"]}">{ICON["phone"]}<span>{site["phone_text"]}</span></a>
    <div class="gear-ind" aria-hidden="true"><small>GEAR</small><b id="gearNow">N</b></div>
    <button class="burger" type="button" aria-expanded="false" aria-controls="nav"><span></span>Menü</button>
  </div>
  <div class="revbar" aria-hidden="true"><i id="revFill"></i></div>
</header>"""


def footer(pre):
    s = site
    return f"""<footer class="ftr" data-gear="6">
  <div class="in ftr-grid">
    <div>
      <img src="{pre}img/seca-logo.webp" alt="Seca" width="141" height="30" loading="lazy">
      <p>{e(s["tagline"])}</p>
      <p class="dim">{e(s["company"])} · székhely: {e(s["seat"])}<br>Adószám: {e(s["tax_number"])} · Cégjegyzékszám: {e(s["company_reg_number"])}</p>
    </div>
    <div>
      <h2>Elérhetőség</h2>
      <p><a href="tel:{s["phone"]}">{s["phone_text"]}</a><br><a href="mailto:{s["email"]}">{s["email"]}</a></p>
      <p class="dim">Személyes átvétel: {e(s["pickup"])}.</p>
    </div>
    <div>
      <h2>Vásárlás</h2>
      <p><a href="{s["links"]["shipping"]}">Szállítás</a><br><a href="{s["links"]["payment"]}">Fizetés</a><br><a href="{s["links"]["size_table"]}">Mérettáblázat</a><br><a href="{s["links"]["terms"]}">ÁSZF</a><br><a href="{s["links"]["privacy"]}">Adatkezelés</a></p>
    </div>
    <div>
      <h2>Kövess minket</h2>
      <p class="social"><a href="{s["social"]["facebook"]}" aria-label="Facebook">{ICON["fb"]}</a><a href="{s["social"]["instagram"]}" aria-label="Instagram">{ICON["ig"]}</a></p>
    </div>
  </div>
  <div class="in ftr-bottom">
    <span>© 2026 {e(s["company"])}</span>
    <span>Üzemeltető: <a href="https://mukodoweb.hu">mukodoweb.hu</a></span>
    <span class="dim">Dizájn demó. A vásárlás a <a href="{s["shop_url"]}">{s["domain"]}</a> webshopban történik.</span>
  </div>
</footer>"""


def page(path, title, desc, body, active="", body_class=""):
    depth = path.count("/")
    pre = "../" * depth
    robots = '<meta name="robots" content="noindex, nofollow">' if site["noindex"] else ""
    doc = f"""<!doctype html>
<html lang="hu">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{robots}
<meta name="theme-color" content="#07090B">
<link rel="icon" href="{pre}img/favicon.svg" type="image/svg+xml">
<link rel="preload" href="{pre}fonts/chakra-petch-700-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{pre}css/fonts.css?v={ASSET_VERSION}">
<link rel="stylesheet" href="{pre}css/style.css?v={ASSET_VERSION}">
<script src="{pre}js/site.js?v={ASSET_VERSION}" defer></script>
</head>
<body class="{body_class}">
{header(pre, active)}
<main id="main">
{body}
</main>
{footer(pre)}
</body>
</html>
"""
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")


def crumbs(pre, items):
    parts = [f'<a href="{pre}index.html">Főoldal</a>'] + [
        f'<a href="{href}">{e(t)}</a>' if href else f'<span aria-current="page">{e(t)}</span>' for t, href in items
    ]
    return '<nav class="crumbs" aria-label="Morzsamenü">' + '<span aria-hidden="true">›</span>'.join(parts) + "</nav>"


def filters(present_modes, groups=None):
    chips = '<button type="button" class="chip" aria-pressed="true" data-f="all">Mind</button>' + "".join(
        f'<button type="button" class="chip chip-{m["id"]}" aria-pressed="false" data-f="{m["id"]}">{m["label"]}<small>{m["hu"]}</small></button>'
        for m in modes if m["id"] in present_modes
    )
    if groups:
        chips = '<button type="button" class="chip" aria-pressed="true" data-g="all">Mind</button>' + "".join(
            f'<button type="button" class="chip" aria-pressed="false" data-g="{g}">{GROUPS[g]}</button>' for g in groups
        )
    return f"""<div class="filters in">
  <div class="chips" role="group" aria-label="Szűrés">{chips}</div>
  <label class="toggle"><input type="checkbox" id="onlyStock"> Csak raktáron</label>
  <label class="sort"><span>Sorrend</span><select id="sortBy"><option value="i">Ajánlott</option><option value="pa">Ár: alacsony → magas</option><option value="pd">Ár: magas → alacsony</option></select></label>
</div>
<p class="empty in" id="empty" hidden>Nincs találat ezzel a szűréssel.</p>"""


# ---------- home ----------
def mode_panel(m, pre, active):
    items = [products[s] for s in m["products"]]
    pick = [p for p in items if p["in_stock"]][:4] or items[:4]
    strip = "".join(
        f'<li><a href="{pre}termek/{p["slug"]}.html"><img src="{pre}img/p/{p["slug"]}-s.webp" alt="" loading="lazy" width="420" height="{round(420 * p["img_h"] / p["img_w"])}">'
        f'<span>{e(short(p["name"]))}</span><b>{huf(p["price"])}</b></a></li>'
        for p in pick
    )
    return f"""<div class="mp" id="mp-{m["id"]}" role="tabpanel" aria-labelledby="mt-{m["id"]}"{"" if active else " hidden"}>
  <figure class="mp-photo"><img src="{pre}{m["photo"]}" alt="" style="object-position:{m["photo_pos"]}"{"" if active else ' loading="lazy"'}></figure>
  <div class="mp-copy">
    <span class="mp-mode">{m["label"]} · {m["hu"]}</span>
    <h2>{e(m["head"])}</h2>
    <p>{e(m["text"])}</p>
    <a class="btn btn-red" href="{pre}mod/{m["id"]}.html">Mind a {len(items)} termék <span aria-hidden="true">›</span></a>
  </div>
  <ul class="mp-strip">{strip}</ul>
</div>"""


def cat_card(c, pre, i):
    items = [products[s] for s in c["products"]]
    lead = next((p for p in items if p["in_stock"]), items[0])
    prices = [p["price"] for p in items if p["price"]]
    lean = LEANS[i % len(LEANS)]
    return (
        f'<li class="card cat-card" style="--lean:{lean}deg"><a href="{pre}kategoria/{c["slug"]}.html">'
        f'<span class="card-img"><img src="{pre}img/p/{lead["slug"]}-s.webp" alt="" loading="lazy" width="420" height="{round(420 * lead["img_h"] / lead["img_w"])}"></span>'
        f'<span class="card-body"><span class="card-name">{e(c["name"])}</span>'
        f'<span class="card-row"><span class="dim">{len(items)} termék</span><b class="price">{huf(min(prices))}-tól</b></span></span></a></li>'
    )


def build_home():
    pre = ""
    default = "sport"
    tabs = "".join(
        f'<button type="button" role="tab" id="mt-{m["id"]}" aria-controls="mp-{m["id"]}" aria-selected="{"true" if m["id"] == default else "false"}" '
        f'data-mode="{m["id"]}" data-gear="{m["gear"]}" data-rpm="{m["rpm"]}"><b>{m["label"]}</b><span>{m["hu"]}</span><i>{len(m["products"])}</i></button>'
        for m in modes
    )
    panels = "".join(mode_panel(m, pre, m["id"] == default) for m in modes)
    n_all = len(cat["products"])
    n_stock = sum(p["in_stock"] for p in cat["products"])
    prices = [p["price"] for p in cat["products"] if p["price"]]

    def cat_section(group, gear, title, extra=""):
        cs = [c for c in cat["categories"] if c["group"] == group]
        return f"""<section class="sec" data-gear="{gear}" aria-labelledby="h-{group}">
  <div class="in">
    <div class="sec-head"><span class="sec-gear" aria-hidden="true">{gear}</span><h2 id="h-{group}">{title}</h2></div>
    {extra}
    <ul class="grid grid-cats">{"".join(cat_card(c, pre, i) for i, c in enumerate(cs))}</ul>
  </div>
</section>"""

    women_lead = f"""<a class="lead-card" href="kategoria/noi-borkabat.html"><img src="img/tiles/noi-borkabat.webp" alt="Motoros nő fekete Seca bőrkabátban, motor mellett" loading="lazy" width="690" height="360"><span><b>Női bőrkabátok</b> Bonneville, Darkside, SRS II Lady</span></a>"""

    body = f"""<section class="dash" data-gear="1" aria-label="Vezetési módok">
  <div class="in">
    <div class="tft">
      <div class="tft-top"><span id="clock">--:--</span><span class="ice" id="ice" hidden>{ICON["warn"]} JEGES ÚT?</span><span id="wx">{e(site["weather"]["label"])}</span></div>
      <div class="tft-tach"><svg class="tach" id="tach" viewBox="0 0 600 64" aria-hidden="true"></svg><div class="gear-big" aria-hidden="true"><small>GEAR</small><b id="dashGear">4</b><em id="shift">SHIFT</em></div></div>
      <div class="tft-body">
        <div class="tft-menu">
          <h1>Hogyan <br>motorozol?</h1>
          <p class="lede">Válassz módot, megmutatjuk hozzá a Seca felszerelést.</p>
          <div class="modes" role="tablist" aria-label="Vezetési mód">{tabs}</div>
          <p class="wx-note" id="wxNote" hidden></p>
        </div>
        <div class="tft-panels">{panels}</div>
      </div>
      <div class="tft-odo">
        <span><small>ODO</small><b>{n_all}</b> termék a demóban</span>
        <span><small>RAKTÁRON</small><b>{n_stock}</b> db-féle</span>
        <span><small>ÁR</small><b>{huf(min(prices))}</b> – {huf(max(prices))}</span>
        <span><small>GLS</small><b>2 900 Ft</b> 1–3 munkanap</span>
      </div>
    </div>
  </div>
</section>
{cat_section("ferfi", 2, "Férfi")}
{cat_section("noi", 3, "Női", women_lead)}
<section class="band" data-gear="4">
  <picture><source media="(max-width: 700px)" srcset="img/hero/hero-2-m.webp"><img src="img/hero/hero-2.webp" alt="Négy motoros fluo sárga, narancs, szürke és kék Seca kabátban" loading="lazy" width="1600" height="653"></picture>
  <div class="in band-copy">
    <h2>Látszódj<br>az úton.</h2>
    <p>Fluo sárga, narancs, kék: a Seca kabátok messziről látszanak.</p>
    <a class="btn btn-red" href="kategoria/ferfi-borkabat.html">Bőrkabátok <span aria-hidden="true">›</span></a>
  </div>
</section>
{cat_section("egyeb", 5, "Kiegészítők és védelem", '<p class="sec-lede">A Richa D3O protektorok puhák és hajlékonyak, ütésnél egy pillanat alatt megkeményednek. Seca kabátokba és nadrágokba is betehetők.</p>')}
<section class="trip" data-gear="6" aria-labelledby="h-trip">
  <div class="in">
    <h2 id="h-trip" class="vh">Szállítás és fizetés</h2>
    <dl class="trip-grid">
      <div><dt>SZÁLLÍTÁS</dt><dd><b>2 900 Ft</b>GLS házhoz, 1–3 munkanap, kártyás fizetésnél. Utánvéttel 4 190 Ft.</dd></div>
      <div><dt>ÁTVÉTEL</dt><dd><b>0 Ft</b>Budapest XVII. kerület, előre egyeztetett időpontban.</dd></div>
      <div><dt>FIZETÉS</dt><dd><b>Barion</b>Bankkártya, előre utalás vagy utánvét.</dd></div>
      <div><dt>MÉRET</dt><dd><b><a href="{site["links"]["size_table"]}">Mérettáblázat ›</a></b>Bizonytalan vagy? Hívj: <a href="tel:{site["phone"]}">{site["phone_text"]}</a></dd></div>
    </dl>
  </div>
</section>"""
    page("index.html", "Secamoto – Seca motoros ruházat", "Seca motoros bőrruha, kabát, nadrág, kesztyű és csizma. Válassz vezetési módot: RAIN, ROAD, URBAN, SPORT vagy TRACK.", body, body_class="home")


# ---------- category + mode pages ----------
def build_category(c):
    pre = "../"
    items = [products[s] for s in c["products"]]
    present = {m for p in items for m in p["modes"]}
    group = GROUPS[c["group"]]
    title_full = f'{group} {c["name"].lower()}' if c["group"] != "egyeb" else c["name"]
    body = f"""<section class="pagehead" data-gear="1">
  <div class="in">
    {crumbs(pre, [(group, f"{pre}index.html#h-{c['group']}"), (c["name"], None)])}
    <h1>{e(c["name"])}<small>{e(group)}</small></h1>
    <p class="ph-meta"><span class="odo-num">{len(items)}</span> termék a demóban · <a href="{c["shop_url"]}">a webshopban mind ›</a></p>
  </div>
</section>
{filters(present)}
<section class="list" data-gear="2"><div class="in">{grid(items, pre)}</div></section>"""
    page(f'kategoria/{c["slug"]}.html', f'{title_full} – Secamoto', f'Seca {title_full.lower()}: {len(items)} termék, árak, készlet.', body, active=c["slug"])


def build_mode(m):
    pre = "../"
    items = [products[s] for s in m["products"]]
    groups = [g for g in GROUPS if any(p["cat"]["group"] == g for p in items)]
    body = f"""<section class="modehead" data-gear="1">
  <img src="{pre}{m["photo"]}" alt="" style="object-position:{m["photo_pos"]}">
  <div class="in">
    {crumbs(pre, [("Vezetési módok", None), (m["label"], None)])}
    <div class="mh-row">
      <div class="gear-big" aria-hidden="true"><small>GEAR</small><b>{m["gear"]}</b></div>
      <div><span class="mp-mode">{m["label"]} · {m["hu"]}</span><h1>{e(m["head"])}</h1><p>{e(m["text"])}</p></div>
    </div>
    <nav class="mh-modes" aria-label="Másik mód">{"".join(f'<a class="pill pill-{o["id"]}" href="{o["id"]}.html"{" aria-current=\"page\"" if o["id"] == m["id"] else ""}>{o["label"]}</a>' for o in modes)}</nav>
  </div>
</section>
{filters(set(), groups)}
<section class="list" data-gear="2"><div class="in">{grid(items, pre)}</div></section>"""
    page(f'mod/{m["id"]}.html', f'{m["label"]} mód: {m["head"]} – Secamoto', m["text"], body, active=m["id"])


# ---------- product pages ----------
def build_product(p):
    pre = "../"
    c = p["cat"]
    group = GROUPS[c["group"]]
    if p["in_stock"]:
        stock = f'<p class="pp-stock st-on"><i></i>Raktáron{f" ({p["qty"]} db)" if p["qty"] else ""}</p>'
    else:
        stock = f'<p class="pp-stock st-off"><i></i>Nincs raktáron. Érdeklődj: <a href="tel:{site["phone"]}">{site["phone_text"]}</a></p>'
    if p["sizes"]:
        chips = "".join(
            f'<li class="{"on" if s in p["sizes_in_stock"] else "off"}">{e(s)}{"" if s in p["sizes_in_stock"] else "<span class=vh> (nincs készleten)</span>"}</li>'
            for s in p["sizes"]
        )
        sizes = f'<div class="pp-block"><h2>Méret</h2><ul class="sizes">{chips}</ul><p class="dim small">Világos: van készleten. <a href="{site["links"]["size_table"]}">Mérettáblázat ›</a></p></div>'
    else:
        sizes = f'<div class="pp-block"><h2>Méret</h2><p class="dim small">Méretek és készlet a webshopban. <a href="{site["links"]["size_table"]}">Mérettáblázat ›</a></p></div>'
    colors = (f'<div class="pp-block"><h2>Szín</h2><p>{e(", ".join(color_hu(x) for x in p["colors"]))}</p></div>' if p["colors"] else "")
    mode_badges = "".join(
        f'<a class="pill pill-{m["id"]}" href="{pre}mod/{m["id"]}.html">{m["label"]}</a>' for m in modes if m["id"] in p["modes"]
    )
    modes_html = f'<div class="pp-block"><h2>Ehhez a módhoz</h2><p class="pills">{mode_badges}</p></div>' if mode_badges else ""
    promo = (f'<p class="pp-promo">{ICON["warn"]}<span>Most −45% a végösszegből a <b>{e(site["promo"]["code"])}</b> kuponnal.</span></p>'
             if site["promo"]["on"] else "")
    feats = (f'<section class="pp-feats" data-gear="3"><div class="in"><h2>Jellemzők</h2><ul>'
             + "".join(f"<li>{e(f.rstrip('.'))}</li>" for f in p["features"]) + "</ul></div></section>") if p["features"] else ""
    ship = "".join(f'<div><dt>{e(s["name"])}</dt><dd>{huf(s["price"]) if s["price"] else "ingyenes"}</dd></div>' for s in site["shipping"])
    related = [products[s] for s in c["products"] if s != p["slug"]][:4]
    rel_html = (f'<section class="related" data-gear="4"><div class="in"><h2>Még ebből: {e(c["name"].lower())}</h2>{grid(related, pre, "rel")}'
                f'<p><a class="btn btn-ghost" href="{pre}kategoria/{c["slug"]}.html">Mind a {len(c["products"])} termék ›</a></p></div></section>') if related else ""
    body = f"""<section class="pp" data-gear="1">
  <div class="in">
    {crumbs(pre, [(group, f"{pre}index.html#h-{c['group']}"), (c["name"], f"{pre}kategoria/{c['slug']}.html"), (short(p["name"]), None)])}
    <div class="pp-grid">
      <figure class="pp-img"><img src="{pre}img/p/{p["slug"]}.webp" alt="{e(p["name"])}" width="{p["img_w"]}" height="{p["img_h"]}"></figure>
      <div class="pp-info">
        <p class="pp-cat">{e(group)} · {e(c["name"])}</p>
        <h1>{e(p["name"])}</h1>
        {f'<p class="pp-sku">Cikkszám: {e(p["sku"])}</p>' if p.get("sku") else ""}
        <p class="pp-price">{f'<b>{huf(p["price"])[:-3]}</b> Ft <small>bruttó</small>' if p["price"] else "Ár a webshopban"}</p>
        {promo}
        {stock}
        {sizes}
        {colors}
        {modes_html}
        <div class="pp-cta">
          <a class="btn btn-red btn-big" href="{p["shop_url"]}">Megveszem a webshopban <span aria-hidden="true">›</span></a>
          <a class="btn btn-ghost" href="tel:{site["phone"]}">{ICON["phone"]} Kérdésem van</a>
        </div>
        <dl class="pp-ship">{ship}</dl>
      </div>
    </div>
  </div>
</section>
{feats}
{rel_html}"""
    desc = p["desc"] or f'{p["name"]}, {huf(p["price"])}. {group} {c["name"].lower()} a Secamoto kínálatából.'
    page(f'termek/{p["slug"]}.html', f'{short(p["name"])} – Secamoto', desc[:155], body, active=c["slug"])


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#07090B"/><text x="32" y="46" text-anchor="middle" font-family="Arial Black, Arial, sans-serif" font-weight="900" font-size="40" fill="#FF2335">S</text></svg>
"""

if __name__ == "__main__":
    (ROOT / "img/favicon.svg").write_text(FAVICON, encoding="utf-8")
    build_home()
    for c in cat["categories"]:
        build_category(c)
    for m in modes:
        build_mode(m)
    for p in cat["products"]:
        build_product(p)
    (ROOT / "robots.txt").write_text("User-agent: *\nDisallow: /\n" if site["noindex"] else "User-agent: *\nAllow: /\n", encoding="utf-8")
    print("built:", 1, "home,", len(cat["categories"]), "categories,", len(modes), "modes,", len(cat["products"]), "products")
    for m in modes:
        print(f'  {m["label"]:6} {len(m["products"]):3} products')
