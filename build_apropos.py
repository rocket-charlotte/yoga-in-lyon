# -*- coding: utf-8 -*-
import site_common as sc

studios = sc.STUDIOS
creneaux = sc.all_creneaux()
total_studios = len(studios)
total_creneaux = len(creneaux)
total_zones = len(set(c["arr"] for c in creneaux))

PAGE_CSS = """
  .apropos-hero { max-width: 1100px; margin: 0 auto; padding: 70px 24px 60px; display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 48px; align-items: center; }
  @media (max-width: 780px) { .apropos-hero { grid-template-columns: 1fr; } }
  .apropos-hero .eyebrow { font-size: 12px; font-weight: 700; color: #9B7FB0; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 10px; }
  .apropos-hero h1 { font-size: 38px; font-weight: 500; margin: 0 0 20px; }
  .apropos-hero p { font-size: 16px; color: #4a3a58; line-height: 1.7; margin: 0 0 16px; }
  .apropos-badges { display: flex; gap: 14px; flex-wrap: wrap; margin-top: 12px; }
  .apropos-badges span { padding: 8px 16px; border-radius: var(--pill-radius); background: var(--lavender-soft); color: var(--brand-purple); font-size: 13px; font-weight: 600; }
  .apropos-visual { position: relative; }
  .apropos-visual .backdrop { position: absolute; top: -24px; right: -24px; width: 90%; height: 90%; border-radius: 32px; background: var(--lavender); z-index: 0; }
  .apropos-visual .panel {
    position: relative; z-index: 1; width: 100%; height: 340px; border-radius: 28px;
    background: linear-gradient(135deg, #f0d9a8, #cdbdf5); display: flex; align-items: center; justify-content: center;
  }

  .contact-section { background: var(--lavender-soft); padding: 60px 24px; position: relative; overflow: hidden; }
  .contact-section .deco { position: absolute; top: -20px; left: -20px; opacity: 0.5; }
  .contact-section .inner { max-width: 560px; margin: 0 auto; position: relative; z-index: 1; }
  .contact-section h2 { font-size: 26px; font-weight: 500; margin: 0 0 8px; text-align: center; }
  .contact-section .sub { font-size: 14.5px; color: #6a5a78; margin: 0 0 28px; text-align: center; }
  .contact-form { display: flex; flex-direction: column; gap: 14px; }
  .contact-form input, .contact-form textarea {
    padding: 13px 16px; border-radius: 12px; border: 1px solid var(--lavender); font-size: 14.5px;
    background: #fff; font-family: 'Inter', sans-serif;
  }
  .contact-form textarea { resize: vertical; }
  .contact-form button {
    padding: 14px 0; border-radius: var(--pill-radius); border: none; background: var(--brand-purple);
    color: #FBF8F4; font-weight: 600; font-size: 15px; cursor: pointer;
  }
  .contact-form button:hover { transform: scale(1.01); }
  .form-thanks { text-align: center; font-size: 15px; color: var(--brand-purple); font-weight: 600; padding: 24px 0; display: none; }
"""

html_out = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Qui sommes-nous — Yoga In Lyon</title>
{sc.seo_head(
    "Qui sommes-nous — Yoga In Lyon",
    "Yoga In Lyon est un annuaire indépendant des studios et cours de yoga à Lyon, avec des créneaux vérifiés studio par studio.",
    "A-propos.html",
)}
{sc.FONTS_LINK}
<style>
{sc.BASE_CSS}
{PAGE_CSS}
</style>
</head>
<body>

{sc.header_html('apropos')}

<section class="apropos-hero">
  <div>
    <div class="eyebrow">L'équipe</div>
    <h1>Qui sommes-nous</h1>
    <p>Yoga in Lyon est un annuaire indépendant né d'un constat simple : trouver un cours de yoga à l'horaire et dans le quartier qui nous convient prend souvent plus de temps que la séance elle-même.</p>
    <p>Nous recensons les studios de Lyon un par un, avec leurs créneaux réels, pour vous éviter d'ouvrir dix onglets avant de dérouler votre tapis.</p>
    <p>Le site est encore jeune : {total_studios} studios référencés à ce jour, du 1er au 9e arrondissement et à Villeurbanne, avec l'ambition de couvrir tout le Grand Lyon.</p>
    <div class="apropos-badges">
      <span>{total_studios} studios</span>
      <span>{total_creneaux} créneaux/semaine</span>
      <span>{total_zones} zones couvertes</span>
    </div>
  </div>
  <div class="apropos-visual">
    <div class="backdrop"></div>
    <div class="panel">
      <svg width="120" height="120" viewBox="0 0 44 44"><g transform="translate(22,26)"><ellipse cx="0" cy="-10" rx="7" ry="13" fill="none" stroke="#412957" stroke-width="1.4" transform="rotate(-28)"></ellipse><ellipse cx="0" cy="-10" rx="7" ry="13" fill="#ffffff" opacity="0.5" transform="rotate(0)"></ellipse><ellipse cx="0" cy="-10" rx="7" ry="13" fill="none" stroke="#412957" stroke-width="1.4" transform="rotate(28)"></ellipse></g></svg>
    </div>
  </div>
</section>

<section id="contact" class="contact-section">
  <svg class="deco" width="140" height="140" viewBox="0 0 44 44"><circle cx="22" cy="12" r="6" fill="none" stroke="#412957" stroke-width="1.5"></circle><circle cx="13" cy="29" r="6" fill="#D9C6EC" opacity="0.7"></circle><circle cx="31" cy="29" r="6" fill="none" stroke="#412957" stroke-width="1.5"></circle></svg>
  <div class="inner">
    <h2>Nous contacter</h2>
    <p class="sub">Studio à ajouter ou à corriger, question, suggestion : écrivez-nous.</p>
    <div class="form-thanks" id="contact-thanks">Merci, votre message a été envoyé !</div>
    <form class="contact-form" id="contact-form" onsubmit="return submitContact(event)">
      <input type="text" required placeholder="Votre nom" id="contact-name">
      <input type="email" required placeholder="Votre email" id="contact-email">
      <textarea required placeholder="Votre message" id="contact-message" rows="4"></textarea>
      <button type="submit">Envoyer</button>
    </form>
  </div>
</section>

{sc.footer_html()}

<script>
function submitContact(e) {{
  e.preventDefault();
  const name = document.getElementById('contact-name').value;
  const email = document.getElementById('contact-email').value;
  const message = document.getElementById('contact-message').value;
  const body = 'De : ' + name + ' (' + email + ')\\n\\n' + message;
  window.location.href = 'mailto:contact@yoga-in-lyon.fr?subject=' + encodeURIComponent('Message depuis Yoga In Lyon') + '&body=' + encodeURIComponent(body);
  document.getElementById('contact-thanks').style.display = 'block';
  document.getElementById('contact-form').style.display = 'none';
  return false;
}}
</script>

</body>
</html>
"""

with open('/sessions/inspiring-confident-ritchie/mnt/outputs/work/apropos.html', 'w', encoding='utf-8') as f:
    f.write(html_out)

print("A-propos genere:", len(html_out), "caracteres")
