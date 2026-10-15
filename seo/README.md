# Passe SEO — Yoga In Lyon

Dossier à copier tel quel à la racine du dépôt `yoga-in-lyon` (à côté de `index.html`).

## Fonctionnement

Rien à faire à la main : le déploiement GitHub Actions (`.github/workflows/deploy.yml`) lance
`python3 seo/seo_build.py dist` après avoir préparé le dossier `dist/`, à chaque push sur `main`.
Les pages du dépôt restent telles que les scripts `build_*.py` les génèrent ; la passe SEO
s'applique uniquement à la version mise en ligne, donc elle n'est jamais perdue quand tu régénères le site.

Pour prévisualiser en local :

```bash
mkdir -p /tmp/dist && cp *.html banner_web.jpg logo_web.png /tmp/dist/ && cp /tmp/dist/Accueil.html /tmp/dist/index.html
python3 seo/seo_build.py /tmp/dist
```

Le script est idempotent : on peut le relancer sans rien dupliquer.

## Ce que ça produit

- `studio-*.html` : une page par studio (26), avec adresse, styles, planning de la semaine en HTML, carte, studios voisins, données structurées `ExerciseGym` et fil d'Ariane.
- 9 pages par style : `hatha-yoga-lyon.html`, `vinyasa-yoga-lyon.html`, `yin-yoga-lyon.html`, `ashtanga-yoga-lyon.html`, `yoga-iyengar-lyon.html`, `kundalini-yoga-lyon.html`, `meditation-yoga-nidra-lyon.html`, `yoga-pilates-renforcement-lyon.html`, `hot-yoga-lyon.html`.
- Planning : les 315 cours sont écrits en HTML dans la page (Google les voit), le JavaScript filtre toujours par-dessus. Les horaires « 9h00 » deviennent « 09h00 » (ils étaient mal triés).
- Pages quartier : texte éditorial propre à chaque quartier, noms de studios en H3, liens vers les styles, fil d'Ariane.
- Toutes les pages : « Voir leur planning » pointe vers la page du studio, `Accueil.html` → `/`, la colonne « Réseaux » (liens vides) devient « Styles de yoga ».
- `sitemap.xml`, `robots.txt`, `.htaccess` (redirections https, sans www, `Accueil.html` → `/`).

## Modifier les textes

Tout est dans `seo/seo_content.py` (un texte par quartier, un par style). Une description maison saisie sur la page Studios est reprise automatiquement sur la page du studio.

## Avertissements affichés

Le script signale les données à corriger (adresse sans code postal, studio « Ashtanga » sans cours d'Ashtanga…). Ce ne sont pas des erreurs bloquantes.
