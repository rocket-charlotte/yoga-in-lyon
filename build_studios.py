# -*- coding: utf-8 -*-
import json
import site_common as sc

studios = sc.STUDIOS

FEATURED_BLURBS = {
    "Yoga Bellecour": "Un studio historique en plein cœur de la Presqu'île : Hatha yoga traditionnel, le même professeur toute la saison, des groupes à taille humaine.",
    "Centre de Yoga Iyengar Croix-Rousse": "Une méthode précise et progressive, avec accessoires (briques, sangles, chaises) pour adapter chaque posture. Cours pour tous niveaux.",
    "Yeahga (Espace holistique)": "Ouvert fin 2024 à la Croix-Rousse : Vinyasa, Hatha, Yin, yoga doux et ateliers bien-être dans un lieu intimiste.",
}

arrondissements = sorted(set(s["arr"] for s in studios))

markers = []
for s in studios:
    coord = sc.COORDS.get(s["nom"])
    if not coord:
        continue
    markers.append({
        "nom": s["nom"], "lat": coord[0], "lng": coord[1],
        "arr": s["arr"], "quartier": s["quartier"], "site": s["site"],
    })
markers_json = json.dumps(markers, ensure_ascii=False)


def studio_card(s, idx):
    style_set = sorted(set(sc.type_simplifie(c["type"]) for c in s["cours"]))
    nb_cours = len(s["cours"])
    gradient, emoji = sc.visual_for(idx)
    blurb = FEATURED_BLURBS.get(s["nom"])
    if not blurb:
        top_styles = ", ".join(style_set[:3])
        blurb = f"{nb_cours} créneau{'x' if nb_cours > 1 else ''} vérifié{'s' if nb_cours > 1 else ''} par semaine · {top_styles}"
    badges = "".join(f'<span class="style-badge">{t}</span>' for t in style_set[:4])
    planning_link = "Yoga_a_Lyon_Planning.html?studio=" + s["nom"].replace(" ", "%20").replace("&", "%26")
    return f"""
      <div class="studio-card" data-arr="{s['arr']}">
        <div class="studio-photo" style="background:{gradient};"><span>{emoji}</span></div>
        <div class="studio-body">
          <div class="studio-name">{s['nom']}</div>
          <div class="studio-quartier">{s['quartier']} · {s['arr']}</div>
          <p class="studio-desc">{blurb}</p>
          <div class="studio-badges">{badges}</div>
          <a href="{planning_link}" class="studio-link">Voir leur planning →</a>
        </div>
      </div>"""


studio_cards_html = "".join(studio_card(s, i) for i, s in enumerate(studios))

arr_pills_html = '<button type="button" class="arr-pill active" onclick="filterArr(this, \'\')">Tous</button>'
for a in arrondissements:
    arr_pills_html += f'<button type="button" class="arr-pill" onclick="filterArr(this, \'{a}\')">{a}</button>'

PAGE_CSS = """
  .studios-header { max-width: 1180px; margin: 0 auto; padding: 56px 24px 20px; }
  .studios-header h1 { font-size: 32px; font-weight: 500; margin: 0 0 10px; }
  .studios-header p { color: #6a5a78; font-size: 16px; margin: 0; }

  .map-section { max-width: 1180px; margin: 0 auto; padding: 20px 24px 30px; }
  #studios-map { width: 100%; height: 380px; border-radius: 18px; overflow: hidden; background: var(--border); }

  .arr-pills { max-width: 1180px; margin: 0 auto; padding: 0 24px 24px; display: flex; gap: 10px; flex-wrap: wrap; }
  .arr-pill { padding: 9px 18px; border-radius: var(--pill-radius); font-size: 13.5px; font-weight: 600; cursor: pointer;
    border: 1px solid var(--lavender); background: #fff; color: var(--brand-purple); font-family: 'Inter', sans-serif; }
  .arr-pill.active { background: var(--brand-purple); color: #FBF8F4; border-color: var(--brand-purple); }
  .arr-pill:hover:not(.active) { border-color: var(--brand-purple); }

  .studios-grid-wrap { max-width: 1180px; margin: 0 auto; padding: 20px 24px 70px; }
  .studios-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 28px; }
  .studio-card { background: #fff; border-radius: 18px; overflow: hidden; display: flex; flex-direction: column; transition: transform 0.2s, box-shadow 0.2s; }
  .studio-card:hover { transform: translateY(-4px); box-shadow: 0 16px 32px rgba(65,41,87,0.12); }
  .studio-photo { width: 100%; height: 170px; display: flex; align-items: center; justify-content: center; }
  .studio-photo span { font-size: 3em; }
  .studio-body { padding: 20px 22px; display: flex; flex-direction: column; gap: 10px; flex: 1; }
  .studio-name { font-family: 'Fraunces', serif; font-size: 18px; font-weight: 500; }
  .studio-quartier { font-size: 12.5px; color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
  .studio-desc { font-size: 14px; color: #5a4a68; line-height: 1.5; margin: 0; }
  .studio-badges { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 2px; }
  .style-badge { font-size: 11.5px; font-weight: 600; padding: 4px 10px; border-radius: var(--pill-radius); background: var(--lavender-soft); color: var(--brand-purple); }
  .studio-link { font-size: 14px; font-weight: 600; margin-top: 8px; }

  .cta-manage { background: var(--lavender-soft); padding: 56px 24px; text-align: center; }
  .cta-manage .inner { max-width: 560px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; gap: 14px; }
  .cta-manage h2 { font-size: 24px; font-weight: 500; margin: 0; }
  .cta-manage p { font-size: 14.5px; color: #6a5a78; margin: 0; }
  .cta-manage a { padding: 13px 28px; border-radius: var(--pill-radius); background: var(--brand-purple); color: #FBF8F4; font-size: 14.5px; font-weight: 600; }
  .cta-manage a:hover { color: #fff; opacity: 0.9; }
"""

html_out = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Studios de yoga à Lyon — Annuaire | Yoga In Lyon</title>
{sc.FONTS_LINK}
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
<style>
{sc.BASE_CSS}
{PAGE_CSS}
</style>
</head>
<body>

{sc.header_html('studios')}

<div class="studios-header">
  <h1>Trouver un studio de yoga à Lyon</h1>
  <p>Studios, quartiers et styles enseignés — pour choisir avant de regarder les horaires.</p>
</div>

<div class="map-section">
  <div id="studios-map"></div>
</div>

<div class="arr-pills" id="arr-pills">
  {arr_pills_html}
</div>

<div class="studios-grid-wrap">
  <div class="studios-grid" id="studios-grid">
    {studio_cards_html}
  </div>
</div>

<div class="cta-manage">
  <div class="inner">
    <h2>Vous gérez un studio ?</h2>
    <p>Pour ajouter, corriger ou mettre à jour les informations de votre studio, contactez-nous.</p>
    <a href="A-propos.html#contact">Nous contacter</a>
  </div>
</div>

{sc.footer_html()}

<script>
function filterArr(el, arr) {{
  document.querySelectorAll('.arr-pill').forEach(p => p.classList.remove('active'));
  el.classList.add('active');
  document.querySelectorAll('.studio-card').forEach(card => {{
    card.style.display = (!arr || card.dataset.arr === arr) ? '' : 'none';
  }});
}}
</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script>
const MARKERS = {markers_json};
const map = L.map('studios-map', {{ scrollWheelZoom: false }}).setView([45.764, 4.842], 12);
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  attribution: '&copy; OpenStreetMap contributors &copy; CARTO', subdomains: 'abcd', maxZoom: 19
}}).addTo(map);
MARKERS.forEach(m => {{
  L.circleMarker([m.lat, m.lng], {{ radius: 9, color: '#ffffff', weight: 2, fillColor: '#2c1c3d', fillOpacity: 1 }})
    .addTo(map)
    .bindPopup('<strong>' + m.nom + '</strong><br>' + m.quartier + ' (' + m.arr + ')');
}});
</script>

</body>
</html>
"""

with open('/sessions/inspiring-confident-ritchie/mnt/outputs/work/studios.html', 'w', encoding='utf-8') as f:
    f.write(html_out)

print("Studios genere:", len(html_out), "caracteres,", len(studios), "studios,", len(markers), "marqueurs")
