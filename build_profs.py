# -*- coding: utf-8 -*-
import site_common as sc

PAGE_CSS = """
  .profs-section {
    max-width: 620px; margin: 0 auto; padding: 110px 24px 120px; text-align: center;
    display: flex; flex-direction: column; align-items: center; gap: 20px;
  }
  .profs-section .eyebrow { font-size: 12px; font-weight: 700; color: #9B7FB0; text-transform: uppercase; letter-spacing: 0.1em; }
  .profs-section h1 { font-size: 34px; font-weight: 500; margin: 0; }
  .profs-section p { font-size: 16px; color: #6a5a78; line-height: 1.6; margin: 0; }
  .profs-form { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; width: 100%; max-width: 420px; margin-top: 8px; }
  .profs-form input { flex: 1 1 220px; padding: 13px 18px; border-radius: var(--pill-radius); border: 1px solid var(--lavender); font-size: 14.5px; }
  .profs-form button {
    flex: 0 0 auto; padding: 13px 26px; border-radius: var(--pill-radius); border: none;
    background: var(--brand-purple); color: #FBF8F4; font-weight: 600; font-size: 14.5px; cursor: pointer;
  }
  .profs-form button:hover { transform: scale(1.05); }
  .form-thanks { font-size: 15px; color: var(--brand-purple); font-weight: 600; padding: 10px 0; display: none; }
"""

html_out = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Profs de yoga à Lyon — Bientôt disponible | Yoga In Lyon</title>
{sc.seo_head(
    "Profs de yoga à Lyon — Bientôt disponible | Yoga In Lyon",
    "Bientôt : l'annuaire des professeurs de yoga à Lyon sur Yoga In Lyon. Inscrivez-vous pour être averti·e du lancement.",
    "Profs.html",
)}
{sc.FONTS_LINK}
<style>
{sc.BASE_CSS}
{PAGE_CSS}
</style>
</head>
<body>

{sc.header_html('profs')}

<section class="profs-section">
  <div class="eyebrow">Bientôt disponible</div>
  <h1>Tous les profs de yoga à Lyon</h1>
  <p>Une page dédiée aux professeurs de yoga lyonnais arrive prochainement. Vous êtes prof et souhaitez y apparaître dès son ouverture ?</p>
  <div class="form-thanks" id="profs-thanks">Merci, vous serez informé·e du lancement !</div>
  <form class="profs-form" id="profs-form" onsubmit="return submitProfs(event)">
    <input type="email" required placeholder="Votre email" id="profs-email">
    <button type="submit">Laissez votre email</button>
  </form>
</section>

{sc.footer_html()}

<script>
function submitProfs(e) {{
  e.preventDefault();
  const email = document.getElementById('profs-email').value;
  window.location.href = 'mailto:contact@yoga-in-lyon.fr?subject=' + encodeURIComponent('Prof de yoga - page Profs') + '&body=' + encodeURIComponent('Prévenez-moi au lancement de la page Profs : ' + email);
  document.getElementById('profs-thanks').style.display = 'block';
  document.getElementById('profs-form').style.display = 'none';
  return false;
}}
</script>

</body>
</html>
"""

with open('/sessions/inspiring-confident-ritchie/mnt/outputs/work/profs.html', 'w', encoding='utf-8') as f:
    f.write(html_out)

print("Profs genere:", len(html_out), "caracteres")
