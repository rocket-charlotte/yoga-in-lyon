# -*- coding: utf-8 -*-
"""Profs de yoga publiés sur Yoga In Lyon.

N'ajoute un prof qu'avec son accord et les infos qu'il ou elle t'a envoyées.
Chaque entrée génère une page prof-<slug>.html, l'ajoute à la page Profs,
au sitemap et à la page des studios où il ou elle enseigne.

Champs :
  nom        (obligatoire) prénom + nom, tel que le prof veut apparaître
  titre      "Professeure de yoga" par défaut
  bio        2 à 6 phrases envoyées par le prof (HTML simple autorisé : <p>, <strong>)
  photo      nom d'un fichier placé dans seo/profs/ (jpg ou png, carré de préférence)
  site, instagram, reservation   liens complets (https://…), tous facultatifs
  formation  une ligne, ex. "RYT 500 Yoga Alliance, formée à Rishikesh"
  cours      où trouver ses cours dans le planning :
             {"studio": "<nom exact du studio>", "match": "<mot présent dans l'intitulé du cours>"}
             sans "match" = tous les cours de ce studio
  extra      cours hors planning (plein air, en ligne, cours particuliers) :
             {"jour": "Samedi", "debut": "10h00", "fin": "11h00", "type": "Yoga en plein air", "lieu": "Parc de la Tête d'Or"}

Exemple (à recopier sans le # devant chaque ligne) :

# {
#     "nom": "Camille Exemple",
#     "titre": "Professeure de yoga",
#     "bio": "<p>Je pratique depuis 12 ans et j'enseigne le Vinyasa depuis 2019...</p>",
#     "photo": "camille-exemple.jpg",
#     "instagram": "https://www.instagram.com/camille.exemple/",
#     "reservation": "https://exemple.fr/reserver",
#     "formation": "RYT 200 Yoga Alliance",
#     "cours": [{"studio": "Yoga Bellecour", "match": "Camille"}],
#     "extra": [{"jour": "Samedi", "debut": "10h00", "fin": "11h00",
#                "type": "Yoga en plein air", "lieu": "Parc de la Tête d'Or"}],
# },
"""

PROFS = [
]

# Studios du planning qui sont en réalité un prof indépendant : ils apparaissent
# dans la section « Profs indépendants » de la page Profs (lien vers leur page studio).
INDEPENDANTS = [
    # Vide tant que ces profs n'ont pas donné leur accord pour apparaître sur la page Profs.
    # Candidates à contacter : "Samtosha Yoga - Patricia Heude", "Yoga by Valérie Maurel (Saône & Soi)",
    # "Karan Anand Nathalie" (noms exacts des studios, à remettre ici une fois l'accord obtenu).
]
