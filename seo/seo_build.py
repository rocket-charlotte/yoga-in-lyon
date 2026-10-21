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
from seo_content import (COLLECTIONS, GUIDES, QUARTIERS, STUDIOS_GUIDE, STYLE_GUIDE, STYLE_GUIDE_CHOIX,  # noqa: E402
                         STYLES)
from seo_profs import INDEPENDANTS, PROFS  # noqa: E402
import shutil  # noqa: E402

BASE = "https://yoga-in-lyon.fr/"
JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
CRENEAUX = ["Matin", "Midi", "Après-midi", "Soir"]
PLANNING = "Yoga_a_Lyon_Planning.html"
TODAY = date.today().isoformat()
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
        "novembre", "décembre"]


def _git_date():
    import subprocess
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs"], cwd=Path(__file__).resolve().parent.parent,
                             capture_output=True, text=True, timeout=10).stdout.strip()
        return out if re.fullmatch(r"\d{4}-\d{2}-\d{2}", out) else TODAY
    except Exception:
        return TODAY


DATA_DATE = _git_date()  # date du dernier commit = dernière vraie modification du contenu


def date_fr(iso):
    y, m, d = iso.split("-")
    return f"{int(d)}{'er' if d == '01' else ''} {MOIS[int(m) - 1]} {y}"
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


def arr_key(arr):
    m = re.search(r"\d+", arr)
    return int(m.group(0)) if m else 99


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


BRAND = " | Yoga In Lyon"


def brand(title):
    """Titre Google : marque ajoutée seulement si le tout reste sous ~60 caractères."""
    base = title.replace(BRAND, "").strip()
    return base + BRAND if len(base) + len(BRAND) <= 61 else base


def fit_desc(desc, n=158):
    desc = re.sub(r"\s+", " ", desc).strip()
    if len(desc) <= n:
        return desc
    i = desc[:n].rfind(". ")
    if i >= 100:
        return desc[:i + 1]
    cut = desc[:n - 1].rsplit(" ", 1)[0].rstrip(" ,;:(–-.")
    return cut + "…"


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
  .quartier-hero { max-width: 1180px; margin: 0 auto; padding: 56px 24px 10px; }
  .quartier-hero .eyebrow { font-size: 12px; font-weight: 700; color: #9B7FB0; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 10px; }
  .quartier-hero h1 { font-size: 32px; font-weight: 500; margin: 0 0 14px; }
  .seo-intro ul { color: #5a4a68; font-size: 15.5px; line-height: 1.7; max-width: 760px; margin: 0 0 14px; padding-left: 22px; }
  .faq h3 { font-size: 18px; font-weight: 500; margin: 22px 0 6px; }
  .seo-intro h2 { font-size: 24px; font-weight: 500; margin: 0 0 14px; }
"""


def ensure_extra_css(text):
    css = f'<style id="seo-extra">{EXTRA_CSS}</style>'
    if 'id="seo-extra"' in text:
        return re.sub(r'<style id="seo-extra">.*?</style>', lambda m: css, text, count=1, flags=re.S)
    return text.replace("</head>", css + "\n</head>", 1)


def page_shell(chrome_parts, *, title, desc, canonical, body, ld, map_js="", robots=""):
    style, header, footer = chrome_parts
    title, desc = brand(title), fit_desc(desc)
    leaflet_css = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />' if map_js else ""
    leaflet_js = '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>' if map_js else ""
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}<link rel="canonical" href="{BASE}{canonical}">
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
{FAVICON}
{GSTATIC}
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
def build_studio(s, studios, chrome_parts, profs_here=()):
    n = len(s["cours"])
    cr = Counter(c["creneau"] for c in s["cours"])
    jours = [j for j in JOURS if any(c["jour"] == j for c in s["cours"])]
    styles_links = ", ".join(f'<a href="{style_page(t)}">{esc(t)}</a>' for t in s["styles"])
    loc = f'{s["quartier"]}, {s["arr"]}' if s["quartier"] and s["quartier"] != s["arr"] else s["arr"]
    title = f'{s["name"]} : yoga {s["arr"]}, horaires et planning'
    if len(title) > 60:
        title = f'{s["name"]} : cours de yoga {s["arr"]}'
    if len(title) > 60:
        title = f'{s["name"]}, yoga {s["arr"]}'
    desc = (f'{s["name"]} ({loc}) : {plural(n, "cours", "cours")} de yoga par semaine, '
            f'{list_fr(s["styles"][:3])}. Horaires vérifiés jour par jour.')
    if len(desc) < 120:
        desc += " Adresse, plan d'accès et réservation."

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
    if len(same) < 4 and s["geo"]:
        others = [o for o in studios.values() if o["geo"] and o["name"] != s["name"] and o not in same]
        others.sort(key=lambda o: (o["geo"][0] - s["geo"][0]) ** 2 + ((o["geo"][1] - s["geo"][1]) * 0.7) ** 2)
        same += others[:4 - len(same)]
    near = "".join(f'<a class="item" href="{studio_page(o["name"])}"><strong>{esc(o["name"])}</strong>'
                   f'<span>{esc(o["quartier"])} · {plural(len(o["cours"]), "cours", "cours")}/sem. · {esc(list_fr(o["styles"][:3]))}</span></a>'
                   for o in same)
    near_html = (f'<div class="section"><h2>Studios de yoga à proximité</h2>'
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
  <p class="note">Horaires relevés sur le site du studio, mis à jour le {date_fr(DATA_DATE)}. Vérifiez auprès de {esc(s['name'])} avant de vous déplacer (vacances, cours complets).</p>
</div>
{'<div class="section"><div id="studio-map"></div></div>' if s['geo'] else ''}
{profs_section(profs_here, "Les profs de ce studio")}
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
    arrs = sorted({c["arr"] for c in cours}, key=arr_key)
    title = f'{meta["titre"]} : {plural(len(sts), "studio", "studios")}, {len(cours)} cours'
    desc = (f'{meta["titre"]} : {len(cours)} cours par semaine dans {plural(len(sts), "studio", "studios")} '
            f'({list_fr(arrs[:3])}). Horaires jour par jour, adresses et plan d\'accès des studios.')
    if len(desc) > 158:
        desc = desc.replace(", adresses et plan d'accès des studios.", " et adresses.")
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


# --------------------------------------------------------------------------- profs
def prof_page(p):
    return "prof-" + p["slug"] + ".html"


def resolve_profs(data, studios, report):
    out = []
    for raw in PROFS:
        p = dict(raw)
        if not p.get("nom"):
            report.append("Prof sans nom dans seo_profs.py : entrée ignorée")
            continue
        p["slug"] = slugify(p["nom"])
        p.setdefault("titre", "Professeure de yoga")
        cours = []
        for rule in p.get("cours", []):
            st = rule.get("studio")
            if st not in studios:
                report.append(f"Prof « {p['nom']} » : studio inconnu « {st} » (nom exact attendu)")
                continue
            m = (rule.get("match") or "").lower()
            found = [dict(c) for c in studios[st]["cours"] if m in c["type"].lower()]
            if not found:
                report.append(f"Prof « {p['nom']} » : aucun cours contenant « {rule.get('match')} » chez {st}")
            cours += found
        for x in p.get("extra", []):
            c = {"jour": x.get("jour", ""), "debut": norm_time(x.get("debut", "")), "fin": norm_time(x.get("fin", "")),
                 "type": x.get("type", "Yoga"), "type_simple": x.get("style"), "studio": None,
                 "lieu": x.get("lieu", ""), "arr": ""}
            cours.append(c)
        p["cours_all"] = cours
        p["studios"] = sorted({c["studio"] for c in cours if c.get("studio")})
        p["styles"] = [s for s, _ in Counter(c["type_simple"] for c in cours if c.get("type_simple")).most_common()]
        out.append(p)
    return out


def prof_card(p):
    img = (f'<img src="prof-{p["slug"]}{Path(p["photo"]).suffix.lower()}" alt="{esc(p["nom"])}" width="64" height="64" '
           f'loading="lazy" style="width:64px;height:64px;border-radius:50%;object-fit:cover;float:left;margin-right:14px">'
           if p.get("photo") else "")
    sub = " · ".join(x for x in [list_fr(p["styles"][:3]) if p["styles"] else "", list_fr(p["studios"][:2]) if p["studios"] else ""] if x)
    return (f'<a class="item" href="{prof_page(p)}">{img}<strong>{esc(p["nom"])}</strong>'
            f'<span>{esc(sub or p["titre"])}</span></a>')


def profs_section(profs, heading):
    if not profs:
        return ""
    return (f'<div class="section"><h2>{esc(heading)}</h2><div class="studio-list">'
            + "".join(prof_card(p) for p in profs) + "</div></div>")


def prof_schedule(cours):
    by_day = defaultdict(list)
    for c in cours:
        by_day[c["jour"]].append(c)
    out = []
    for j in sorted(by_day, key=lambda d: JOURS.index(d) if d in JOURS else 9):
        rows = []
        for c in sorted(by_day[j], key=lambda c: c["debut"]):
            t = esc(c["debut"] + (" – " + c["fin"] if c["fin"] else ""))
            where = (f'<a href="{studio_page(c["studio"])}">{esc(c["studio"])}</a> <span class="s">({esc(c["arr"])})</span>'
                     if c.get("studio") else esc(c.get("lieu") or ""))
            style = (f'<a href="{style_page(c["type_simple"])}">{esc(c["type_simple"])}</a>'
                     if c.get("type_simple") in STYLES else esc(c.get("type_simple") or ""))
            rows.append(f'<tr><td class="t">{t}</td><td>{esc(c["type"])} · {where}</td><td class="s">{style}</td></tr>')
        out.append(f'<div class="day-block"><h3>{esc(j)}</h3><table class="slots">{"".join(rows)}</table></div>')
    return "\n".join(out)


def build_prof(p, studios, chrome_parts):
    n = len(p["cours_all"])
    first = p["nom"].split()[0]
    lieux = p["studios"] + sorted({c["lieu"] for c in p["cours_all"] if c.get("lieu")})
    title = f'{p["nom"]}, {p["titre"].lower()} à Lyon'
    desc = (f'{p["nom"]}, {p["titre"].lower()} à Lyon'
            + (f' : {list_fr(p["styles"][:3])}' if p["styles"] else "")
            + (f', {plural(n, "cours", "cours")} par semaine' if n else "")
            + (f' ({list_fr(lieux[:3])})' if lieux else "") + ". Horaires et réservation.")
    photo = (f'<img src="prof-{p["slug"]}{Path(p["photo"]).suffix.lower()}" alt="{esc(p["nom"])}, {esc(p["titre"].lower())} à Lyon" '
             f'width="160" height="160" style="width:160px;height:160px;border-radius:50%;object-fit:cover;margin-bottom:18px">'
             if p.get("photo") else "")
    links = [(k, lbl) for k, lbl in (("reservation", "Réserver un cours →"), ("site", "Site web →"),
                                       ("instagram", "Instagram →")) if p.get(k)]
    facts = ""
    if p["styles"]:
        facts += ('<div class="fact"><div class="k">Styles</div><div class="v">'
                  + ", ".join(f'<a href="{style_page(s)}">{esc(s)}</a>' if s in STYLES else esc(s) for s in p["styles"])
                  + "</div></div>")
    if lieux:
        facts += ('<div class="fact"><div class="k">Où pratiquer avec ' + esc(first) + '</div><div class="v">'
                  + ", ".join(f'<a href="{studio_page(s)}">{esc(s)}</a>' if s in studios else esc(s) for s in lieux)
                  + "</div></div>")
    if n:
        facts += f'<div class="fact"><div class="k">Cours par semaine</div><div class="v">{n}</div></div>'
    if p.get("formation"):
        facts += f'<div class="fact"><div class="k">Formation</div><div class="v">{esc(p["formation"])}</div></div>'
    for k, lbl in links:
        facts += (f'<div class="fact"><div class="k">{"Réservation" if k == "reservation" else k.capitalize()}</div>'
                  f'<div class="v"><a href="{esc(p[k])}" target="_blank" rel="noopener">{lbl}</a></div></div>')
    bio = p.get("bio") or ""
    if bio and not bio.lstrip().startswith("<"):
        bio = f"<p>{esc(bio)}</p>"
    sched = (f'<div class="section"><h2>Les cours de {esc(first)} cette semaine</h2>{prof_schedule(p["cours_all"])}'
             f'<p class="note">Horaires relevés sur les sites des studios. Vérifiez avant de vous déplacer.</p></div>'
             if n else "")
    body = f"""
<nav class="crumbs" aria-label="Fil d'Ariane"><a href="/">Accueil</a> › <a href="Profs.html">Profs</a> › {esc(p['nom'])}</nav>
<div class="quartier-hero">
  {photo}
  <div class="eyebrow">{esc(p['titre'])} à Lyon</div>
  <h1>{esc(p['nom'])}</h1>
</div>
<div class="seo-intro">{bio}</div>
<div class="facts">{facts}</div>
{sched}
<div class="section"><div class="pills"><a href="Profs.html">Tous les profs de yoga à Lyon</a><a href="{PLANNING}">Planning de tous les studios</a></div></div>
"""
    person = {"@context": "https://schema.org", "@type": "Person", "name": p["nom"], "jobTitle": p["titre"],
              "url": BASE + prof_page(p), "address": {"@type": "PostalAddress", "addressLocality": "Lyon", "addressCountry": "FR"}}
    same = [p[k] for k in ("site", "instagram") if p.get(k)]
    if same:
        person["sameAs"] = same
    if p.get("photo"):
        person["image"] = BASE + f'prof-{p["slug"]}{Path(p["photo"]).suffix.lower()}'
    if p["studios"]:
        person["worksFor"] = [{"@type": "ExerciseGym", "name": s, "url": BASE + studio_page(s)} for s in p["studios"]]
    ld = [person, breadcrumb([("Accueil", "/"), ("Profs", "Profs.html"), (p["nom"], prof_page(p))])]
    return page_shell(chrome_parts, title=title, desc=desc, canonical=prof_page(p), body=body, ld=ld)


PROFS_OFFER = """
<div class="section seo-intro" id="vous-etes-prof">
  <h2>Vous êtes prof de yoga à Lyon ?</h2>
  <p>Yoga In Lyon vous crée <strong>gratuitement</strong> une page qui regroupe tous vos cours, quel que soit le studio, avec vos liens de réservation. Elle peut servir de lien unique dans votre bio Instagram, et vos élèves y trouvent tous vos créneaux au même endroit.</p>
  <p>Il suffit d'envoyer :</p>
  <ul>
    <li>une photo de vous (format carré de préférence) ;</li>
    <li>deux à six phrases de présentation : votre parcours, votre façon d'enseigner ;</li>
    <li>les studios et créneaux où vous enseignez, et vos cours hors studio (plein air, en ligne) ;</li>
    <li>vos liens : site, Instagram, réservation.</li>
  </ul>
  <p><a class="cta-btn" style="display:inline-block;padding:13px 26px;border-radius:999px;background:var(--brand-purple);color:#FBF8F4;font-weight:600" href="mailto:contact@yoga-in-lyon.fr?subject=Ma%20page%20prof%20sur%20Yoga%20In%20Lyon&amp;body=Bonjour%2C%0A%0ANom%20%3A%0APr%C3%A9sentation%20%3A%0AStudios%20et%20cr%C3%A9neaux%20%3A%0ACours%20hors%20studio%20%3A%0ASite%20%2F%20Instagram%20%2F%20r%C3%A9servation%20%3A%0A%0A(photo%20en%20pi%C3%A8ce%20jointe)">Créer ma page gratuitement</a></p>
  <p class="note">La page est en ligne sous quelques jours. Vous pouvez demander à la modifier ou à la retirer à tout moment.</p>
</div>
"""


def patch_profs_page(text, profs, studios):
    n = len(profs)
    title = "Profs de yoga à Lyon : trouvez votre professeur" if n else "Profs de yoga à Lyon"
    text = set_meta(text, title, "Les professeurs de yoga à Lyon : leurs cours dans les studios et en indépendant, "
                    "leurs styles et leurs horaires. Vous êtes prof ? Créez gratuitement votre page.")
    indep = [studios[s] for s in INDEPENDANTS if s in studios]
    indep_html = ""
    if indep:
        indep_html = ('<div class="section"><h2>Profs indépendants</h2><div class="studio-list">'
                      + "".join(f'<a class="item" href="{studio_page(s["name"])}"><strong>{esc(s["name"])}</strong>'
                                f'<span>{esc(s["quartier"])} · {plural(len(s["cours"]), "cours", "cours")}/sem. · '
                                f'{esc(list_fr(s["styles"][:3]))}</span></a>' for s in indep)
                      + "</div></div>")
    intro = ("<p>Un bon prof compte souvent plus que le studio. Retrouvez ici les professeurs de yoga qui enseignent "
             "à Lyon, où ils donnent leurs cours et comment réserver.</p>")
    block = (f'<div class="quartier-hero"><div class="eyebrow">Yoga In Lyon</div><h1>Profs de yoga à Lyon</h1></div>'
             f'<div class="seo-intro">{intro}</div>'
             + profs_section(profs, "Les profs") + indep_html + PROFS_OFFER
             + f'<div class="section"><div class="pills"><a href="Studios.html">Tous les studios</a>'
               f'<a href="{PLANNING}">Planning de la semaine</a></div></div>')
    text = re.sub(r'<section class="profs-section">.*?</section>\s*', "", text, count=1, flags=re.S)
    text = re.sub(r'<script>\s*function submitProfs.*?</script>\s*', "", text, count=1, flags=re.S)
    text = replace_block(text, "pageld", jsonld({"@context": "https://schema.org", "@type": "CollectionPage",
                         "name": "Profs de yoga à Lyon", "url": BASE + "Profs.html"})
                         + jsonld(breadcrumb([("Accueil", "/"), ("Profs", "Profs.html")])), anchor_before="</head>")
    return replace_block(text, "profs", block, anchor_before='<footer class="site-footer">')


def patch_about(text):
    return replace_block(text, "pageld", jsonld({"@context": "https://schema.org", "@type": "AboutPage",
                         "name": "Qui sommes-nous", "url": BASE + "A-propos.html",
                         "about": {"@id": BASE + "#organization"}})
                         + jsonld(breadcrumb([("Accueil", "/"), ("Qui sommes-nous", "A-propos.html")])),
                         anchor_before="</head>")


# --------------------------------------------------------------------------- guides
def minutes(h):
    m = re.fullmatch(r"(\d{2})h(\d{2})", h or "")
    return int(m.group(1)) * 60 + int(m.group(2)) if m else None


def bar_rows(rows, total, link=None):
    """rows = [(label, value, extra_cells)] → lignes de tableau avec une barre proportionnelle."""
    top = max(v for _, v, _ in rows) or 1
    out = []
    for label, v, extra in rows:
        lab = f'<a href="{link(label)}">{esc(label)}</a>' if link and link(label) else esc(label)
        out.append(f'<tr><td class="t">{lab}</td>{extra}<td style="width:42%"><div style="height:10px;border-radius:5px;'
                   f'background:var(--lavender);width:{v / top * 100:.0f}%"></div></td>'
                   f'<td class="s">{v} ({v / total * 100:.0f} %)</td></tr>')
    return '<table class="slots">' + "".join(out) + "</table>"


def article_shell(g, chrome_parts, body, studios):
    title = g["titre"]
    pub, mod = g["publie"], max(g["publie"], DATA_DATE)
    head = f"""
<nav class="crumbs" aria-label="Fil d'Ariane"><a href="/">Accueil</a> › <a href="guides.html">Guides</a> › {esc(g['court'])}</nav>
<div class="quartier-hero"><div class="eyebrow">Guide · mis à jour le {date_fr(mod)}</div><h1>{esc(title)}</h1></div>
<div class="seo-intro"><p><strong>{esc(g['chapo'])}</strong></p></div>
"""
    others = "".join(f'<a href="{o["slug"]}.html">{esc(o["court"])}</a>' for o in GUIDES if o["slug"] != g["slug"])
    tail = (f'<div class="section"><h2>À lire aussi</h2><div class="pills">{others}'
            f'<a href="Studios.html">Tous les studios</a><a href="{PLANNING}">Le planning de la semaine</a></div></div>')
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": title, "description": g["chapo"],
           "url": BASE + g["slug"] + ".html", "datePublished": pub, "dateModified": mod, "inLanguage": "fr-FR",
           "image": BASE + "banner_web.jpg",
           "author": {"@type": "Organization", "name": "Yoga In Lyon", "url": BASE},
           "publisher": {"@type": "Organization", "name": "Yoga In Lyon", "logo": {"@type": "ImageObject",
                                                                                  "url": BASE + "logo_web.png"}}},
          breadcrumb([("Accueil", "/"), ("Guides", "guides.html"), (g["court"], g["slug"] + ".html")])]
    return page_shell(chrome_parts, title=title, desc=g.get("desc", g["chapo"]), canonical=g["slug"] + ".html",
                      body=head + body + tail, ld=ld)


def build_guide_chiffres(g, data, studios, chrome_parts):
    n, ns = len(data), len(studios)
    st = Counter(c["type_simple"] for c in data).most_common()
    ar = sorted(Counter(c["arr"] for c in data).items(), key=lambda x: arr_key(x[0]))
    sts_by_arr = Counter(s["arr"] for s in studios.values())
    days = [(j, sum(1 for c in data if c["jour"] == j)) for j in JOURS]
    cren = [(k, sum(1 for c in data if c["creneau"] == k)) for k in ["Matin", "Midi", "Après-midi", "Soir"]]
    top_arr = max(ar, key=lambda x: x[1])
    busiest = max(days, key=lambda x: x[1])
    soir = dict(cren)["Soir"]
    week = [c for c in data if c["jour"] in JOURS[:5] and minutes(c["debut"]) is not None]
    first = min(week, key=lambda c: minutes(c["debut"]))
    last = max(data, key=lambda c: minutes(c["debut"]) or 0)
    durs = [(minutes(c["fin"]) - minutes(c["debut"]), c) for c in data if minutes(c["fin"]) and minutes(c["debut"])]
    longest = max(durs, key=lambda x: x[0])
    sunday = sorted({c["studio"] for c in data if c["jour"] == "Dimanche"})
    facts = "".join(f'<div class="fact"><div class="k">{k}</div><div class="v" style="font-size:26px;font-family:Fraunces,serif">{v}</div></div>'
                    for k, v in [("Studios", ns), ("Cours par semaine", n), ("Zones couvertes", len(ar)),
                                 ("Styles", len(st))])
    body = f"""
<div class="facts">{facts}</div>
<div class="section"><h2>Le {esc(st[0][0])} représente {st[0][1] / n * 100:.0f} % des cours</h2>
{bar_rows([(k, v, "") for k, v in st], n, link=lambda k: style_page(k) if k in STYLES else None)}</div>
<div class="section"><h2>Le {esc(arr_label(top_arr[0]) if top_arr[0] != "Villeurbanne" else top_arr[0])} concentre le plus de cours</h2>
{bar_rows([(a, v, f'<td class="s">{plural(sts_by_arr[a], "studio", "studios")}</td>') for a, v in ar], n, link=arr_page)}</div>
<div class="section"><h2>Le soir domine : {soir / n * 100:.0f} % des cours ont lieu en soirée</h2>
{bar_rows([(k, v, "") for k, v in cren], n)}
<h3 style="font-size:18px;font-weight:500;margin:26px 0 8px">Le {busiest[0].lower()} est le jour le plus chargé</h3>
{bar_rows([(k, v, "") for k, v in days], n)}</div>
<div class="section seo-intro"><h2>Les records de la semaine</h2>
<p><strong>Le plus matinal :</strong> {esc(first['type'])} chez <a href="{studio_page(first['studio'])}">{esc(first['studio'])}</a>, le {first['jour'].lower()} à {first['debut']}.</p>
<p><strong>Le plus tardif :</strong> {esc(last['type'])} chez <a href="{studio_page(last['studio'])}">{esc(last['studio'])}</a>, le {last['jour'].lower()} à {last['debut']}.</p>
<p><strong>Le plus long :</strong> {esc(longest[1]['type'])} chez <a href="{studio_page(longest[1]['studio'])}">{esc(longest[1]['studio'])}</a>, {longest[0] // 60}h{longest[0] % 60:02d} de pratique.</p>
<p><strong>Le midi :</strong> {dict(cren)['Midi']} cours entre 12h et 14h, à retrouver sur notre page <a href="{COLLECTIONS['midi']['slug']}.html">yoga le midi</a>.</p>
<p><strong>Le dimanche :</strong> {plural(len(sunday), "studio ouvre", "studios ouvrent")}, voir les <a href="{COLLECTIONS['weekend']['slug']}.html">cours du week-end</a>.</p></div>
<div class="section seo-intro"><h2>Méthode</h2>
<p>Ces chiffres sont calculés à partir du planning de Yoga In Lyon : les cours réguliers relevés sur les sites de {ns} studios de Lyon et Villeurbanne, mis à jour le {date_fr(DATA_DATE)}. Les stages, ateliers et cours ponctuels ne sont pas comptés. Ils se mettent à jour automatiquement avec le planning.</p>
<p>Journalistes et blogueurs : ces chiffres sont libres de reprise avec un lien vers yoga-in-lyon.fr. Pour un classement sur mesure, écrivez à contact@yoga-in-lyon.fr.</p></div>
"""
    g = dict(g, titre=f"Le yoga à Lyon en chiffres : {ns} studios, {n} cours par semaine")
    return article_shell(g, chrome_parts, body, studios)


def build_guide_styles(g, data, studios, chrome_parts):
    cnt = Counter(c["type_simple"] for c in data)
    sts = defaultdict(set)
    for c in data:
        sts[c["type_simple"]].add(c["studio"])
    rows = "".join(
        f'<tr><td class="t"><a href="{style_page(s)}">{esc(s)}</a></td><td>{esc(r)}</td><td>{esc(w)}</td>'
        f'<td class="s">{cnt[s]} cours, {plural(len(sts[s]), "studio", "studios")}</td></tr>'
        for s, (r, w, _) in STYLE_GUIDE.items() if cnt.get(s))
    detail = "".join(f'<p><strong><a href="{style_page(s)}">{esc(s)}</a>.</strong> {esc(d)}</p>'
                     for s, (_, _, d) in STYLE_GUIDE.items() if cnt.get(s))
    body = f"""
<div class="section"><h2>Les styles de yoga en un coup d'œil</h2>
<table class="slots"><tr><td class="t"><strong>Style</strong></td><td><strong>Rythme</strong></td><td><strong>Pour qui</strong></td><td class="s"><strong>À Lyon chaque semaine</strong></td></tr>{rows}</table></div>
<div class="section seo-intro"><h2>À quoi ressemble un cours</h2>{detail}</div>
<div class="section seo-intro">{STYLE_GUIDE_CHOIX}</div>
<div class="section"><h2>Trouver un cours adapté</h2><div class="pills">{collections_pills()}</div></div>
"""
    return article_shell(g, chrome_parts, body, studios)


def build_guides_index(chrome_parts):
    items = "".join(f'<a class="item" href="{g["slug"]}.html"><strong>{esc(g["court"])}</strong>'
                    f'<span>{esc(g["chapo"])}</span></a>' for g in GUIDES)
    body = f"""
<nav class="crumbs" aria-label="Fil d'Ariane"><a href="/">Accueil</a> › Guides</nav>
<div class="quartier-hero"><div class="eyebrow">Yoga In Lyon</div><h1>Guides du yoga à Lyon</h1></div>
<div class="seo-intro"><p>Nos guides pour choisir son cours, comprendre les styles de yoga et découvrir la pratique à Lyon, à partir des plannings de tous les studios.</p></div>
<div class="section"><div class="studio-list">{items}</div></div>
"""
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": "Guides du yoga à Lyon",
           "url": BASE + "guides.html"}, breadcrumb([("Accueil", "/"), ("Guides", "guides.html")])]
    return page_shell(chrome_parts, title="Guides du yoga à Lyon : styles, quartiers, horaires",
                      desc="Les guides de Yoga In Lyon : quel style de yoga choisir pour débuter, le yoga à Lyon en "
                           "chiffres, où et quand pratiquer. Basés sur les plannings de tous les studios.",
                      canonical="guides.html", body=body, ld=ld)


def build_404(chrome_parts):
    body = f"""
<div class="quartier-hero"><div class="eyebrow">Erreur 404</div><h1>Cette page n'existe pas (ou plus)</h1></div>
<div class="seo-intro"><p>Le lien est peut-être ancien, ou le studio a changé de nom. Voici de quoi retrouver votre cours :</p></div>
<div class="section"><div class="pills"><a href="/">Accueil</a><a href="Studios.html">Tous les studios</a><a href="{PLANNING}">Planning de la semaine</a><a href="guides.html">Guides</a></div></div>
"""
    return page_shell(chrome_parts, title="Page introuvable", desc="Cette page n'existe pas sur Yoga In Lyon.",
                      canonical="404.html", body=body, ld=[], robots='<meta name="robots" content="noindex">\n')


# --------------------------------------------------------------------------- thematic pages
COLLECTION_FILTERS = {
    "debutant": lambda c: re.search(r"niveau 1\b|niveaux 1|d[ée]butant|bases|tous niveaux|hatha 1\b|doux|douceur",
                                    c["type"], re.I),
    "prenatal": lambda c: re.search(r"pr[ée]natal", c["type"], re.I),
    "seniors": lambda c: re.search(r"s[ée]nior|adapt|chaise", c["type"], re.I),
    "midi": lambda c: c["creneau"] == "Midi",
    "weekend": lambda c: c["jour"] in ("Samedi", "Dimanche"),
    "croix-rousse": lambda c: "Croix-Rousse" in c["quartier"],
    "part-dieu": lambda c: "Part-Dieu" in c["quartier"],
}


def collections_pills(exclude=None):
    return "".join(f'<a href="{v["slug"]}.html">{esc(v["court"])}</a>'
                   for k, v in COLLECTIONS.items() if k != exclude)


def build_collection(key, data, studios, chrome_parts):
    meta = COLLECTIONS[key]
    cours = [c for c in data if COLLECTION_FILTERS[key](c)]
    sts = Counter(c["studio"] for c in cours)
    styles = [t for t, _ in Counter(c["type_simple"] for c in cours).most_common()]
    arrs = sorted({c["arr"] for c in cours}, key=arr_key)
    title = f'{meta["titre"]} : {len(cours)} cours, {plural(len(sts), "studio", "studios")}'
    desc = (f'{meta["titre"]} : {len(cours)} cours par semaine dans {plural(len(sts), "studio", "studios")} '
            f'vérifiés ({list_fr(arrs[:3])}). {list_fr(styles[:3])}. Horaires jour par jour.')
    items = "".join(f'<a class="item" href="{studio_page(n)}"><strong>{esc(n)}</strong>'
                    f'<span>{esc(studios[n]["quartier"])} · {esc(studios[n]["arr"])} · {plural(k, "cours", "cours")}/sem.</span></a>'
                    for n, k in sts.most_common())
    style_pills = "".join(f'<a href="{style_page(t)}">{esc(t)}</a>' for t in styles if t in STYLES)
    body = f"""
<nav class="crumbs" aria-label="Fil d'Ariane"><a href="/">Accueil</a> › <a href="{PLANNING}">Planning</a> › {esc(meta['court'])}</nav>
<div class="quartier-hero">
  <div class="eyebrow">Yoga In Lyon · {len(cours)} cours par semaine</div>
  <h1>{esc(meta['titre'])}</h1>
</div>
<div class="seo-intro">{meta['intro']}</div>
<div class="section"><h2>Les studios qui proposent ces cours</h2><div class="studio-list">{items}</div></div>
<div class="section"><h2>Tous les créneaux de la semaine</h2>{schedule_html(cours, show_studio=True)}
<p class="note">Horaires relevés sur les sites des studios. Vérifiez auprès du studio avant de vous déplacer.</p></div>
<div class="section"><h2>Les styles de yoga concernés</h2><div class="pills">{style_pills}</div></div>
<div class="section"><h2>Trouver un cours selon vos envies</h2><div class="pills">{collections_pills(key)}</div></div>
"""
    ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": meta["titre"],
           "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": BASE + studio_page(n), "name": n}
                               for i, (n, _) in enumerate(sts.most_common())]},
          breadcrumb([("Accueil", "/"), ("Planning", PLANNING), (meta["court"], meta["slug"] + ".html")])]
    return page_shell(chrome_parts, title=title, desc=desc, canonical=meta["slug"] + ".html", body=body, ld=ld)


# --------------------------------------------------------------------------- patches
def set_meta(text, title, desc):
    """Remplace <title>, meta description et leurs équivalents Open Graph / Twitter."""
    t, d = esc(brand(title)), esc(fit_desc(desc))
    text = re.sub(r"<title>.*?</title>", lambda m: f"<title>{t}</title>", text, count=1, flags=re.S)
    for attr, val in (('name="description"', d), ('property="og:title"', t), ('property="og:description"', d),
                      ('name="twitter:title"', t), ('name="twitter:description"', d)):
        text = re.sub(rf'<meta {attr} content="[^"]*">', lambda m, a=attr, v=val: f'<meta {a} content="{v}">', text)
    return text


GSTATIC = '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
FAVICON = ('<link rel="icon" href="/favicon.ico" sizes="any">'
           '<link rel="icon" type="image/png" sizes="48x48" href="/favicon-48.png">'
           '<link rel="apple-touch-icon" href="/apple-touch-icon.png">')


def ensure_favicon(text):
    if "fonts.gstatic.com" not in text:
        text = text.replace("</head>", GSTATIC + "\n</head>", 1)
    if 'rel="apple-touch-icon"' in text:
        return text
    return text.replace("</head>", FAVICON + "\n</head>", 1)

def patch_common(text, studios, styles_present):
    return ensure_favicon(ensure_extra_css(fix_links(text, studios, styles_present)))


def fix_links(text, studios, styles_present):
    # Accueil.html -> /
    text = re.sub(r'href="(?:\./)?Accueil\.html"', 'href="/"', text)

    # liens studio -> page studio
    def repl(m):
        name = urllib.parse.unquote(html.unescape(m.group(1)))
        return f'href="{studio_page(name)}"' if name in studios else m.group(0)
    text = re.sub(r'href="Yoga_a_Lyon_Planning\.html\?studio=([^"]+)"', repl, text)
    text = text.replace(">Voir leur planning →<", ">Voir le studio et ses horaires →<")

    # lien Guides dans l'en-tête et le pied de page
    if 'href="guides.html"' not in text:
        text = re.sub(r'(<nav>.*?)(\s*<a href="A-propos\.html")', r'\1\n    <a href="guides.html" class="">Guides</a>\2',
                      text, count=1, flags=re.S)
        text = text.replace('<a href="Yoga_a_Lyon_Planning.html">Planning</a>',
                            '<a href="Yoga_a_Lyon_Planning.html">Planning</a>\n        <a href="guides.html">Guides</a>', 1)
    # colonne Réseaux (liens vides) -> Styles de yoga
    styles_col = ('<div class="nav-col">\n        <div class="head">Styles de yoga</div>\n'
                  + "".join(f'        <a href="{STYLES[t]["slug"]}.html">{esc(t)}</a>\n' for t in STYLES if t in styles_present)
                  + "      </div>\n      <div class=\"nav-col\">\n        <div class=\"head\">Trouver un cours</div>\n"
                  + "".join(f'        <a href="{v["slug"]}.html">{esc(v["court"])}</a>\n' for v in COLLECTIONS.values())
                  + "      </div>")
    text = re.sub(r'<div class="nav-col">\s*<div class="head">Réseaux</div>\s*(?:<a href="#">[^<]*</a>\s*)+</div>',
                  lambda m: styles_col, text)
    return text


def patch_quartier(text, arr, data, studios):
    cours = [c for c in data if c["arr"] == arr]
    sts = [s for s in studios.values() if s["arr"] == arr]
    quartiers = []
    for s in sts:
        for q in re.split(r"\s*/\s*|\s*\(", s["quartier"]):
            q = q.strip(" )")
            if q and q != arr and not q.startswith(("Cours", "Lyon")) and q not in quartiers:
                quartiers.append(q)
    styles = [x for x, _ in Counter(c["type_simple"] for c in cours).most_common(3)]
    where = "à Villeurbanne" if arr == "Villeurbanne" else f"dans le {arr_label(arr)}"
    short = [re.sub(r"^Yoga ", "", s) for s in styles[:2]]
    text = set_meta(text, f"Yoga {arr} : {plural(len(sts), 'studio', 'studios')}, {len(cours)} cours par semaine",
                    f"{plural(len(sts), 'studio', 'studios')} de yoga {where}"
                    + (f" ({list_fr(quartiers[:2])})" if quartiers else "")
                    + f", {len(cours)} cours par semaine : {list_fr(short)}. Adresses et horaires.")
    text = replace_block(text, "gridh2", f'<div class="section" style="padding-bottom:0"><h2>Les studios de yoga · '
                         f'{esc(arr)}</h2></div>', anchor_before='<div class="studios-grid-wrap">')
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
    n_s = len({c["studio"] for c in data})
    text = set_meta(text, f"Planning des cours de yoga à Lyon : {len(data)} cours par semaine",
                    f"Le planning complet des cours de yoga à Lyon : {len(data)} créneaux vérifiés dans {n_s} studios, "
                    "filtrables par style, jour, horaire et arrondissement.")
    text = re.sub(r'<img src="banner_web\.jpg" alt="">',
                  '<img src="banner_web.jpg" alt="Cours de yoga au bord de la Saône à Lyon" width="1920" height="814">',
                  text, count=1)
    text = replace_block(text, "updated", f'<p class="note" style="max-width:1180px;margin:0 auto;padding:0 24px">'
                         f'Planning mis à jour le {date_fr(DATA_DATE)}.</p>', anchor_before='<div class="layout">')
    text = replace_block(text, "pageld", jsonld({"@context": "https://schema.org", "@type": "CollectionPage",
                         "name": "Planning des cours de yoga à Lyon", "url": BASE + PLANNING,
                         "dateModified": DATA_DATE, "isPartOf": {"@id": BASE + "#website"}})
                         + jsonld(breadcrumb([("Accueil", "/"), ("Planning", PLANNING)])), anchor_before="</head>")
    # rendu statique du planning : visible par Google, remplacé par le JS au chargement
    static = '<div class="seo-static">' + schedule_html(data, show_studio=True, heading="h2") + "</div>"
    text = re.sub(r'(<div id="results">)(?:<!--seo:static-->.*?<!--/seo:static-->)?',
                  lambda m: m.group(1) + "<!--seo:static-->" + static + "<!--/seo:static-->", text, count=1, flags=re.S)
    pills = "".join(f'<a href="{STYLES[t]["slug"]}.html">{esc(t)}</a>' for t in STYLES if t in styles_present)
    text = replace_block(text, "styles", f'<div class="section"><h2>Le yoga à Lyon par style</h2>'
                         f'<div class="pills">{pills}</div><h2 style="margin-top:28px">Trouver un cours selon vos envies</h2>'
                         f'<div class="pills">{collections_pills()}</div></div>', anchor_before='<footer class="site-footer">')
    return text


def patch_studios_page(text, data, studios):
    n_s, n_c = len(studios), len(data)
    text = set_meta(text, f"Studios de yoga à Lyon : adresses, styles et horaires",
                    f"Les {n_s} studios de yoga de Lyon et Villeurbanne, vérifiés à la main : adresse, quartier, "
                    f"styles et planning de chaque studio.")
    text = re.sub(r"<h1>Trouver un studio de yoga à Lyon</h1>",
                  f"<h1>Studios de yoga à Lyon : les {n_s} adresses vérifiées</h1>", text, count=1)

    by_arr = defaultdict(list)
    for s in studios.values():
        by_arr[s["arr"]].append(s)
    arr_order = sorted(by_arr, key=arr_key)
    rows = "".join(
        f'<tr><td class="t"><a href="{arr_page(a)}">{esc(a)}</a></td><td>'
        + ", ".join(f'<a href="{studio_page(s["name"])}">{esc(s["name"])}</a>' for s in by_arr[a])
        + f'</td><td class="s">{sum(len(s["cours"]) for s in by_arr[a])} cours/sem.</td></tr>'
        for a in arr_order)
    top_arr = max(by_arr, key=lambda a: len(by_arr[a]))
    sunday = sorted({c["studio"] for c in data if c["jour"] == "Dimanche"})
    weekday = [c for c in data if c["jour"] in JOURS[:5]]
    earliest = min(weekday, key=lambda c: c["debut"])
    midi = [c for c in data if c["creneau"] == "Midi"]
    deb = Counter(c["studio"] for c in data if COLLECTION_FILTERS["debutant"](c)).most_common(3)
    faq = [
        ("Combien y a-t-il de studios de yoga à Lyon ?",
         f"Yoga In Lyon référence {n_s} studios de yoga vérifiés à Lyon et Villeurbanne, qui proposent ensemble "
         f"{n_c} cours par semaine. Le secteur le plus fourni est le {arr_label(top_arr)} avec "
         f"{len(by_arr[top_arr])} studios."),
        ("Quel studio de yoga choisir pour débuter à Lyon ?",
         f"Pour débuter, choisissez un cours de Hatha, un cours doux ou un cours « tous niveaux ». Les studios qui en "
         f"proposent le plus sont {list_fr([n for n, _ in deb])}. Tous les cours adaptés sont réunis sur notre page "
         f'<a href="{COLLECTIONS["debutant"]["slug"]}.html">yoga pour débutants à Lyon</a>.'),
        ("Où faire du yoga le dimanche à Lyon ?",
         f"{plural(len(sunday), 'studio propose', 'studios proposent')} des cours le dimanche : {list_fr(sunday)}. "
         f'Voir tous les <a href="{COLLECTIONS["weekend"]["slug"]}.html">cours du week-end</a>.'),
        ("Peut-on faire du yoga le midi à Lyon ?",
         f"Oui : {len(midi)} cours ont lieu le midi chaque semaine, surtout à Part-Dieu, aux Brotteaux et à la "
         f'Croix-Rousse. Retrouvez-les sur la page <a href="{COLLECTIONS["midi"]["slug"]}.html">yoga le midi à Lyon</a>.'),
        ("Quel est le cours de yoga le plus tôt à Lyon ?",
         f"En semaine, le premier cours commence à {earliest['debut']} : {earliest['type']} chez "
         f"{earliest['studio']} ({earliest['arr']})."),
    ]
    faq_html = "".join(f"<h3>{esc(q)}</h3><p>{a}</p>" for q, a in faq)
    faq_ld = jsonld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}}
        for q, a in faq]})
    block = (f'<div class="section seo-intro">{STUDIOS_GUIDE}</div>'
             f'<div class="section"><h2>Les studios de yoga par arrondissement</h2><table class="slots">{rows}</table></div>'
             f'<div class="section"><h2>Trouver un cours selon vos envies</h2><div class="pills">{collections_pills()}</div></div>'
             f'<div class="section seo-intro faq"><h2>Questions fréquentes</h2>{faq_html}</div>')
    text = replace_block(text, "guide", block, anchor_before='<div class="cta-manage">')
    text = replace_block(text, "faqld", faq_ld, anchor_before="</head>")
    return text


def patch_home(text, styles_present, data, studios):
    n_s, n_c = len(studios), len(data)
    text = set_meta(text, f"Studio de yoga à Lyon : les {n_s} adresses et leurs cours",
                    f"Trouvez votre studio de yoga à Lyon : {n_s} studios vérifiés à la main, {n_c} cours par semaine, "
                    "du 1er au 9e arrondissement et à Villeurbanne. Planning filtrable par style, jour et quartier.")
    text = re.sub(r'<img src="banner_web\.jpg"(?![^>]*fetchpriority)',
                  '<img src="banner_web.jpg" width="1920" height="814" fetchpriority="high"', text, count=1)
    text = replace_block(text, "orgld", jsonld({"@context": "https://schema.org", "@type": "Organization",
                         "@id": BASE + "#organization", "name": "Yoga In Lyon", "url": BASE,
                         "logo": BASE + "logo_web.png", "email": "contact@yoga-in-lyon.fr",
                         "areaServed": {"@type": "City", "name": "Lyon"}}), anchor_before="</head>")
    pills = "".join(f'<a href="{STYLES[t]["slug"]}.html">{esc(t)}</a>' for t in STYLES if t in styles_present)
    block = (f'<section class="quartiers-section"><div class="inner"><h2>Le yoga par style</h2>'
             f'<div class="quartiers-links">{pills}</div></div></section>'
             f'<section class="quartiers-section"><div class="inner"><h2>Trouver un cours selon vos envies</h2>'
             f'<div class="quartiers-links">{collections_pills()}</div></div></section>'
             f'<section class="quartiers-section"><div class="inner"><h2>Nos guides</h2><div class="quartiers-links">'
             + "".join(f'<a href="{g["slug"]}.html">{esc(g["court"])}</a>' for g in GUIDES)
             + '</div></div></section>'
             f'<section class="quartiers-section"><div class="inner"><h2>Les studios de yoga à Lyon</h2>'
             f'<div class="quartiers-links">'
             + "".join(f'<a href="{studio_page(n)}">{esc(n)}</a>' for n in sorted(studios, key=str.lower))
             + '</div></div></section>')
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
    profs = resolve_profs(data, studios, report)
    photos_dir = Path(__file__).resolve().parent / "profs"
    for p in profs:
        if p.get("photo"):
            src = photos_dir / p["photo"]
            if src.exists():
                shutil.copyfile(src, site / f'prof-{p["slug"]}{src.suffix.lower()}')
            else:
                report.append(f"Photo introuvable pour « {p['nom']} » : seo/profs/{p['photo']}")
                p["photo"] = None
        fn = prof_page(p)
        (site / fn).write_text(build_prof(p, studios, chrome_parts), encoding="utf-8")
        generated.append(fn)
    for s in studios.values():
        fn = studio_page(s["name"])
        here = [p for p in profs if s["name"] in p["studios"]]
        (site / fn).write_text(build_studio(s, studios, chrome_parts, here), encoding="utf-8")
        generated.append(fn)
    for ts in STYLES:
        if ts in styles_present:
            fn = STYLES[ts]["slug"] + ".html"
            (site / fn).write_text(build_style(ts, data, studios, chrome_parts), encoding="utf-8")
            generated.append(fn)
    for key in COLLECTIONS:
        fn = COLLECTIONS[key]["slug"] + ".html"
        (site / fn).write_text(build_collection(key, data, studios, chrome_parts), encoding="utf-8")
        generated.append(fn)
    builders = {"chiffres": build_guide_chiffres, "styles": build_guide_styles}
    for g in GUIDES:
        (site / (g["slug"] + ".html")).write_text(builders[g["kind"]](g, data, studios, chrome_parts), encoding="utf-8")
        generated.append(g["slug"] + ".html")
    (site / "guides.html").write_text(build_guides_index(chrome_parts), encoding="utf-8")
    (site / "404.html").write_text(build_404(chrome_parts), encoding="utf-8")
    generated += ["guides.html", "404.html"]
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
            t = patch_home(t, styles_present, data, studios)
        if p.name == "Studios.html":
            t = patch_studios_page(t, data, studios)
        if p.name == "Profs.html":
            t = patch_profs_page(t, profs, studios)
        if p.name == "A-propos.html":
            t = patch_about(t)
        if t != t0:
            p.write_text(t, encoding="utf-8")

    # sitemap / robots / htaccess
    pages = sorted(p.name for p in site.glob("*.html") if p.name not in ("Accueil.html", "404.html")
                   and not p.name.startswith("_"))
    urls = [BASE] + [BASE + n for n in pages if n != "index.html"]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{esc(u)}</loc><lastmod>{DATA_DATE}</lastmod></url>" for u in urls]
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

    print(f"OK : {len(profs)} pages prof, {len(studios)} pages studio, {len(generated) - len(studios) - len(profs) - len(GUIDES) - 2} pages style/thématiques, {len(GUIDES)} guides, "
          f"{len(urls)} URL dans sitemap.xml")
    for r in report:
        print("  ⚠ " + r)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
