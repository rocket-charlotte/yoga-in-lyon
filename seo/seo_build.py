#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yoga In Lyon — passe SEO sur le site généré.

Usage :  python3 seo/seo_build.py .          (depuis la racine du site)

À relancer après chaque mise à jour du planning. Le script est idempotent :
on peut le lancer autant de fois qu'on veut, il remplace ses propres ajouts.

Ce qu'il fait :
  1. Lit les cours (const DATA) dans Yoga_a_Lyon_Planning.html et normalise
     les horaires ("9h00" -> "09h00", sinon le tri par heure est faux).
  2. Génère une page par studio  : studio-<nom>.html
  3. Génère une page par style   : hatha-yoga-lyon.html, vinyasa-yoga-lyon.html…
  4. Écrit le planning complet en HTML dans la page Planning (lisible par Google,
     le JavaScript continue de filtrer par-dessus).
  5. Enrichit les pages quartier (texte éditorial, noms de studios en H3,
     liens vers les styles, fil d'Ariane).
  6. Sur toutes les pages : liens « Voir leur planning » -> page studio,
     liens Accueil.html -> /, colonne « Réseaux » vide -> « Styles de yoga ».
  7. Écrit sitemap.xml et robots.txt (et .htaccess s'il n'existe pas).
"""
import html
import json
import re
import sys
import unicodedata
import urllib.parse
from collections import Counter, OrderedDict, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from seo_content import QUARTIERS, STYLES  # noqa: E402

BASE = "https://yoga-in-lyon.fr/"
JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
CRENEAUX = ["Matin", "Midi", "Après-midi", "Soir"]
PLANNING = "Yoga_a_Lyon_Planning.html"
TODAY = date.today().isoformat()
esc = html.escape


# --------------------------------------------------------------------------- utils
def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return re.sub(r"-+", "-", s)


def norm_time(t):
    m = re.fullmatch(r"(\d{1,2})h(\d{2})", (t or "").strip())
    return f"{int(m.group(1)):02d}h{m.group(2)}" if m else (t or "")


def arr_page(arr):
    return "yoga-villeurbanne.html" if arr == "Villeurbanne" else "yoga-" + slugify(arr) + ".html"


def arr_label(arr):
    """'Lyon 4e' -> '4e arrondissement de Lyon'."""
    m = re.fullmatch(r"Lyon (\d+)(er|e)", arr)
    return f"{m.group(1)}{m.group(2)} arrondissement de Lyon" if m else arr


def studio_page(name):
    return "studio-" + re.sub(r"^studio-", "", slugify(name)) + ".html"


def style_page(ts):
    return STYLES[ts]["slug"] + ".html" if ts in STYLES else PLANNING


def plural(n, one, many):
    return f"{n} {one if n == 1 else many}"


def replace_block(text, key, new, anchor_after=None, anchor_before=None):
    """Insère/remplace un bloc délimité par <!--seo:key-->…<!--/seo:key-->."""
    block = f"<!--seo:{key}-->{new}<!--/seo:{key}-->"
    pat = re.compile(rf"<!--seo:{re.escape(key)}-->.*?<!--/seo:{re.escape(key)}-->", re.S)
    if pat.search(text):
        return pat.sub(lambda m: block, text, count=1)
    if anchor_after and anchor_after in text:
        i = text.index(anchor_after) + len(anchor_after)
        return text[:i] + "\n" + block + text[i:]
    if anchor_before and anchor_before in text:
        i = text.index(anchor_before)
        return text[:i] + block + "\n" + text[i:]
    return text


def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"


def postal(adresse):
    m = re.search(r"(\d{5})\s+([A-Za-zÀ-ÿ' -]+)", adresse or "")
    street = (adresse or "").split(",")[0].strip()
    if m and re.match(r"^\d", street):
        return {"@type": "PostalAddress", "streetAddress": street, "postalCode": m.group(1),
                "addressLocality": m.group(2).strip(), "addressCountry": "FR"}
    return {"@type": "PostalAddress", "addressLocality": "Lyon", "addressCountry": "FR"}


def breadcrumb(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n,
                                 "item": BASE + (u if u != "/" else "")} for i, (n, u) in enumerate(items)]}


# --------------------------------------------------------------------------- data
def load(site):
    planning = (site / PLANNING).read_text(encoding="utf-8")
    m = re.search(r"const DATA = (\[.*?\]);\s*\n", planning, re.S)
    if not m:
        sys.exit("DATA introuvable dans " + PLANNING)
    data = json.loads(m.group(1))
    for c in data:
        c["debut"], c["fin"] = norm_time(c.get("debut")), norm_time(c.get("fin"))
    planning = planning[:m.start(1)] + json.dumps(data, ensure_ascii=False) + planning[m.end(1):]

    markers = {}
    for p in site.glob("yoga-*.html"):
        mm = re.search(r"const MARKERS = (\[.*?\]);", p.read_text(encoding="utf-8"), re.S)
        if mm:
            for x in json.loads(mm.group(1)):
                markers[x["nom"]] = (x["lat"], x["lng"])

    descs = {}
    sp = site / "Studios.html"
    if sp.exists():
        t = sp.read_text(encoding="utf-8")
        for card in re.findall(r'class="studio-card".*?(?=class="studio-card"|</main>|<footer)', t, re.S):
            n = re.search(r'class="studio-name"[^>]*>(.*?)</', card, re.S)
            d = re.search(r'class="studio-desc"[^>]*>(.*?)</p>', card, re.S)
            if n and d:
                txt = html.unescape(re.sub(r"<[^>]+>", "", d.group(1))).strip()
                if not re.match(r"^\d+ créneaux? vérifiés?", txt):
                    descs[html.unescape(n.group(1)).strip()] = txt

    studios = OrderedDict()
    for c in data:
        s = studios.setdefault(c["studio"], {"name": c["studio"], "arr": c["arr"], "quartier": c["quartier"],
                                             "site": c["site"], "adresse": c["adresse"], "favicon": c.get("favicon", ""),
                                             "cours": []})
        s["cours"].append(c)
    for s in studios.values():
        s["cours"].sort(key=lambda c: (JOURS.index(c["jour"]) if c["jour"] in JOURS else 9, c["debut"]))
        s["styles"] = [ts for ts, _ in Counter(c["type_simple"] for c in s["cours"]).most_common()]
        s["geo"] = markers.get(s["name"])
        s["desc"] = descs.get(s["name"])
    return data, studios, planning


def chrome(site, studios, styles_present):
    """Récupère le <style>, le header et le footer d'une page quartier pour habiller les nouvelles pages."""
    ref = sorted(site.glob("yoga-lyon-*.html"))[0].read_text(encoding="utf-8")
    style = re.search(r"<style>.*?</style>", ref, re.S).group(0)
    header = re.search(r'<header class="site-header">.*?</header>', ref, re.S).group(0)
    header = re.sub(r'class="active"', 'class=""', header)
    footer = re.search(r'<footer class="site-footer">.*?</footer>', ref, re.S).group(0)
    return style, fix_links(header, studios, styles_present), fix_links(footer, studios, styles_present)


EXTRA_CSS = """
  .seo-intro { max-width: 1180px; margin: 0 auto; padding: 4px 24px 8px; }
  .seo-intro p { color: #5a4a68; font-size: 15.5px; line-height: 1.7; max-width: 760px; margin: 0 0 14px; }
  h3.studio-name { margin: 0; }
  .crumbs { max-width: 1180px; margin: 0 auto; padding: 22px 24px 0; font-size: 13px; color: var(--muted); }
  .crumbs a { color: var(--muted); } .crumbs a:hover { color: var(--brand-purple); }
  .facts { max-width: 1180px; margin: 0 auto; padding: 8px 24px 24px; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; }
  .fact { background: #fff; border-radius: 14px; padding: 16px 18px; border: 1px solid var(--border); }
  .fact .k { font-size: 11.5px; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); margin-bottom: 6px; }
  .fact .v { font-size: 15px; line-height: 1.45; }
  .section { max-width: 1180px; margin: 0 auto; padding: 18px 24px 40px; }
  .section h2 { font-size: 24px; font-weight: 500; margin: 0 0 16px; }
  .day-block { margin-bottom: 22px; }
  .day-block h3 { font-size: 18px; font-weight: 500; margin: 0 0 8px; }
  .slots { width: 100%; border-collapse: collapse; background: #fff; border-radius: 14px; overflow: hidden; }
  .slots td { padding: 11px 14px; border-bottom: 1px solid var(--border); font-size: 14.5px; vertical-align: top; }
  .slots tr:last-child td { border-bottom: 0; }
  .slots td.t { white-space: nowrap; font-weight: 600; width: 130px; }
  .slots td.s { color: var(--muted); }
  .note { font-size: 13px; color: var(--muted); margin-top: 6px; }
  .pills { display: flex; flex-wrap: wrap; gap: 10px; }
  .pills a { padding: 9px 18px; border-radius: 999px; background: var(--lavender-soft); color: var(--brand-purple); font-size: 13.5px; font-weight: 600; }
  .pills a:hover { background: var(--lavender); }
  .studio-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
  .studio-list a.item { display: block; background: #fff; border-radius: 14px; padding: 16px 18px; border: 1px solid var(--border); }
  .studio-list a.item strong { display: block; font-family: 'Fraunces', serif; font-size: 17px; font-weight: 500; color: var(--ink); }
  .studio-list a.item span { font-size: 13.5px; color: var(--muted); }
  #studio-map { width: 100%; height: 280px; border-radius: 18px; overflow: hidden; background: var(--border); }
  .seo-static .course-card { margin-bottom: 8px; }
"""


def ensure_extra_css(text):
    css = f'<style id="seo-extra">{EXTRA_CSS}</style>'
    if 'id="seo-extra"' in text:
        return re.sub(r'<style id="seo-extra">.*?</style>', lambda m: css, text, count=1, flags=re.S)
    return text.replace("</head>", css + "\n</head>", 1)


def page_shell(chrome_parts, *, title, desc, canonical, body, ld, map_js=""):
    style, header, footer = chrome_parts
    leaflet_css = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />' if map_js else ""
    leaflet_js = '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>' if map_js else ""
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{BASE}{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Yoga In Lyon">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{BASE}banner_web.jpg">
<meta property="og:url" content="{BASE}{canonical}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
{leaflet_css}
{"".join(jsonld(x) for x in ld)}
{style}
<style id="seo-extra">{EXTRA_CSS}</style>
</head>
<body>

{header}
{body}
{footer}
{leaflet_js}
{map_js}
</body>
</html>
"""


def map_script(points, el="studio-map", zoom=15):
    pts = [{"nom": n, "lat": la, "lng": ln} for n, (la, ln) in points if (la, ln) != (None, None)]
    if not pts:
        return ""
    return f"""<script>
const PTS = {json.dumps(pts, ensure_ascii=False)};
const map = L.map('{el}', {{ scrollWheelZoom: false }}).setView([PTS[0].lat, PTS[0].lng], {zoom});
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}', {{ maxZoom: 16, attribution: '&copy; Esri' }}).addTo(map);
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Reference/MapServer/tile/{{z}}/{{y}}/{{x}}', {{ maxZoom: 16 }}).addTo(map);
PTS.forEach(m => L.circleMarker([m.lat, m.lng], {{ radius: 8, color: '#fff', weight: 2, fillColor: '#2c1c3d', fillOpacity: 1 }}).addTo(map).bindPopup('<strong>' + m.nom + '</strong>'));
</script>"""


def schedule_html(cours, show_studio=False, heading="h3"):
    by_day = defaultdict(list)
    for c in cours:
        by_day[c["jour"]].append(c)
    out = []
    for j in sorted(by_day, key=lambda d: JOURS.index(d) if d in JOURS else 9):
        rows = []
        for c in sorted(by_day[j], key=lambda c: c["debut"]):
            t = esc(c["debut"] + (" – " + c["fin"] if c["fin"] else ""))
            who = (f' · <a href="{studio_page(c["studio"])}">{esc(c["studio"])}</a> <span class="s">({esc(c["arr"])})</span>'
                   if show_studio else "")
            rows.append(f'<tr><td class="t">{t}</td><td>{esc(c["type"])}{who}</td>'
                        f'<td class="s"><a href="{style_page(c["type_simple"])}">{esc(c["type_simple"])}</a></td></tr>')
        out.append(f'<div class="day-block"><{heading}>{esc(j)}</{heading}><table class="slots">{"".join(rows)}</table></div>')
    return "\n".join(out)


def list_fr(items):
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " et " + items[-1]


# --------------------------------------------------------------------------- studio pages
def build_studio(s, studios, chrome_parts):
    n = len(s["cours"])
    cr = Counter(c["creneau"] for c in s["cours"])
    jours = [j for j in JOURS if any(c["jour"] == j for c in s["cours"])]
    styles_links = ", ".join(f'<a href="{style_page(t)}">{esc(t)}</a>' for t in s["styles"])
    loc = f'{s["quartier"]}, {s["arr"]}' if s["quartier"] and s["quartier"] != s["arr"] else s["arr"]
    title = f'{s["name"]} — cours de yoga {s["arr"]} : horaires et planning | Yoga In Lyon'
    desc = (f'{s["name"]} ({loc}) : {plural(n, "cours", "cours")} de yoga par semaine, '
            f'{list_fr(s["styles"][:3])}. Horaires vérifiés jour par jour.')

    # texte généré à partir des données (unique pour chaque studio)
    parts = [f'{esc(s["name"])} propose {plural(n, "cours de yoga", "cours de yoga")} par semaine '
             f'dans le quartier {esc(s["quartier"])} ({esc(s["arr"])}).']
    if len(s["styles"]) > 1:
        parts.append(f'Le style le plus représenté est le {esc(s["styles"][0])}, aux côtés de '
                     f'{esc(list_fr(s["styles"][1:]))}.')
    else:
        parts.append(f'Le studio est spécialisé en {esc(s["styles"][0])}.')
    moments = [(cr.get("Matin", 0), "le matin"), (cr.get("Midi", 0), "le midi"),
               (cr.get("Après-midi", 0), "l'après-midi"), (cr.get("Soir", 0), "en soirée")]
    moments = [f"{k} {m}" for k, m in moments if k]
    if len(jours) == 7:
        quand = "tous les jours de la semaine"
    elif jours == JOURS[:5]:
        quand = "du lundi au vendredi"
    elif jours == JOURS[:6]:
        quand = "du lundi au samedi"
    else:
        quand = "le " + list_fr([j.lower() for j in jours])
    parts.append(f'Les cours ont lieu {quand}, dont {list_fr(moments)}.')
    auto = " ".join(parts)
    intro = (f'<p>{esc(s["desc"])}</p>' if s["desc"] else "") + f"<p>{auto}</p>"

    same = [o for o in studios.values() if o["arr"] == s["arr"] and o["name"] != s["name"]]
    near = "".join(f'<a class="item" href="{studio_page(o["name"])}"><strong>{esc(o["name"])}</strong>'
                   f'<span>{esc(o["quartier"])} · {plural(len(o["cours"]), "cours", "cours")}/sem. · {esc(list_fr(o["styles"][:3]))}</span></a>'
                   for o in same)
    near_html = (f'<div class="section"><h2>Autres studios de yoga · {esc(s["arr"])}</h2>'
                 f'<div class="studio-list">{near}</div></div>') if same else ""

    body = f"""
<nav class="crumbs" aria-label="Fil d'Ariane"><a href="/">Accueil</a> › <a href="Studios.html">Studios</a> › <a href="{arr_page(s['arr'])}">{esc(s['arr'])}</a> › {esc(s['name'])}</nav>
<div class="quartier-hero">
  <div class="eyebrow">{esc(loc)}</div>
  <h1>{esc(s['name'])} : cours de yoga à {esc(s['quartier'] if s['quartier'] != s['arr'] else s['arr'])}</h1>
</div>
<div class="seo-intro">{intro}</div>
<div class="facts">
  <div class="fact"><div class="k">Adresse</div><div class="v">{esc(s['adresse'])}</div></div>
  <div class="fact"><div class="k">Quartier</div><div class="v"><a href="{arr_page(s['arr'])}">{esc(loc)}</a></div></div>
  <div class="fact"><div class="k">Styles</div><div class="v">{styles_links}</div></div>
  <div class="fact"><div class="k">Cours par semaine</div><div class="v">{n}</div></div>
  <div class="fact"><div class="k">Site du studio</div><div class="v"><a href="{esc(s['site'])}" target="_blank" rel="noopener">Réserver sur leur site →</a></div></div>
</div>
<div class="section">
  <h2>Planning de la semaine</h2>
  {schedule_html(s['cours'])}
  <p class="note">Horaires relevés sur le site du studio. Vérifiez auprès de {esc(s['name'])} avant de vous déplacer (vacances, cours complets).</p>
</div>
{'<div class="section"><div id="studio-map"></div></div>' if s['geo'] else ''}
{near_html}
<div class="section"><div class="pills"><a href="{arr_page(s['arr'])}">Tout le yoga · {esc(s['arr'])}</a><a href="{PLANNING}">Planning de tous les studios</a></div></div>
"""
    gym = {"@context": "https://schema.org", "@type": "ExerciseGym", "name": s["name"],
           "url": BASE + studio_page(s["name"]), "sameAs": s["site"], "address": postal(s["adresse"]),
           "description": re.sub(r"<[^>]+>", "", auto)}
    if s["geo"]:
        gym["geo"] = {"@type": "GeoCoordinates", "latitude": s["geo"][0], "longitude": s["geo"][1]}
    ld = [gym, breadcrumb([("Accueil", "/"), ("Studios", "Studios.html"), (s["arr"], arr_page(s["arr"])),
                           (s["name"], studio_page(s["name"]))])]
    return page_shell(chrome_parts, title=title, desc=desc, canonical=studio_page(s["name"]), body=body, ld=ld,
                      map_js=map_script([(s["name"], s["geo"])]) if s["geo"] else "")


# --------------------------------------------------------------------------- style pages
def build_style(ts, data, studios, chrome_parts):
    meta = STYLES[ts]
    cours = [c for c in data if c["type_simple"] == ts]
    sts = Counter(c["studio"] for c in cours)
    arrs = sorted({c["arr"] for c in cours}, key=lambda a: (a == "Villeurbanne", len(a), a))
    title = f'{meta["titre"]} : {plural(len(sts), "studio", "studios")}, {len(cours)} cours/semaine | Yoga In Lyon'
    desc = (f'{meta["titre"]} : {len(cours)} créneaux par semaine dans {plural(len(sts), "studio", "studios")} '
            f'vérifiés ({list_fr(arrs[:4])}…). Horaires jour par jour.')
    items = "".join(f'<a class="item" href="{studio_page(n)}"><strong>{esc(n)}</strong>'
                    f'<span>{esc(studios[n]["quartier"])} · {esc(studios[n]["arr"])} · {plural(k, "cours", "cours")}/sem.</span></a>'
                    for n, k in sts.most_common())
    others = "".join(f'<a href="{v["slug"]}.html">{esc(k)}</a>' for k, v in STYLES.items() if k != ts)
    body = f"""
<nav class="crumbs" aria-label="Fil d'Ariane"><a href="/">Accueil</a> › <a href="{PLANNING}">Planning</a> › {esc(ts)}</nav>
<div class="quartier-hero">
  <div class="eyebrow">Yoga In Lyon · {len(cours)} cours par semaine</div>
  <h1>{esc(meta['titre'])}</h1>
</div>
<div class="seo-intro">{meta['intro']}</div>
<div class="section"><h2>Les studios qui proposent ce style à Lyon</h2><div class="studio-list">{items}</div></div>
<div class="section"><h2>Tous les cours de {esc(ts)} de la semaine</h2>{schedule_html(cours, show_studio=True)}
<p class="note">Horaires relevés sur les sites des studios. Vérifiez auprès du studio avant de vous déplacer.</p></div>
<div class="section"><h2>Les autres styles de yoga à Lyon</h2><div class="pills">{others}</div></div>
"""
    ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": meta["titre"],
           "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": BASE + studio_page(n), "name": n}
                               for i, (n, _) in enumerate(sts.most_common())]},
          breadcrumb([("Accueil", "/"), ("Planning", PLANNING), (ts, meta["slug"] + ".html")])]
    return page_shell(chrome_parts, title=title, desc=desc, canonical=meta["slug"] + ".html", body=body, ld=ld)


# --------------------------------------------------------------------------- patches
def patch_common(text, studios, styles_present):
    return ensure_extra_css(fix_links(text, studios, styles_present))


def fix_links(text, studios, styles_present):
    # Accueil.html -> /
    text = re.sub(r'href="(?:\./)?Accueil\.html"', 'href="/"', text)

    # liens studio -> page studio
    def repl(m):
        name = urllib.parse.unquote(html.unescape(m.group(1)))
        return f'href="{studio_page(name)}"' if name in studios else m.group(0)
    text = re.sub(r'href="Yoga_a_Lyon_Planning\.html\?studio=([^"]+)"', repl, text)
    text = text.replace(">Voir leur planning →<", ">Voir le studio et ses horaires →<")

    # colonne Réseaux (liens vides) -> Styles de yoga
    styles_col = ('<div class="nav-col">\n        <div class="head">Styles de yoga</div>\n'
                  + "".join(f'        <a href="{STYLES[t]["slug"]}.html">{esc(t)}</a>\n' for t in STYLES if t in styles_present)
                  + "      </div>")
    text = re.sub(r'<div class="nav-col">\s*<div class="head">Réseaux</div>\s*(?:<a href="#">[^<]*</a>\s*)+</div>',
                  lambda m: styles_col, text)
    return text


def patch_quartier(text, arr, data, studios):
    intro = QUARTIERS.get(arr, "")
    if intro:
        text = replace_block(text, "intro", f'<div class="seo-intro">{intro}</div>',
                             anchor_before='<div class="map-section">')
    text = re.sub(r'<div class="studio-name">(.*?)</div>', r'<h3 class="studio-name">\1</h3>', text)
    present = Counter(c["type_simple"] for c in data if c["arr"] == arr)
    pills = "".join(f'<a href="{style_page(t)}">{esc(t)} à Lyon</a>' for t, _ in present.most_common() if t in STYLES)
    if pills:
        text = replace_block(text, "styles", f'<div class="other-quartiers"><h2>Les styles de yoga '
                             f'pratiqués · {esc(arr)}</h2><div class="links">{pills}</div></div>',
                             anchor_before='<div class="other-quartiers">')
    bc = jsonld(breadcrumb([("Accueil", "/"), ("Studios", "Studios.html"), (arr, arr_page(arr))]))
    text = replace_block(text, "breadcrumb", bc, anchor_before="</head>")
    return text


def patch_planning(text, data, styles_present):
    # rendu statique du planning : visible par Google, remplacé par le JS au chargement
    static = '<div class="seo-static">' + schedule_html(data, show_studio=True, heading="h2") + "</div>"
    text = re.sub(r'(<div id="results">)(?:<!--seo:static-->.*?<!--/seo:static-->)?',
                  lambda m: m.group(1) + "<!--seo:static-->" + static + "<!--/seo:static-->", text, count=1, flags=re.S)
    pills = "".join(f'<a href="{STYLES[t]["slug"]}.html">{esc(t)}</a>' for t in STYLES if t in styles_present)
    text = replace_block(text, "styles", f'<div class="section"><h2>Le yoga à Lyon par style</h2>'
                         f'<div class="pills">{pills}</div></div>', anchor_before='<footer class="site-footer">')
    return text


def patch_home(text, styles_present):
    pills = "".join(f'<a href="{STYLES[t]["slug"]}.html">{esc(t)}</a>' for t in STYLES if t in styles_present)
    block = (f'<section class="quartiers-section"><div class="inner"><h2>Le yoga par style</h2>'
             f'<div class="quartiers-links">{pills}</div></div></section>')
    if "<!--seo:homestyles-->" in text:
        return replace_block(text, "homestyles", block)
    i = text.find('<section class="quartiers-section">')
    if i >= 0:
        j = text.find("</section>", i) + len("</section>")
        return text[:j] + "\n<!--seo:homestyles-->" + block + "<!--/seo:homestyles-->" + text[j:]
    return text


# --------------------------------------------------------------------------- main
def main(site):
    site = Path(site).resolve()
    data, studios, planning = load(site)
    styles_present = {c["type_simple"] for c in data}
    chrome_parts = chrome(site, studios, styles_present)
    report = []

    generated = []
    for s in studios.values():
        fn = studio_page(s["name"])
        (site / fn).write_text(build_studio(s, studios, chrome_parts), encoding="utf-8")
        generated.append(fn)
    for ts in STYLES:
        if ts in styles_present:
            fn = STYLES[ts]["slug"] + ".html"
            (site / fn).write_text(build_style(ts, data, studios, chrome_parts), encoding="utf-8")
            generated.append(fn)
    unknown = styles_present - set(STYLES)
    if unknown:
        report.append("Styles sans texte dans seo_content.py : " + ", ".join(sorted(unknown)))

    # pages existantes
    arr_by_page = {arr_page(a): a for a in {c["arr"] for c in data}}
    (site / PLANNING).write_text(planning, encoding="utf-8")
    for p in sorted(site.glob("*.html")):
        if p.name in generated:
            continue
        t = p.read_text(encoding="utf-8")
        t0 = t
        t = patch_common(t, studios, styles_present)
        if p.name in arr_by_page:
            t = patch_quartier(t, arr_by_page[p.name], data, studios)
        if p.name == PLANNING:
            t = patch_planning(t, data, styles_present)
        if p.name in ("index.html", "Accueil.html"):
            t = patch_home(t, styles_present)
        if t != t0:
            p.write_text(t, encoding="utf-8")

    # sitemap / robots / htaccess
    pages = sorted(p.name for p in site.glob("*.html") if p.name not in ("Accueil.html",) and not p.name.startswith("_"))
    urls = [BASE] + [BASE + n for n in pages if n != "index.html"]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{esc(u)}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls]
    sm.append("</urlset>")
    (site / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")
    (site / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n", encoding="utf-8")
    ht = site / ".htaccess"
    src_ht = Path(__file__).resolve().parent / "htaccess.txt"
    if not ht.exists() and src_ht.exists():
        ht.write_text(src_ht.read_text(encoding="utf-8"), encoding="utf-8")
    elif ht.exists() and "seo-yoga-in-lyon" not in ht.read_text(encoding="utf-8"):
        report.append(".htaccess déjà présent : ajoute à la main le contenu de seo/htaccess.txt")

    # contrôles qualité des données
    for s in studios.values():
        if not s["geo"]:
            report.append(f"Pas de coordonnées GPS pour « {s['name']} »")
        if not re.search(r"\d{5}", s["adresse"] or ""):
            report.append(f"Adresse incomplète (pas de code postal) : « {s['name']} » → {s['adresse']}")
        kw = {"ashtanga": "Ashtanga", "iyengar": "Yoga Iyengar", "kundalini": "Yoga Kundalini", "vinyasa": "Yoga Vinyasa"}
        for k, ts in kw.items():
            if k in s["name"].lower() and ts not in s["styles"]:
                report.append(f"« {s['name']} » n'a aucun cours classé {ts} dans le planning")

    print(f"OK : {len(studios)} pages studio, {len(generated) - len(studios)} pages style, "
          f"{len(urls)} URL dans sitemap.xml")
    for r in report:
        print("  ⚠ " + r)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
