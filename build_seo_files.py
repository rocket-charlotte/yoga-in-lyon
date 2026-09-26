# -*- coding: utf-8 -*-
"""Genere sitemap.xml et robots.txt a la racine du site (dossier dist du deploiement)."""
import datetime
import site_common as sc

OUT_DIR = '/sessions/inspiring-confident-ritchie/mnt/outputs/work'

today = datetime.date.today().isoformat()

static_pages = [
    ("", "1.0"),
    ("Yoga_a_Lyon_Planning.html", "0.9"),
    ("Studios.html", "0.9"),
    ("A-propos.html", "0.5"),
    ("Profs.html", "0.5"),
]
quartier_pages = [(sc.arr_page_filename(a), "0.8") for a in sc.all_arrondissements()]

urls = static_pages + quartier_pages

entries = "\n".join(
    f"""  <url>
    <loc>{sc.SITE_URL}/{path}</loc>
    <lastmod>{today}</lastmod>
    <priority>{priority}</priority>
  </url>"""
    for path, priority in urls
)

sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>
"""

robots = f"""User-agent: *
Allow: /

Sitemap: {sc.SITE_URL}/sitemap.xml
"""

with open(f'{OUT_DIR}/sitemap.xml', 'w', encoding='utf-8') as f:
    f.write(sitemap)
with open(f'{OUT_DIR}/robots.txt', 'w', encoding='utf-8') as f:
    f.write(robots)

print("sitemap.xml genere:", len(urls), "urls")
print("robots.txt genere")
