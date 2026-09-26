# -*- coding: utf-8 -*-
import json
import site_common as sc

studios = sc.STUDIOS
creneaux = sc.all_creneaux()

quartiers = sorted(set(c["quartier"] for c in creneaux))
arrondissements = sorted(set(c["arr"] for c in creneaux))
jours = sorted(set(c["jour"] for c in creneaux), key=sc.jour_key)
types = sorted(set(c["type_simple"] for c in creneaux))
CRENEAUX_ORDRE = ["Matin", "Midi", "Après-midi", "Soir"]
creneaux_horaires = [c for c in CRENEAUX_ORDRE if c in set(x["creneau"] for x in creneaux)]

total_studios = len(studios)
total_creneaux = len(creneaux)
total_zones = len(set(c["arr"] for c in creneaux))
total_styles = len(types)

# --- Donnee allegee pour le compteur "X cours correspondent" en direct sur la home ---
search_data = [{"type_simple": c["type_simple"], "jour": c["jour"], "creneau": c["creneau"], "arr": c["arr"]} for c in creneaux]
search_data_json = json.dumps(search_data, ensure_ascii=False)

style_chip_hues = {t: sc.TYPE_HUES.get(t, sc.TYPE_HUES["Hatha Yoga"]) for t in types}


def style_chips_html():
    chips = ['<button type="button" class="style-chip active" style="--chip-hue:260;" onclick="selectChip(this, \'\')">Tous</button>']
    for t in types:
        hue = style_chip_hues[t]
        chips.append(f'<button type="button" class="style-chip" style="--chip-hue:{hue:.0f};" onclick="selectChip(this, \'{t}\')">{t}</button>')
    return "".join(chips)


def day_options():
    return "".join(f'<option value="{d}">{d}</option>' for d in jours)


def creneau_options():
    return "".join(f'<option value="{c}">{c}</option>' for c in creneaux_horaires)


def arr_options():
    return "".join(f'<option value="{a}">{a}</option>' for a in arrondissements)


# --- Markers carte ---
markers = []
for s in studios:
    coord = sc.COORDS.get(s["nom"])
    if not coord:
        continue
    markers.append({
        "nom": s["nom"], "lat": coord[0], "lng": coord[1],
        "arr": s["arr"], "quartier": s["quartier"], "site": s["site"],
        "nb_cours": len(s["cours"]),
    })
markers_json = json.dumps(markers, ensure_ascii=False)

# --- 3 studios coup de coeur ---
featured_names = ["Yoga Bellecour", "Centre de Yoga Iyengar Croix-Rousse", "Yeahga (Espace holistique)"]
featured = [s for s in studios if s["nom"] in featured_names]
featured_blurbs = {
    "Yoga Bellecour": "Un studio historique en plein cœur de la Presqu'île : Hatha yoga traditionnel, le même professeur toute la saison, des groupes à taille humaine (8 à 14 élèves).",
    "Centre de Yoga Iyengar Croix-Rousse": "Une méthode précise et progressive, avec accessoires (briques, sangles, chaises) pour adapter chaque posture. Cours pour tous niveaux, du débutant aux séniors.",
    "Yeahga (Espace holistique)": "Ouvert fin 2024 à la Croix-Rousse : Vinyasa, Hatha, Yin, yoga doux et ateliers bien-être dans un lieu intimiste (10 personnes max par cours).",
}


def featured_card(s, idx):
    blurb = featured_blurbs.get(s["nom"], "")
    gradient, emoji = sc.visual_for(idx)
    return f"""
      <div class="feature-card">
        <div class="feature-photo" style="background:{gradient};"><span>{emoji}</span></div>
        <div class="feature-body">
          <div class="feature-name">{s['nom']}</div>
          <div class="feature-quartier">{s['quartier']} · {s['arr']}</div>
          <p class="feature-blurb">{blurb}</p>
          <a href="{s['site']}" target="_blank" rel="noopener">Voir le site du studio →</a>
        </div>
      </div>"""


featured_html = "".join(featured_card(s, i) for i, s in enumerate(featured))

WHY_ICONS = [
    '<svg width="40" height="40" viewBox="0 0 44 44"><g transform="translate(22,26)"><ellipse cx="0" cy="-10" rx="5.5" ry="10" fill="none" stroke="#412957" stroke-width="1.8" transform="rotate(-28)"></ellipse><ellipse cx="0" cy="-10" rx="5.5" ry="10" fill="#D9C6EC" opacity="0.6"></ellipse><ellipse cx="0" cy="-10" rx="5.5" ry="10" fill="none" stroke="#412957" stroke-width="1.8" transform="rotate(28)"></ellipse></g></svg>',
    '<svg width="40" height="40" viewBox="0 0 44 44"><circle cx="22" cy="22" r="9" fill="none" stroke="#412957" stroke-width="2"></circle><line x1="22" y1="4" x2="22" y2="10" stroke="#412957" stroke-width="2"></line><line x1="22" y1="34" x2="22" y2="40" stroke="#D9C6EC" stroke-width="2"></line><line x1="4" y1="22" x2="10" y2="22" stroke="#D9C6EC" stroke-width="2"></line><line x1="34" y1="22" x2="40" y2="22" stroke="#412957" stroke-width="2"></line></svg>',
    '<svg width="40" height="40" viewBox="0 0 44 44"><circle cx="22" cy="12" r="6" fill="none" stroke="#412957" stroke-width="2"></circle><circle cx="13" cy="29" r="6" fill="#D9C6EC" opacity="0.7"></circle><circle cx="31" cy="29" r="6" fill="none" stroke="#412957" stroke-width="2"></circle></svg>',
    '<svg width="40" height="40" viewBox="0 0 44 44"><circle cx="18" cy="18" r="11" fill="none" stroke="#412957" stroke-width="2"></circle><ellipse cx="30" cy="30" rx="6" ry="4" fill="#D9C6EC" transform="rotate(-30 30 30)"></ellipse></svg>',
]
WHY_CARDS = [
    ("Studios vérifiés à la main", "Chaque studio référencé est visité et vérifié, pas de fiche fantôme ni de cours annulé."),
    (f"{total_creneaux} créneaux par semaine", "Matin, midi ou soir : le planning couvre toute la semaine, tous les quartiers."),
    ("Tous les styles de yoga", "Vinyasa, Hatha, Yin, Iyengar et plus : chaque style a sa couleur pour s'y retrouver."),
    ("Ancré dans les quartiers", "De la Croix-Rousse à Confluence en passant par Villeurbanne : trouvez le studio le plus proche de chez vous."),
]


def why_cards_html():
    out = ""
    for icon, (title, desc) in zip(WHY_ICONS, WHY_CARDS):
        out += f"""
      <div class="why-card">
        <div class="why-icon">{icon}</div>
        <h3>{title}</h3>
        <p>{desc}</p>
      </div>"""
    return out


PAGE_CSS = """
  @keyframes fadeInUp { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: translateY(0); } }

  .hero { position: relative; width: 100%; height: 62vh; min-height: 420px; overflow: hidden; }
  .hero img { width: 100%; height: 100%; object-fit: cover; object-position: 50% 35%; display: block; }
  .hero .hero-scrim {
    position: absolute; inset: 0; background: linear-gradient(0deg, rgba(36,20,46,0.55) 0%, rgba(36,20,46,0.05) 45%, transparent 70%);
  }
  .hero .hero-text { position: absolute; left: 48px; bottom: 40px; max-width: 640px; color: #FBF8F4; z-index: 2; }
  .hero .hero-text h1 {
    font-size: 44px; font-weight: 600; margin: 0 0 8px; line-height: 1.08;
    text-shadow: 0 2px 18px rgba(0,0,0,0.35);
  }
  .hero .hero-text p { font-size: 16px; margin: 0; color: #EFE6F6; text-shadow: 0 1px 10px rgba(0,0,0,0.3); }
  @media (max-width: 700px) {
    .hero .hero-text { left: 20px; right: 20px; bottom: 24px; }
    .hero .hero-text h1 { font-size: 28px; }
  }

  .search-card-wrap { max-width: 1180px; margin: -64px auto 0; padding: 0 24px; position: relative; z-index: 10; }
  .search-card {
    background: #fff; border-radius: 24px; box-shadow: 0 28px 64px rgba(65,41,87,0.22);
    padding: 36px 40px; display: flex; flex-direction: column; gap: 22px;
    border-top: 4px solid var(--brand-purple); animation: fadeInUp 0.7s ease-out both;
  }
  .search-card .eyebrow { font-size: 12px; font-weight: 700; color: #9B7FB0; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; }
  .search-card h2 { font-size: 26px; font-weight: 500; margin: 0; }
  .search-row { display: flex; flex-wrap: wrap; align-items: end; gap: 20px; }
  .style-chips-field { flex: 1 1 100%; display: flex; flex-direction: column; gap: 8px; }
  .style-chips-field label, .search-row .field label { font-size: 12px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }
  .style-chips { display: flex; flex-wrap: wrap; gap: 8px; max-height: 90px; overflow-y: auto; }
  .style-chip { padding: 8px 16px; border-radius: 999px; font-size: 13.5px; font-weight: 600; cursor: pointer; border: 2px solid transparent;
    background: oklch(95% 0.03 var(--chip-hue,260)); color: oklch(35% 0.09 var(--chip-hue,260)); font-family: 'Inter', sans-serif; }
  .style-chip.active { background: oklch(64% 0.14 var(--chip-hue,260)); color: #fff; border-color: oklch(64% 0.14 var(--chip-hue,260)); }
  .search-row .field { flex: 1 1 150px; display: flex; flex-direction: column; gap: 6px; }
  .search-row .field select {
    border: none; border-bottom: 2px solid var(--border); padding: 8px 0; font-size: 16px; color: var(--ink);
    background: transparent; font-family: 'Inter', sans-serif; cursor: pointer; outline: none;
  }
  .search-footer { flex: 1 1 100%; display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
  .search-footer .match-count { font-size: 14px; color: #6a5a78; }
  .search-footer .match-count strong { color: var(--brand-purple); }
  .search-footer .go-btn {
    flex: 0 0 auto; padding: 16px 36px; border-radius: 999px; border: none; background: var(--brand-purple); color: #FBF8F4;
    font-size: 16px; font-weight: 700; font-family: 'Inter', sans-serif; cursor: pointer;
    box-shadow: 0 10px 24px rgba(65,41,87,0.3); transition: transform 0.15s, box-shadow 0.15s;
  }
  .search-footer .go-btn:hover { transform: scale(1.03); box-shadow: 0 14px 30px rgba(65,41,87,0.4); }

  .stats-band { background: var(--footer-bg); padding: 126px 24px 56px; }
  .stats-inner { max-width: 1180px; margin: 0 auto; display: flex; flex-wrap: wrap; justify-content: space-around; gap: 36px; }
  .stat-item { display: flex; flex-direction: column; align-items: center; gap: 14px; }
  .stat-circle { width: 84px; height: 84px; border-radius: 50%; border: 3px solid #D9C6EC; display: flex; align-items: center; justify-content: center; }
  .stat-circle .val { font-size: 22px; font-weight: 600; color: #FBF8F4; }
  .stat-label { font-size: 12.5px; color: #cbb8dd; text-transform: uppercase; letter-spacing: 0.05em; text-align: center; }

  section.hp { max-width: 1180px; margin: 0 auto; padding: 90px 24px 60px; }
  section.hp h2 { font-size: 34px; font-weight: 500; margin: 0 0 12px; text-align: center; }
  section.hp .sub { text-align: center; color: #6a5a78; font-size: 16px; max-width: 520px; margin: 0 auto 48px; }

  .why-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 32px; }
  .why-card { display: flex; flex-direction: column; gap: 14px; padding: 18px; border-radius: 16px; transition: transform 0.2s, box-shadow 0.2s; }
  .why-card:hover { transform: translateY(-4px); box-shadow: 0 16px 30px rgba(65,41,87,0.1); }
  .why-card h3 { font-size: 19px; font-weight: 500; margin: 0; }
  .why-card p { font-size: 14.5px; color: #6a5a78; line-height: 1.55; margin: 0; }

  section.featured-section { background: linear-gradient(180deg, #E9D9FA, #FFFBFC); padding: 70px 24px; }
  section.featured-section .inner { max-width: 1180px; margin: 0 auto; }
  section.featured-section h2 { font-size: 34px; font-weight: 500; margin: 0 0 50px; text-align: left; }
  .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 28px; }
  .feature-card { background: #fff; border-radius: 18px; overflow: hidden; display: flex; flex-direction: column; transition: transform 0.2s, box-shadow 0.2s; }
  .feature-card:hover { transform: translateY(-6px); box-shadow: 0 20px 40px rgba(65,41,87,0.16); }
  .feature-photo { height: 190px; display: flex; align-items: center; justify-content: center; }
  .feature-photo span { font-size: 3em; }
  .feature-body { padding: 22px 24px; display: flex; flex-direction: column; gap: 8px; flex: 1; }
  .feature-name { font-family: 'Fraunces', serif; font-size: 19px; font-weight: 500; }
  .feature-quartier { font-size: 13px; color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
  .feature-blurb { font-size: 14.5px; color: #5a4a68; line-height: 1.55; margin: 4px 0 12px; flex: 1; }

  #map { width: 100%; height: 420px; border-radius: 18px; overflow: hidden; background: var(--border); }
  .map-note { text-align: center; font-size: 0.8em; color: var(--muted); margin-top: 12px; }

  .reviews-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
  .review-card { background: var(--card); border-radius: 18px; padding: 24px; box-shadow: 0 2px 10px rgba(138,111,214,0.08); }
  .review-stars { color: #f2b84b; font-size: 1em; margin-bottom: 8px; }
  .review-text { font-size: 0.95em; line-height: 1.6; font-style: italic; margin: 0 0 12px; }
  .review-author { font-size: 0.85em; font-weight: 700; }
  .review-source { font-size: 0.78em; color: var(--muted); margin-top: 2px; }

  .quartiers-section { padding: 60px 24px 10px; text-align: center; }
  .quartiers-section .inner { max-width: 900px; margin: 0 auto; }
  .quartiers-section h2 { font-size: 26px; font-weight: 500; margin: 0 0 22px; }
  .quartiers-links { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; }
  .quartiers-links a {
    padding: 9px 18px; border-radius: 999px; background: var(--lavender-soft); color: var(--brand-purple);
    font-size: 14px; font-weight: 600;
  }
  .quartiers-links a:hover { background: var(--lavender); }

  .cta-band { padding: 90px 24px; text-align: center; background-color: var(--brand-purple); color: #FFFFFC; }
  .cta-band .inner { max-width: 720px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; gap: 22px; }
  .cta-band h2 { font-size: 36px; font-weight: 500; margin: 0; color: #FFDFFF; }
  .cta-band a { padding: 15px 34px; border-radius: 999px; color: #361E42; font-size: 16px; font-weight: 600; background-color: #FCC1FF; }
  .cta-band a:hover { background-color: #ffd1ff; color: #361E42; }

  .newsletter-section { position: relative; padding: 64px 24px; background-image: url('banner_web.jpg'); background-size: cover; background-position: center; overflow: hidden; }
  .newsletter-section .dim { position: absolute; inset: 0; background: rgba(241,233,249,0.88); }
  .newsletter-section .inner { position: relative; z-index: 1; max-width: 620px; margin: 0 auto; text-align: center; display: flex; flex-direction: column; align-items: center; gap: 16px; }
  .newsletter-section h2 { font-size: 28px; font-weight: 500; color: var(--brand-purple); margin: 0; }
  .newsletter-section p { font-size: 15px; color: #6a5a78; margin: 0; }
  .newsletter-form { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; width: 100%; max-width: 420px; }
  .newsletter-form input { flex: 1 1 220px; padding: 13px 18px; border-radius: 999px; border: 1px solid var(--lavender); font-size: 14.5px; background: #fff; }
  .newsletter-form button { flex: 0 0 auto; padding: 13px 26px; border-radius: 999px; border: none; background: var(--brand-purple); color: #FBF8F4; font-weight: 600; font-size: 14.5px; cursor: pointer; }
  .newsletter-form button:hover { transform: scale(1.05); }
  .form-thanks { font-size: 15px; color: var(--brand-purple); font-weight: 600; display: none; }
"""

html_out = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Yoga In Lyon — L'annuaire des cours de yoga à Lyon</title>
{sc.seo_head(
    "Yoga In Lyon — L'annuaire des cours de yoga à Lyon",
    f"Trouvez votre studio et votre cours de yoga à Lyon : {total_studios} studios vérifiés, {total_creneaux} créneaux par semaine, du 1er au 9e arrondissement et à Villeurbanne.",
    "",
)}
{sc.FONTS_LINK}
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
<script type="application/ld+json">{sc.website_jsonld()}</script>
<style>
{sc.BASE_CSS}
{PAGE_CSS}
</style>
</head>
<body>

{sc.header_html('accueil')}

<section class="hero">
  <img src="banner_web.jpg" alt="Séance de yoga au bord de la Saône à Lyon">
  <div class="hero-scrim"></div>
  <div class="hero-text">
    <h1>Yoga à Lyon : trouvez votre studio et votre cours</h1>
    <p>{total_studios} studios vérifiés à la main · {total_creneaux} créneaux par semaine · du 1er au 9e arrondissement et à Villeurbanne</p>
  </div>
</section>

<div class="search-card-wrap">
  <div class="search-card">
    <div>
      <div class="eyebrow">Recherche rapide</div>
      <h2>Trouvez votre cours de yoga à Lyon</h2>
    </div>
    <div class="search-row">
      <div class="style-chips-field">
        <label>Style de yoga</label>
        <div class="style-chips" id="style-chips">{style_chips_html()}</div>
      </div>
      <div class="field">
        <label for="hp-jour">Jour</label>
        <select id="hp-jour" onchange="updateMatchCount()">
          <option value="">Tous les jours</option>
          {day_options()}
        </select>
      </div>
      <div class="field">
        <label for="hp-creneau">Heure</label>
        <select id="hp-creneau" onchange="updateMatchCount()">
          <option value="">Toute la journée</option>
          {creneau_options()}
        </select>
      </div>
      <div class="field">
        <label for="hp-arr">Arrondissement</label>
        <select id="hp-arr" onchange="updateMatchCount()">
          <option value="">Tous les arrondissements</option>
          {arr_options()}
        </select>
      </div>
      <div class="search-footer">
        <div class="match-count"><strong id="match-count">{total_creneaux}</strong> cours correspondent à cette recherche</div>
        <button type="button" class="go-btn" onclick="goSearch()">Trouver un cours →</button>
      </div>
    </div>
  </div>
</div>

<section class="stats-band">
  <div class="stats-inner">
    <div class="stat-item"><div class="stat-circle" style="border-color:#D9C6EC;"><div class="val">{total_studios}</div></div><div class="stat-label">Studios référencés</div></div>
    <div class="stat-item"><div class="stat-circle" style="border-color:#B79FCB;"><div class="val">{total_creneaux}</div></div><div class="stat-label">Créneaux / semaine</div></div>
    <div class="stat-item"><div class="stat-circle" style="border-color:#9B7FB0;"><div class="val">{total_zones}</div></div><div class="stat-label">Zones couvertes</div></div>
    <div class="stat-item"><div class="stat-circle" style="border-color:#D9C6EC;"><div class="val">{total_styles}</div></div><div class="stat-label">Styles de yoga</div></div>
  </div>
</section>

<section class="hp">
  <h2>Pourquoi Yoga in Lyon</h2>
  <p class="sub">Un annuaire pensé pour trouver un cours près de chez vous, au bon moment.</p>
  <div class="why-grid">
    {why_cards_html()}
  </div>
</section>

<section class="featured-section">
  <div class="inner">
    <h2>Nos studios coup de cœur du mois</h2>
    <div class="feature-grid">
      {featured_html}
    </div>
  </div>
</section>

<section class="hp">
  <h2>Les studios sur la carte</h2>
  <p class="sub">Localisez les studios référencés dans les arrondissements de Lyon et à Villeurbanne.</p>
  <div id="map"></div>
  <p class="map-note">Carte © OpenStreetMap — emplacements approximatifs, {len(markers)} studios positionnés sur {total_studios} vérifiés.</p>
</section>

<section class="hp">
  <h2>Avis vérifiés</h2>
  <p class="sub">Extraits d'avis Google publiés sur les sites des studios eux-mêmes.</p>
  <div class="reviews-grid">
    <div class="review-card">
      <div class="review-stars">★★★★★</div>
      <p class="review-text">« Thierry est un véritable passionné qui transmet avec bienveillance son enseignement en s'adaptant à chacun. »</p>
      <div class="review-author">Marie B.</div>
      <div class="review-source">Avis Google — Yoga Bellecour</div>
    </div>
    <div class="review-card">
      <div class="review-stars">★★★★★</div>
      <p class="review-text">« Plus de 15 années de pratique dans cette école et toujours une belle qualité d'enseignement. Salle très bien équipée. »</p>
      <div class="review-author">Stéphanie C.</div>
      <div class="review-source">Avis Google — Centre de Yoga Iyengar Croix-Rousse</div>
    </div>
    <div class="review-card">
      <div class="review-stars">★★★★★</div>
      <p class="review-text">« Un yoga de qualité, une salle bien équipée, des groupes de niveaux, et des enseignants attentifs et bienveillants. »</p>
      <div class="review-author">Patricia L.</div>
      <div class="review-source">Avis Google — Centre de Yoga Iyengar Croix-Rousse</div>
    </div>
  </div>
</section>

<section class="quartiers-section">
  <div class="inner">
    <h2>Le yoga par quartier</h2>
    <div class="quartiers-links">
      {"".join(f'<a href="{sc.arr_page_filename(a)}">Yoga {a}</a>' for a in sc.all_arrondissements())}
    </div>
  </div>
</section>

<section class="cta-band">
  <div class="inner">
    <h2>L'annuaire de référence du yoga à Lyon</h2>
    <a href="Yoga_a_Lyon_Planning.html">Voir tous les cours à Lyon</a>
  </div>
</section>

<section class="newsletter-section">
  <div class="dim"></div>
  <div class="inner">
    <h2>Restez informé·e</h2>
    <p>Nouveaux studios et cours ajoutés chaque semaine à Lyon.</p>
    <div class="form-thanks" id="newsletter-thanks">Merci, vous êtes inscrit·e !</div>
    <form class="newsletter-form" id="newsletter-form" onsubmit="return submitNewsletter(event)">
      <input type="email" required placeholder="Votre email" id="newsletter-email">
      <button type="submit">S'inscrire</button>
    </form>
  </div>
</section>

{sc.footer_html()}

<script>
const SEARCH_DATA = {search_data_json};

function selectChip(el, styleVal) {{
  document.querySelectorAll('.style-chip').forEach(c => c.classList.remove('active'));
  el.classList.add('active');
  el.dataset.selected = "1";
  updateMatchCount();
}}

function getSelectedStyle() {{
  const active = document.querySelector('.style-chip.active');
  return active ? (active.textContent === 'Tous' ? '' : active.textContent) : '';
}}

function updateMatchCount() {{
  const styleVal = getSelectedStyle();
  const jourVal = document.getElementById('hp-jour').value;
  const creneauVal = document.getElementById('hp-creneau').value;
  const arrVal = document.getElementById('hp-arr').value;
  const count = SEARCH_DATA.filter(c =>
    (!styleVal || c.type_simple === styleVal) &&
    (!jourVal || c.jour === jourVal) &&
    (!creneauVal || c.creneau === creneauVal) &&
    (!arrVal || c.arr === arrVal)
  ).length;
  document.getElementById('match-count').textContent = count;
}}

function goSearch() {{
  const type = getSelectedStyle();
  const jour = document.getElementById('hp-jour').value;
  const creneau = document.getElementById('hp-creneau').value;
  const arr = document.getElementById('hp-arr').value;
  const params = new URLSearchParams();
  if (type) params.set('type', type);
  if (jour) params.set('jour', jour);
  if (creneau) params.set('creneau', creneau);
  if (arr) params.set('arr', arr);
  const qs = params.toString();
  window.location.href = 'Yoga_a_Lyon_Planning.html' + (qs ? '?' + qs : '');
}}

function submitNewsletter(e) {{
  e.preventDefault();
  const email = document.getElementById('newsletter-email').value;
  window.location.href = 'mailto:contact@yoga-in-lyon.fr?subject=' + encodeURIComponent('Inscription newsletter') + '&body=' + encodeURIComponent('Merci de m\\'inscrire à la newsletter : ' + email);
  document.getElementById('newsletter-thanks').style.display = 'block';
  document.getElementById('newsletter-form').style.display = 'none';
  return false;
}}
</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script>
const MARKERS = {markers_json};

const map = L.map('map', {{ scrollWheelZoom: false }}).setView([45.764, 4.835], 12);
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  maxZoom: 19,
  subdomains: 'abcd',
  attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
}}).addTo(map);

const purpleIcon = L.divIcon({{
  className: 'custom-marker',
  html: '<div style="background:#2c1c3d;width:16px;height:16px;border-radius:50%;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,0.4);"></div>',
  iconSize: [16,16],
  iconAnchor: [8,8]
}});

MARKERS.forEach(m => {{
  const marker = L.marker([m.lat, m.lng], {{icon: purpleIcon}}).addTo(map);
  marker.bindPopup(`<strong>${{m.nom}}</strong><br>${{m.quartier}} · ${{m.arr}}<br>${{m.nb_cours}} créneaux vérifiés<br><a href="${{m.site}}" target="_blank" rel="noopener">Voir le site →</a>`);
}});
</script>

</body>
</html>
"""

with open('/sessions/inspiring-confident-ritchie/mnt/outputs/work/accueil.html', 'w', encoding='utf-8') as f:
    f.write(html_out)

print("Homepage generee:", len(html_out), "caracteres,", len(markers), "marqueurs sur la carte")
