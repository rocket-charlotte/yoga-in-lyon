# -*- coding: utf-8 -*-
"""Genere une page statique par arrondissement/quartier (SEO longue traine :
"yoga + quartier"). Une page par valeur de sc.all_arrondissements()."""
import json
import site_common as sc

OUT_DIR = '/sessions/inspiring-confident-ritchie/mnt/outputs/work'

PAGE_CSS = """
  .quartier-hero { max-width: 1180px; margin: 0 auto; padding: 56px 24px 10px; }
  .quartier-hero .eyebrow { font-size: 12px; font-weight: 700; color: #9B7FB0; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 10px; }
  .quartier-hero h1 { font-size: 32px; font-weight: 500; margin: 0 0 14px; }
  .quartier-hero p { color: #6a5a78; font-size: 16px; line-height: 1.6; max-width: 760px; margin: 0 0 18px; }
  .quartier-hero .cta-btn { display: inline-block; padding: 13px 26px; border-radius: var(--pill-radius); background: var(--brand-purple); color: #FBF8F4; font-size: 14.5px; font-weight: 600; }
  .quartier-hero .cta-btn:hover { color: #fff; opacity: 0.9; }

  .map-section { max-width: 1180px; margin: 0 auto; padding: 20px 24px 30px; }
  #quartier-map { width: 100%; height: 320px; border-radius: 18px; overflow: hidden; background: var(--border); }

  .studios-grid-wrap { max-width: 1180px; margin: 0 auto; padding: 10px 24px 70px; }
  .studios-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 28px; }
  .studio-card { background: #fff; border-radius: 18px; overflow: hidden; display: flex; flex-direction: column; transition: transform 0.2s, box-shadow 0.2s; }
  .studio-card:hover { transform: translateY(-4px); box-shadow: 0 16px 32px rgba(65,41,87,0.12); }
  .studio-photo { width: 100%; height: 150px; display: flex; align-items: center; justify-content: center; }
  .studio-photo span { font-size: 3em; }
  .studio-body { padding: 20px 22px; display: flex; flex-direction: column; gap: 10px; flex: 1; }
  .studio-name { font-family: 'Fraunces', serif; font-size: 18px; font-weight: 500; }
  .studio-quartier { font-size: 12.5px; color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
  .studio-desc { font-size: 14px; color: #5a4a68; line-height: 1.5; margin: 0; }
  .studio-badges { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 2px; }
  .style-badge { font-size: 11.5px; font-weight: 600; padding: 4px 10px; border-radius: var(--pill-radius); background: var(--lavender-soft); color: var(--brand-purple); }
  .studio-link { font-size: 14px; font-weight: 600; margin-top: 8px; }

  .other-quartiers { max-width: 1180px; margin: 0 auto; padding: 0 24px 70px; }
  .other-quartiers h2 { font-size: 20px; font-weight: 500; margin: 0 0 16px; }
  .other-quartiers .links { display: flex; flex-wrap: wrap; gap: 10px; }
  .other-quartiers a { padding: 9px 18px; border-radius: 999px; background: var(--lavender-soft); color: var(--brand-purple); font-size: 13.5px; font-weight: 600; }
  .other-quartiers a:hover { background: var(--lavender); }
"""


def studio_card(s, idx):
    style_set = sorted(set(sc.type_simplifie(c["type"]) for c in s["cours"]))
    nb_cours = len(s["cours"])
    gradient, emoji = sc.visual_for(idx)
    top_styles = ", ".join(style_set[:3])
    blurb = f"{nb_cours} créneau{'x' if nb_cours > 1 else ''} vérifié{'s' if nb_cours > 1 else ''} par semaine · {top_styles}"
    badges = "".join(f'<span class="style-badge">{t}</span>' for t in style_set[:4])
    planning_link = "Yoga_a_Lyon_Planning.html?studio=" + s["nom"].replace(" ", "%20").replace("&", "%26")
    return f"""
      <div class="studio-card">
        <div class="studio-photo" style="background:{gradient};"><span>{emoji}</span></div>
        <div class="studio-body">
          <div class="studio-name">{s['nom']}</div>
          <div class="studio-quartier">{s['quartier']} · {s['arr']}</div>
          <p class="studio-desc">{blurb}</p>
          <div class="studio-badges">{badges}</div>
          <a href="{planning_link}" class="studio-link">Voir leur planning →</a>
        </div>
      </div>"""


def build_page(arr, all_arrs):
    studios_arr = [s for s in sc.STUDIOS if s["arr"] == arr]
    creneaux_arr = [c for c in sc.all_creneaux() if c["arr"] == arr]
    types_arr = sorted(set(c["type_simple"] for c in creneaux_arr))
    label = sc.arr_label(arr)
    filename = sc.arr_page_filename(arr)

    markers = []
    for s in studios_arr:
        coord = sc.COORDS.get(s["nom"])
        if not coord:
            continue
        markers.append({"nom": s["nom"], "lat": coord[0], "lng": coord[1]})
    markers_json = json.dumps(markers, ensure_ascii=False)

    studio_cards_html = "".join(studio_card(s, i) for i, s in enumerate(studios_arr))
    item_list_json = sc.item_list_jsonld(studios_arr)

    other_links = "".join(
        f'<a href="{sc.arr_page_filename(a)}">Yoga {a}</a>' for a in all_arrs if a != arr
    )

    styles_txt = ", ".join(types_arr) if types_arr else "plusieurs styles de yoga"

    title = f"Yoga à {label} — Studios et cours | Yoga In Lyon"
    description = (
        f"Cours de yoga à {label} : {len(studios_arr)} studio"
        f"{'s' if len(studios_arr) > 1 else ''} vérifié"
        f"{'s' if len(studios_arr) > 1 else ''}, {len(creneaux_arr)} créneau"
        f"{'x' if len(creneaux_arr) > 1 else ''} par semaine ({styles_txt})."
    )

    html_out = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
{sc.seo_head(title, description, filename)}
{sc.FONTS_LINK}
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
<script type="application/ld+json">{item_list_json}</script>
<style>
{sc.BASE_CSS}
{PAGE_CSS}
</style>
</head>
<body>

{sc.header_html('studios')}

<div class="quartier-hero">
  <div class="eyebrow">Yoga In Lyon</div>
  <h1>Cours de yoga à {label}</h1>
  <p>{description} Retrouvez ci-dessous les studios du secteur avec leurs styles enseignés, ou consultez directement le planning complet filtré sur {label.split(' arrondissement')[0] if 'arrondissement' in label else label}.</p>
  <a class="cta-btn" href="Yoga_a_Lyon_Planning.html?arr={arr.replace(' ', '%20')}">Voir le planning complet de {label}</a>
</div>

<div class="map-section">
  <div id="quartier-map"></div>
</div>

<div class="studios-grid-wrap">
  <div class="studios-grid">
    {studio_cards_html}
  </div>
</div>

<div class="other-quartiers">
  <h2>Yoga dans les autres quartiers de Lyon</h2>
  <div class="links">{other_links}</div>
</div>

{sc.footer_html()}

<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script>
const MARKERS = {markers_json};
const map = L.map('quartier-map', {{ scrollWheelZoom: false }}).setView(
  MARKERS.length ? [MARKERS[0].lat, MARKERS[0].lng] : [45.764, 4.842], 13
);
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  attribution: '&copy; OpenStreetMap contributors &copy; CARTO', subdomains: 'abcd', maxZoom: 19
}}).addTo(map);
MARKERS.forEach(m => {{
  L.circleMarker([m.lat, m.lng], {{ radius: 9, color: '#ffffff', weight: 2, fillColor: '#2c1c3d', fillOpacity: 1 }})
    .addTo(map)
    .bindPopup('<strong>' + m.nom + '</strong>');
}});
</script>

</body>
</html>
"""
    with open(f'{OUT_DIR}/{filename}', 'w', encoding='utf-8') as f:
        f.write(html_out)
    return filename, len(studios_arr), len(creneaux_arr)


all_arrs = sc.all_arrondissements()
results = [build_page(a, all_arrs) for a in all_arrs]
for filename, n_studios, n_creneaux in results:
    print(f"{filename}: {n_studios} studios, {n_creneaux} creneaux")
print(len(results), "pages quartier generees")
