# -*- coding: utf-8 -*-
"""
Module partage par tous les scripts build_*.py du site Yoga In Lyon.
Design repris de la maquette generee dans Claude Design (palette lavande/prune,
Fraunces + Inter, cartes arrondies, header sticky, footer prune).
Contient : chargement des donnees studios, helpers de normalisation,
systeme de couleurs par style de yoga, header/footer HTML communs.
"""
import json, html, datetime

STUDIOS_PATH = '/sessions/inspiring-confident-ritchie/mnt/outputs/work/studios_final.json'

with open(STUDIOS_PATH, encoding='utf-8') as f:
    STUDIOS = json.load(f)

JOURS_ORDRE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


def jour_key(j):
    for base in JOURS_ORDRE:
        if j.startswith(base):
            return JOURS_ORDRE.index(base)
    return 99


def creneau_horaire(debut):
    try:
        h = int(debut.split('h')[0])
    except Exception:
        return "Inconnu"
    if 5 <= h < 12:
        return "Matin"
    if 12 <= h < 14:
        return "Midi"
    if 14 <= h < 18:
        return "Après-midi"
    return "Soir"


def type_simplifie(t):
    t_low = t.lower()
    if "iyengar" in t_low: return "Yoga Iyengar"
    if "kundalini" in t_low: return "Yoga Kundalini"
    if "jivamukti" in t_low: return "Yoga Vinyasa"
    if "vinyasa" in t_low: return "Yoga Vinyasa"
    if "flow" in t_low or "rocket" in t_low or "power" in t_low: return "Yoga Vinyasa"
    if "ashtanga" in t_low: return "Ashtanga"
    if "hatha" in t_low: return "Hatha Yoga"
    if "alignement" in t_low: return "Hatha Yoga"
    if "énergie" in t_low or "energie" in t_low: return "Hatha Yoga"
    if "postural" in t_low: return "Hatha Yoga"
    if "nidra" in t_low: return "Pranayama & Nidra"
    if "pranayama" in t_low: return "Pranayama & Nidra"
    if "méditation" in t_low or "meditation" in t_low: return "Pranayama & Nidra"
    if "yin" in t_low: return "Yin Yoga"
    if "relaxation" in t_low or "doux" in t_low: return "Yin Yoga"
    if "soma" in t_low: return "Yin Yoga"
    if "hot yoga" in t_low: return "Hot Yoga"
    if "pilates" in t_low: return "Renfo & Pilates"
    if "core" in t_low or "flexibility" in t_low or "strength" in t_low: return "Renfo & Pilates"
    return "Hatha Yoga"


def favicon_url(site):
    from urllib.parse import urlparse
    try:
        domain = urlparse(site).netloc or site
    except Exception:
        domain = site
    domain = (domain or "").replace("www.", "")
    if not domain:
        return ""
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=64"


# --- Systeme de couleurs par style de yoga (degrade doux façon Claude Design) ---
# Chaque style a un "hue" OKLCH ; bg tres clair, texte fonce, point (dot) plus vif.
TYPE_ORDER = [
    "Hatha Yoga", "Pranayama & Nidra", "Yoga Iyengar", "Renfo & Pilates",
    "Yoga Kundalini", "Yin Yoga", "Hot Yoga", "Ashtanga", "Yoga Vinyasa",
]
# Palette volontairement restreinte aux tons bleu / violet / rose / rouge
# (hue OKLCH de 220° à 380°=20°, on evite le vert/jaune/orange/cyan).
TYPE_HUES = {name: (220 + i * 20) % 360 for i, name in enumerate(TYPE_ORDER)}


def style_colors(type_simple):
    hue = TYPE_HUES.get(type_simple, TYPE_HUES["Hatha Yoga"])
    return {
        "bg": f"oklch(93% 0.045 {hue:.0f})",
        "text": f"oklch(35% 0.09 {hue:.0f})",
        "dot": f"oklch(64% 0.14 {hue:.0f})",
    }


# --- Coordonnees GPS approximatives des studios (pour les cartes Leaflet) ---
COORDS = {
    "École de Yoga Horizon": (45.7706, 4.8291),
    "Multifa": (45.7690, 4.8275),
    "Karan Anand Nathalie": (45.7460, 4.8320),
    "Latitude Yoga": (45.7525, 4.8265),
    "Yoga Bellecour": (45.7600, 4.8330),
    "Samtosha Yoga - Patricia Heude": (45.7615, 4.8325),
    "École de Yoga de Mysore (Ashtanga)": (45.7528, 4.8268),
    "Studio Arbol Flow": (45.7592, 4.8415),
    "Centre Tao Yoga": (45.7738, 4.8283),
    "Centre de Yoga Iyengar Croix-Rousse": (45.7728, 4.8296),
    "L'Atelier du Yoga": (45.7718, 4.8302),
    "Yoga Room - Les Halles": (45.7618, 4.8478),
    "Yeahga (Espace holistique)": (45.7738, 4.8270),
    "Yoga Korner": (45.7680, 4.8330),
    "Yoga by Valérie Maurel (Saône & Soi)": (45.7645, 4.8195),
    "Cocon Yoga - Le Cocon": (45.7448, 4.8398),
    "Cocon Yoga - Oblique": (45.7469, 4.8362),
    "GOTAMYOGA": (45.7458, 4.8580),
    "Pranam Yoga": (45.7699, 4.8047),
    "Vima Yoga": (45.7665, 4.8807),
    "The Good Flow": (45.7645, 4.8530),
    "O Yoga Studio": (45.7690, 4.8480),
    "Les Ailes Hatha Yoga": (45.7715, 4.8555),
    "Yoga Dojo Lyon Massena": (45.7708, 4.8540),
    "Sesam Yoga Lyon 6": (45.7695, 4.8500),
    "Sesam Yoga Lyon 7": (45.7455, 4.8375),
}

# Degrades illustratifs (pas de vraies photos, pour rester safe niveau droits d'image)
GRADIENTS = [
    "linear-gradient(135deg, #e8c9c2, #c9a6d6)",
    "linear-gradient(135deg, #b7cfc2, #8fb8a8)",
    "linear-gradient(135deg, #f0d9a8, #cdbdf5)",
    "linear-gradient(135deg, #c2d6e8, #a6b8d6)",
    "linear-gradient(135deg, #e8c2d6, #d6a6c9)",
    "linear-gradient(135deg, #d6e8c2, #b8d6a6)",
    "linear-gradient(135deg, #dcc2e8, #b8a6d6)",
    "linear-gradient(135deg, #e8d2c2, #d6b8a6)",
]
EMOJIS = ["🧘‍♀️", "🪢", "🌿", "🧘", "🕉️", "🌸", "🌙", "☀️", "🍃", "✨"]


def visual_for(index):
    return GRADIENTS[index % len(GRADIENTS)], EMOJIS[index % len(EMOJIS)]


FONTS_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700'
    '&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">'
)

BASE_CSS = """
  :root {
    --bg: #FFFBFC;
    --card: #ffffff;
    --ink: #241A2E;
    --muted: #7A6690;
    --muted-soft: #9885a8;
    --lavender: #D9C6EC;
    --lavender-soft: #F1E9F9;
    --lavender-dark: #412957;
    --lavender-accent: #6a4a8c;
    --border: #EAE1F2;
    --pill-radius: 999px;
    --brand-purple: #412957;
    --footer-bg: #2c1c3d;
  }
  * { box-sizing: border-box; }
  body { margin: 0; font-family: 'Inter', Helvetica, Arial, sans-serif; background: var(--bg); color: var(--ink); }
  h1, h2, h3, .day-title, .brand-word { font-family: 'Fraunces', Georgia, serif; }
  a { color: var(--lavender-dark); text-decoration: none; }
  a:hover { color: var(--lavender-accent); }
  input[type="checkbox"] { accent-color: var(--lavender-dark); width: 16px; height: 16px; cursor: pointer; }

  .site-header {
    position: sticky; top: 0; z-index: 30;
    display: flex; align-items: center; justify-content: space-between;
    padding: 18px 48px;
    backdrop-filter: blur(6px);
    border-bottom: 1px solid var(--border);
    background: rgba(255,251,252,0.92);
  }
  .site-header .brand { font-size: 22px; font-weight: 600; color: var(--brand-purple); font-family: 'Fraunces', serif; }
  .site-header nav { display: flex; align-items: center; gap: 26px; flex-wrap: wrap; }
  .site-header nav a { font-size: 15px; font-weight: 500; color: var(--brand-purple); opacity: 0.75; }
  .site-header nav a:hover { opacity: 1; }
  .site-header nav a.active { opacity: 1; border-bottom: 2px solid var(--brand-purple); padding-bottom: 3px; }
  .site-header nav a.pill-cta {
    font-weight: 600; padding: 10px 22px; border-radius: var(--pill-radius);
    background: var(--brand-purple); color: #FBF8F4; opacity: 1;
  }
  .site-header nav a.pill-cta:hover { background: var(--lavender-accent); }
  @media (max-width: 820px) {
    .site-header { padding: 14px 18px; }
    .site-header nav { gap: 12px; }
    .site-header nav a:not(.pill-cta) { display: none; }
  }

  .search-bar-wrap { max-width: 1280px; margin: 0 auto; padding: 0 24px; position: relative; z-index: 5; }
  .search-bar {
    background: var(--card); border-radius: 18px; box-shadow: 0 12px 32px rgba(65,41,87,0.14);
    display: flex; flex-wrap: wrap; align-items: end; gap: 18px; padding: 22px 26px;
  }
  .search-seg { flex: 1 1 160px; display: flex; flex-direction: column; gap: 6px; min-width: 140px; }
  .search-seg label { font-size: 12px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }
  .search-seg select {
    border: none; border-bottom: 2px solid var(--border); padding: 8px 0 8px 0;
    font-size: 15px; background: transparent; font-family: 'Inter', sans-serif; color: var(--ink);
    cursor: pointer; outline: none; width: 100%;
  }
  .search-seg select:focus { border-bottom-color: var(--lavender-dark); }
  .search-btn {
    flex: 0 0 auto; padding: 13px 26px; border-radius: var(--pill-radius); border: none;
    background: var(--brand-purple); color: #FBF8F4; font-size: 14.5px; font-weight: 600;
    cursor: pointer; font-family: 'Inter', sans-serif; white-space: nowrap;
  }
  .search-btn:hover { background: var(--lavender-accent); }
  @media (max-width: 700px) {
    .search-bar { border-radius: 20px; padding: 16px; }
    .search-btn { width: 100%; }
  }

  footer.site-footer { background: var(--footer-bg); color: #e9e1f1; padding: 64px 48px 28px; margin-top: 0; }
  footer.site-footer .inner { max-width: 1180px; margin: 0 auto; }
  footer.site-footer .top-row {
    display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-end; gap: 24px;
    padding-bottom: 44px; border-bottom: 1px solid rgba(255,255,255,0.12);
  }
  footer.site-footer .contact-block { display: flex; flex-direction: column; gap: 12px; font-size: 14px; color: #cbb8dd; }
  footer.site-footer .wordmark { font-family: 'Fraunces', serif; font-size: 52px; font-weight: 600; color: #FBF8F4; line-height: 1; }
  footer.site-footer .mid-row {
    display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start; gap: 32px; padding: 36px 0;
  }
  footer.site-footer .tagline { font-size: 14px; color: #B79FCB; max-width: 280px; line-height: 1.5; }
  footer.site-footer .nav-col { display: flex; flex-direction: column; gap: 10px; }
  footer.site-footer .nav-col .head { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #FBF8F4; }
  footer.site-footer .nav-col a { color: #cbb8dd; font-size: 14px; }
  footer.site-footer .nav-col a:hover { color: #fff; }
  footer.site-footer .cta-btn {
    padding: 13px 28px; border-radius: var(--pill-radius); background: #FBF8F4; color: var(--brand-purple);
    font-size: 14px; font-weight: 600; align-self: flex-start;
  }
  footer.site-footer .bottom { text-align: center; font-size: 12.5px; color: #8a76a0; padding-top: 20px; }
  @media (max-width: 700px) {
    footer.site-footer { padding: 44px 20px 24px; }
    footer.site-footer .wordmark { font-size: 34px; }
  }
"""


def header_html(active):
    """active: 'accueil' | 'studios' | 'profs' | 'apropos' | 'planning'"""
    def cls(key):
        return " active" if key == active else ""
    return f"""<header class="site-header">
  <a href="Accueil.html" class="brand">Yoga in Lyon</a>
  <nav>
    <a href="Accueil.html" class="{cls('accueil').strip()}">Accueil</a>
    <a href="Studios.html" class="{cls('studios').strip()}">Studios</a>
    <a href="Profs.html" class="{cls('profs').strip()}">Profs</a>
    <a href="A-propos.html" class="{cls('apropos').strip()}">Qui sommes-nous</a>
    <a href="Yoga_a_Lyon_Planning.html" class="pill-cta{cls('planning')}">Voir le planning</a>
  </nav>
</header>"""


def footer_html():
    year = datetime.datetime.now().year
    return f"""<footer class="site-footer">
  <div class="inner">
    <div class="top-row">
      <div class="contact-block">
        <div>contact@yoga-in-lyon.fr</div>
        <div>Lyon, France</div>
      </div>
      <div class="wordmark">Yoga in Lyon</div>
    </div>
    <div class="mid-row">
      <div class="tagline">L'annuaire de référence des studios et cours de yoga à Lyon.</div>
      <div class="nav-col">
        <div class="head">Navigation</div>
        <a href="Accueil.html">Accueil</a>
        <a href="Studios.html">Studios</a>
        <a href="Profs.html">Profs</a>
        <a href="A-propos.html">Qui sommes-nous</a>
        <a href="Yoga_a_Lyon_Planning.html">Planning</a>
      </div>
      <div class="nav-col">
        <div class="head">Réseaux</div>
        <a href="#">Instagram</a>
        <a href="#">Facebook</a>
      </div>
      <a href="Yoga_a_Lyon_Planning.html" class="cta-btn">Trouver un cours</a>
    </div>
    <div class="bottom">L'annuaire du yoga à Lyon · {year}</div>
  </div>
</footer>"""


def all_creneaux():
    """Retourne la liste a plat de tous les creneaux, enrichis (type_simple, creneau, favicon)."""
    out = []
    for s in STUDIOS:
        for c in s["cours"]:
            out.append({
                "studio": s["nom"],
                "arr": s["arr"],
                "quartier": s["quartier"],
                "site": s["site"],
                "adresse": s["adresse"],
                "jour": c["jour"],
                "debut": c["debut"],
                "fin": c.get("fin", ""),
                "type": c["type"],
                "type_simple": type_simplifie(c["type"]),
                "creneau": creneau_horaire(c["debut"]),
                "favicon": favicon_url(s["site"]),
            })
    out.sort(key=lambda c: (jour_key(c["jour"]), c["debut"]))
    return out


def search_select(label, options, select_id, placeholder, onchange="onSearchBar()"):
    opts = "".join(f'<option value="{html.escape(o)}">{html.escape(o)}</option>' for o in options)
    onchange_attr = f' onchange="{onchange}"' if onchange else ""
    return f"""
    <div class="search-seg">
      <label for="{select_id}">{label}</label>
      <select id="{select_id}"{onchange_attr}>
        <option value="">{placeholder}</option>
        {opts}
      </select>
    </div>"""
