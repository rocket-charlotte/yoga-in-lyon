# -*- coding: utf-8 -*-
"""Photos des studios (utilisées avec l'accord des studios, obtenu par Charlotte en octobre 2026).

Par défaut, le déploiement récupère l'image principale que chaque studio a choisie pour son
site (balise og:image), la redimensionne et l'affiche avec le crédit « Photo : <studio> ».

Pour choisir une autre photo, ou en retirer une, ajoute une ligne ici :
    "Nom exact du studio": "https://adresse-complète-de-l-image.jpg",
    "Nom exact du studio": None,        # pas de photo pour ce studio
    "Nom exact du studio": "mon-fichier.jpg",   # photo déposée dans seo/photos/
"""

PHOTOS = {
    # Images principales inutilisables (logo, dessin, capture de planning) : à remplacer par une vraie photo
    "The Good Flow": None,
    "Les Ailes Hatha Yoga": None,
    "Studio Arbol Flow": None,
    "O Yoga Studio": None,
    "École de Yoga Horizon": None,
    "L'Atelier du Yoga": None,
}
