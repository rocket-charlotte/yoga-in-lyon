# -*- coding: utf-8 -*-
import json, html
import site_common as sc

studios = sc.STUDIOS
creneaux = sc.all_creneaux()

arrondissements = sorted(set(c["arr"] for c in creneaux))
quartiers = sorted(set(c["quartier"] for c in creneaux))
jours = sorted(set(c["jour"] for c in creneaux), key=sc.jour_key)
types = sorted(set(c["type_simple"] for c in creneaux))
CRENEAUX_ORDRE = ["Matin", "Midi", "Après-midi", "Soir"]
creneaux_horaires = [c for c in CRENEAUX_ORDRE if c in set(x["creneau"] for x in creneaux)]

data_json = json.dumps(creneaux, ensure_ascii=False)
style_colors_json = json.dumps({t: sc.style_colors(t) for t in types}, ensure_ascii=False)


def checkbox_group(name, options, group_id, with_dot=False):
    items = ""
    for o in options:
        dot_html = ""
        if with_dot:
            colors = sc.style_colors(o)
            dot_html = f'<span class="chk-dot" style="background:{colors["dot"]};"></span>'
        items += (
            f'<label class="chk"><input type="checkbox" class="{group_id}-cb" value="{html.escape(o)}" '
            f'onchange="render()">{dot_html}<span class="chk-label">{html.escape(o)}</span></label>'
        )
    controls = (
        f'<div class="group-controls">'
        f'<a href="#" onclick="toggleGroup(\'{group_id}\', true); return false;">Tout</a>'
        f'<span class="sep">/</span>'
        f'<a href="#" onclick="toggleGroup(\'{group_id}\', false); return false;">Aucun</a>'
        f'</div>'
    )
    return f'<div class="filter-box"><div class="filter-title-row"><h3 class="filter-title">{name}</h3>{controls}</div><div class="chk-list">{items}</div></div>'


filters_html = (
    checkbox_group("Arrondissement", arrondissements, "arr")
    + checkbox_group("Jour", jours, "jour")
    + checkbox_group("Créneau horaire", creneaux_horaires, "creneau")
    + checkbox_group("Type de yoga", types, "type", with_dot=True)
)

search_bar_html = (
    '<div class="search-bar">'
    + sc.search_select("Style de yoga", types, "search-type", "Tous les styles")
    + sc.search_select("Jour", jours, "search-jour", "Tous les jours")
    + sc.search_select("Créneau", creneaux_horaires, "search-creneau", "Toute la journée")
    + sc.search_select("Arrondissement", arrondissements, "search-arr", "Tous les arrondissements")
    + '<button type="button" class="search-btn" onclick="onSearchBar()">Filtrer</button>'
    + '</div>'
)

PAGE_CSS = """
  body { background: var(--bg); }
  .hero-banner { position: relative; width: 100%; height: 220px; overflow: hidden; }
  .hero-banner img { width: 100%; height: 100%; object-fit: cover; object-position: 50% 60%; display: block; }
  .hero-banner .overlay { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(44,28,61,0.35), rgba(44,28,61,0.6)); }
  .page-title-wrap { max-width: 1280px; margin: 0 auto; padding: 28px 24px 0; }
  .page-title-wrap h1 { font-size: 30px; font-weight: 500; margin: 8px 0 20px; }

  .layout { max-width: 1280px; margin: 0 auto; padding: 34px 24px 80px; display: grid; grid-template-columns: 260px 1fr; gap: 32px; align-items: start; }
  @media (max-width: 860px) { .layout { grid-template-columns: 1fr; } }

  .sidebar { display: flex; flex-direction: column; gap: 26px; position: sticky; top: 96px; align-self: start; }
  @media (max-width: 860px) {
    .sidebar { position: static; top: auto; }
  }
  .result-box { background: var(--lavender-soft); border-radius: 14px; padding: 18px 20px; display: flex; flex-direction: column; gap: 4px; }
  .result-box .num { font-family: 'Fraunces', serif; font-size: 22px; font-weight: 600; color: var(--brand-purple); }
  .result-box .sub { font-size: 12.5px; color: var(--muted); }
  .reset-link { font-size: 12px; text-align: right; }

  .filter-box { border-top: 1px solid var(--border); padding-top: 14px; }
  .filter-box:first-of-type { border-top: none; padding-top: 0; }
  .filter-title-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
  .filter-title { font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--brand-purple); margin: 0; }
  .group-controls { display: flex; gap: 8px; font-size: 11.5px; }
  .group-controls a { color: var(--muted); }
  .group-controls a:hover { color: var(--brand-purple); }
  .group-controls .sep { color: #ccc; }
  .chk-list { display: flex; flex-direction: column; gap: 9px; max-height: 190px; overflow-y: auto; padding-right: 2px; }
  .chk { display: flex; align-items: center; gap: 9px; font-size: 14px; cursor: pointer; color: var(--ink); }
  .chk-dot { width: 9px; height: 9px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
  .chk-label { line-height: 1.3; }

  main.content { min-width: 0; display: flex; flex-direction: column; gap: 36px; }
  .result-count { font-size: 14px; color: var(--muted); }
  .day-section-head { display: flex; align-items: center; gap: 14px; margin: 0 0 16px; padding-bottom: 10px; border-bottom: 1px solid var(--border); }
  .day-num { width: 36px; height: 36px; border-radius: 50%; background: var(--brand-purple); color: #FBF8F4; display: flex; align-items: center; justify-content: center; font-family: 'Fraunces', serif; font-size: 15px; font-weight: 600; flex-shrink: 0; }
  .day-title { font-size: 22px; font-weight: 500; margin: 0; }
  .course-list { display: flex; flex-direction: column; gap: 12px; }
  .course-card { display: flex; align-items: stretch; background: #fff; border: 1px solid var(--border); border-radius: 14px; overflow: hidden; transition: box-shadow 0.15s, transform 0.15s; }
  .course-card:hover { box-shadow: 0 10px 24px rgba(65,41,87,0.14); transform: translateY(-2px); }
  .course-card .stripe { width: 4px; flex-shrink: 0; }
  .course-card .body { display: flex; align-items: center; gap: 18px; padding: 16px 22px; flex: 1; min-width: 0; flex-wrap: wrap; }
  .course-card .avatar { width: 38px; height: 38px; border-radius: 8px; flex-shrink: 0; background-color: var(--lavender-soft); background-size: 20px 20px; background-position: center; background-repeat: no-repeat; }
  .course-card .info { flex: 1 1 auto; min-width: 160px; }
  .course-card .info .name { font-size: 16px; font-weight: 600; color: var(--ink); }
  .course-card .info .sub { font-size: 12.5px; color: var(--muted); margin-top: 2px; }
  .course-card .time { flex: 0 0 auto; font-size: 14.5px; font-weight: 600; color: var(--brand-purple); }
  .course-card .badge { flex: 0 0 auto; font-size: 12px; font-weight: 600; padding: 5px 12px; border-radius: var(--pill-radius); }
  .course-card .site-link { flex: 0 0 auto; font-size: 13.5px; font-weight: 600; }
  .empty-msg { text-align: center; color: var(--muted-soft); padding: 60px 0; font-size: 15px; }

  .methodology { max-width: 1280px; margin: 0 auto; padding: 0 24px 40px; font-size: 12.5px; color: var(--muted); line-height: 1.7; }
"""

html_out = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Yoga à Lyon — Plannings des cours</title>
{sc.FONTS_LINK}
<style>
{sc.BASE_CSS}
{PAGE_CSS}
</style>
</head>
<body>

{sc.header_html('planning')}

<section class="hero-banner">
  <img src="banner_web.jpg" alt="">
  <div class="overlay"></div>
</section>

<div class="page-title-wrap">
  <h1>Tous les cours de yoga à Lyon</h1>
</div>

<div class="search-bar-wrap">
  {search_bar_html}
</div>

<div class="layout">

  <aside class="sidebar">
    <div class="result-box">
      <div class="num" id="result-num"></div>
      <div class="sub" id="result-sub"></div>
    </div>
    <div class="reset-link"><a href="#" onclick="resetFilters(); return false;">Réinitialiser les filtres</a></div>
    {filters_html}
  </aside>

  <main class="content">
    <div class="result-count" id="count"></div>
    <div id="results"></div>
    <div class="empty-msg" id="empty" style="display:none;">Aucun cours ne correspond à ces filtres. Essayez d'en décocher quelques-uns.</div>
  </main>

</div>

<p class="methodology"><strong>Méthodologie :</strong> ce site recense uniquement les cours de yoga à Lyon pour lesquels un jour et un horaire précis et actuel ont pu être vérifiés (page planning publiée en clair sur le site du studio, ou capture d'écran du planning fournie). {len(studios)} studios et {len(creneaux)} créneaux ont été confirmés à ce stade. Pour les studios non listés ici, mieux vaut consulter directement leur site ou application de réservation.</p>

{sc.footer_html()}

<script>
const DATA = {data_json};
const STYLE_COLORS = {style_colors_json};

function getChecked(groupClass) {{
  return Array.from(document.querySelectorAll('.' + groupClass + '-cb:checked')).map(el => el.value);
}}

function toggleGroup(groupClass, state) {{
  document.querySelectorAll('.' + groupClass + '-cb').forEach(el => el.checked = state);
  render();
}}

function setSingleCheck(groupClass, value) {{
  document.querySelectorAll('.' + groupClass + '-cb').forEach(el => {{
    el.checked = value ? (el.value === value) : false;
  }});
}}

function onSearchBar() {{
  const typeVal = document.getElementById('search-type').value;
  const jourVal = document.getElementById('search-jour').value;
  const creneauVal = document.getElementById('search-creneau').value;
  const arrVal = document.getElementById('search-arr').value;
  setSingleCheck('type', typeVal);
  setSingleCheck('jour', jourVal);
  setSingleCheck('creneau', creneauVal);
  setSingleCheck('arr', arrVal);
  render();
}}

let STUDIO_FILTER = null;

function render() {{
  const arrs = getChecked('arr');
  const joursSel = getChecked('jour');
  const creneauxSel = getChecked('creneau');
  const typesSel = getChecked('type');

  const filtered = DATA.filter(c =>
    (arrs.length === 0 || arrs.includes(c.arr)) &&
    (joursSel.length === 0 || joursSel.includes(c.jour)) &&
    (creneauxSel.length === 0 || creneauxSel.includes(c.creneau)) &&
    (typesSel.length === 0 || typesSel.includes(c.type_simple)) &&
    (!STUDIO_FILTER || c.studio === STUDIO_FILTER)
  );

  const countEl = document.getElementById('count');
  countEl.textContent = "";
  if (STUDIO_FILTER) {{
    countEl.textContent = filtered.length + " cours trouvé" + (filtered.length > 1 ? "s" : "") + " — studio : " + STUDIO_FILTER + "  ";
    const clearLink = document.createElement('a');
    clearLink.href = "#";
    clearLink.textContent = "(voir tous les studios)";
    clearLink.onclick = (e) => {{ e.preventDefault(); STUDIO_FILTER = null; render(); }};
    countEl.appendChild(clearLink);
  }} else {{
    countEl.textContent = filtered.length + " cours trouvé" + (filtered.length > 1 ? "s" : "");
  }}
  document.getElementById('result-num').textContent = filtered.length + " cours";
  const nbStudios = new Set(filtered.map(c => c.studio)).size;
  document.getElementById('result-sub').textContent = "sur " + nbStudios + " studio" + (nbStudios > 1 ? "s" : "") + " à Lyon";

  const resultsEl = document.getElementById('results');
  const emptyEl = document.getElementById('empty');

  if (filtered.length === 0) {{
    resultsEl.innerHTML = "";
    emptyEl.style.display = "block";
    return;
  }}
  emptyEl.style.display = "none";

  const joursOrdre = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"];
  const groups = {{}};
  filtered.forEach(c => {{
    if (!groups[c.jour]) groups[c.jour] = [];
    groups[c.jour].push(c);
  }});

  const joursTries = Object.keys(groups).sort((a,b) => {{
    const ia = joursOrdre.findIndex(j => a.startsWith(j));
    const ib = joursOrdre.findIndex(j => b.startsWith(j));
    return (ia<0?99:ia) - (ib<0?99:ib);
  }});

  let outHtml = "";
  joursTries.forEach(jour => {{
    const dayNum = joursOrdre.findIndex(j => jour.startsWith(j)) + 1;
    outHtml += `<div class="day-section"><div class="day-section-head"><div class="day-num">${{dayNum > 0 ? dayNum : '·'}}</div><h2 class="day-title">${{jour}}</h2></div><div class="course-list">`;
    groups[jour].sort((a,b) => a.debut.localeCompare(b.debut));
    groups[jour].forEach(c => {{
      const colors = STYLE_COLORS[c.type_simple] || STYLE_COLORS["Hatha Yoga"];
      outHtml += `
        <div class="course-card">
          <div class="stripe" style="background:${{colors.dot}};"></div>
          <div class="body">
            <div class="avatar" style="background-image:url('${{c.favicon}}');"></div>
            <div class="info">
              <div class="name">${{c.type}}</div>
              <div class="sub">${{c.studio}} · ${{c.quartier}} (${{c.arr}})</div>
            </div>
            <div class="time">${{c.debut}}${{c.fin ? ' – ' + c.fin : ''}}</div>
            <div class="badge" style="background:${{colors.bg}};color:${{colors.text}};">${{c.type_simple}}</div>
            <a class="site-link" href="${{c.site}}" target="_blank" rel="noopener">Voir le site →</a>
          </div>
        </div>`;
    }});
    outHtml += `</div></div>`;
  }});

  resultsEl.innerHTML = outHtml;
}}

function resetFilters() {{
  document.querySelectorAll('input[type=checkbox]').forEach(el => el.checked = false);
  document.getElementById('search-type').value = "";
  document.getElementById('search-jour').value = "";
  document.getElementById('search-creneau').value = "";
  document.getElementById('search-arr').value = "";
  STUDIO_FILTER = null;
  render();
}}

function applyUrlParams() {{
  const params = new URLSearchParams(window.location.search);
  const qType = params.get('type') || "";
  const qJour = params.get('jour') || "";
  const qCreneau = params.get('creneau') || "";
  const qArr = params.get('arr') || params.get('quartier') || "";
  const qStudio = params.get('studio') || "";
  if (qType) document.getElementById('search-type').value = qType;
  if (qJour) document.getElementById('search-jour').value = qJour;
  if (qCreneau) document.getElementById('search-creneau').value = qCreneau;
  if (qArr) document.getElementById('search-arr').value = qArr;
  setSingleCheck('type', qType);
  setSingleCheck('jour', qJour);
  if (qCreneau) setSingleCheck('creneau', qCreneau);
  if (qArr) setSingleCheck('arr', qArr);
  STUDIO_FILTER = qStudio || null;
}}

applyUrlParams();
render();
</script>

</body>
</html>
"""

with open('/sessions/inspiring-confident-ritchie/mnt/outputs/work/yoga_lyon_planning.html', 'w', encoding='utf-8') as f:
    f.write(html_out)

print("Site genere:", len(html_out), "caracteres")
print(len(creneaux), "creneaux,", len(studios), "studios,", len(arrondissements), "arrondissements,", len(types), "types,", len(jours), "jours,", len(creneaux_horaires), "creneaux horaires")
