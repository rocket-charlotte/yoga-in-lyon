#!/usr/bin/env python3
"""Collecte ponctuelle : relit le site de chaque studio et garde les passages qui parlent de prix
et de cours d'essai. Lancée par .github/workflows/collect-tarifs.yml, résultat poussé sur la branche
« collecte ». Sert de base au relevé manuel des tarifs (seo/seo_tarifs.py)."""
import html, json, re, sys, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "collecte")
OUT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (YogaInLyon; contact@yoga-in-lyon.fr)"}
KEY = re.compile(r"tarif|prix|price|pricing|abonnement|essai|d[ée]couverte|offre|formule|carte|pass|trial|cours-unique|inscription|adh[ée]sion", re.I)
HIT = re.compile(r"€|euros?\b|essai|d[ée]couverte|offert|gratuit|1er cours|premier cours|trial|free", re.I)


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.geturl(), r.read(3_000_000).decode("utf-8", "ignore")


def text_of(page):
    page = re.sub(r"(?is)<(script|style|noscript|svg)\b.*?</\1>", " ", page)
    page = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h\d|tr|td|section|span)>", "\n", page)
    t = html.unescape(re.sub(r"<[^>]+>", " ", page))
    lines = [re.sub(r"\s+", " ", l).strip() for l in t.split("\n")]
    return [l for l in lines if l]


plan = (ROOT / "Yoga_a_Lyon_Planning.html").read_text(encoding="utf-8")
data = json.loads(re.search(r"const DATA = (\[.*?\]);\s*\n", plan, re.S).group(1))
studios = {}
for c in data:
    studios.setdefault(c["studio"], c["site"])

summary = []
for name, site in studios.items():
    root = "{0.scheme}://{0.netloc}/".format(urllib.parse.urlparse(site))
    todo, seen, pages = [site, root], set(), []
    while todo and len(pages) < 8:
        u = todo.pop(0)
        if u in seen:
            continue
        seen.add(u)
        try:
            final, page = get(u)
        except Exception as e:
            pages.append((u, f"ERREUR {type(e).__name__}", []))
            continue
        lines = text_of(page)
        pages.append((final, "ok", lines))
        for href, label in re.findall(r'<a[^>]+href=["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', page, re.I | re.S):
            full = urllib.parse.urljoin(final, html.unescape(href))
            lab = re.sub(r"<[^>]+>", " ", label)
            if urllib.parse.urlparse(full).netloc == urllib.parse.urlparse(final).netloc and (KEY.search(full) or KEY.search(lab)):
                if full not in seen and full not in todo:
                    todo.append(full)
        for src in re.findall(r'<iframe[^>]+src=["\']([^"\']+)', page, re.I):
            pages.append((urllib.parse.urljoin(final, src), "iframe (non lu)", []))
    out = [f"# {name}\nsite planning : {site}\n"]
    n_hits = 0
    for u, status, lines in pages:
        out.append(f"\n## {u}  [{status}]")
        keep = set()
        for i, l in enumerate(lines):
            if HIT.search(l):
                keep.update(range(max(0, i - 2), min(len(lines), i + 3)))
        for i in sorted(keep):
            out.append(lines[i][:300])
        n_hits += len(keep)
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    (OUT / f"{slug}.md").write_text("\n".join(out), encoding="utf-8")
    summary.append(f"{name}: {len(pages)} pages, {n_hits} lignes utiles")
(OUT / "_resume.txt").write_text("\n".join(summary), encoding="utf-8")
print("\n".join(summary))
