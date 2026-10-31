# -*- coding: utf-8 -*-
"""Tarifs et offres d'essai des studios, relevés sur leurs sites (tarif plein, cours collectifs de yoga).

Sert aux articles « Prix d'un cours de yoga à Lyon » et « Cours d'essai à Lyon », et à la ligne Tarifs
des pages studio. À mettre à jour quand un studio change ses prix (et changer RELEVE).

Champs (tous facultatifs) :
  unite      prix d'un cours à l'unité (€)
  carte      (nombre de cours, prix €) : la carte la plus proche de 10 cours
  annuel     prix d'un abonnement à l'année, 1 cours par semaine (€)
  seances    nombre de séances couvertes par cet abonnement annuel, si le studio l'indique
  trimestre  (nombre de séances, prix €) quand le studio ne vend qu'au trimestre
  essai      "gratuit", ou un prix en € pour le cours d'essai payant
  essai_note précision sur le cours d'essai
  decouverte (texte de l'offre, prix €, nombre de cours) ; prix None si non affiché
  reduit     ce que le studio propose pour payer moins (tarif réduit, solidaire…)
  source     page où les prix ont été relevés
  note       mise en garde
"""

RELEVE = "2026-10-31"

TARIFS = {
    "Vima Yoga": {
        "unite": 25, "carte": (10, 210), "annuel": 420, "seances": 40,
        "essai": 10, "essai_note": "déduit de l'abonnement",
        "reduit": "tarif réduit sur les abonnements",
        "source": "https://www.vima-yoga.com/les-tarifs/",
    },
    "Yoga Dojo Lyon Massena": {
        "carte": (10, 170), "annuel": 410, "seances": 40,
        "decouverte": ("8 jours d'essai dans les disciplines de votre choix", None, None),
        "reduit": "cotisations solidaires selon les revenus (de 290 € à 370 € l'année), étudiants",
        "source": "https://yoga.dojolyon.fr/inscriptions-yoga-2026-2027/",
        "note": "carte de 10 cours adhésion comprise",
    },
    "Cocon Yoga - Le Cocon": {
        "carte": (5, 85),
        "decouverte": ("Pass découverte", None, None),
        "reduit": "chèques-vacances acceptés sur les cartes, parrainage",
        "source": "https://coconyoga.com/tarifs",
    },
    "Cocon Yoga - Oblique": {
        "carte": (5, 85),
        "decouverte": ("Pass découverte", None, None),
        "reduit": "chèques-vacances acceptés sur les cartes, parrainage",
        "source": "https://coconyoga.com/tarifs",
    },
    "Sesam Yoga Lyon 7": {
        "unite": 22, "carte": (12, 220), "annuel": 550,
        "decouverte": ("Offre découverte, valable 30 jours", 44, 4),
        "reduit": "tarifs réduit et solidaire, cours solidaires à 5 € le lundi et le jeudi",
        "source": "https://www.centresesam.fr/tarifs-sesam/",
    },
    "Sesam Yoga Lyon 6": {
        "unite": 22, "carte": (12, 220), "annuel": 550,
        "decouverte": ("Offre découverte, valable 30 jours", 44, 4),
        "reduit": "tarifs réduit et solidaire, cours solidaires à 5 €",
        "source": "https://www.centresesam.fr/tarifs-sesam/",
    },
    "École de Yoga Horizon": {
        "unite": 19.5, "carte": (10, 180), "annuel": 480, "seances": 34,
        "essai": "gratuit", "essai_note": "sur un cours de niveau 1, sans réservation",
        "decouverte": ("Offre découverte, valable 3 semaines", 36, 3),
        "source": "https://www.yoga-horizon.fr/activites/tarifs/",
    },
    "Centre Tao Yoga": {
        "essai_note": "cours d'essai ou découverte possible, à demander aux enseignants",
        "source": "http://centretaoyoga.fr/",
    },
    "Centre de Yoga Iyengar Croix-Rousse": {
        "annuel": 630, "seances": 37, "trimestre": (14, 260),
        "essai": 15, "essai_note": "offert du 1er au 30 septembre",
        "source": "https://www.yogaiyengar-lyon.com/tarifs.html",
        "note": "tarifs niveau 1 (cours de 1h15)",
    },
    "Yoga Room - Les Halles": {
        "carte": (22, 298),
        "decouverte": ("Pass découverte, 30 jours de cours illimités", 68, None),
        "source": "https://www.yoga-room.fr/",
    },
    "The Good Flow": {
        "decouverte": ("Pass découverte, 15 jours de cours illimités", None, None),
        "source": "https://thegoodflow-yoga.com/tarifs/",
    },
    "Samtosha Yoga - Patricia Heude": {
        "trimestre": (None, 230), "annuel": 645,
        "essai": 15, "essai_note": "remboursé en cas d'inscription au trimestre",
        "reduit": "-5 à -10 % pour les étudiants",
        "source": "http://www.samtosha-yoga.fr/cours/tarifs/",
    },
    "Yeahga (Espace holistique)": {
        "unite": 20, "carte": (10, 170),
        "decouverte": ("Offre 3 cours", 30, 3),
        "source": "https://www.yeahga.fr/tarifs",
    },
    "Pandi Panda Yoga": {
        "unite": 16, "carte": (10, 145), "annuel": 375, "seances": 30,
        "essai_note": "pas de cours d'essai gratuit",
        "decouverte": ("Carnet découverte", 36, 3),
        "reduit": "13 € le cours en plein air l'été (parc de la Tête d'Or, parc Blandan)",
        "source": "https://pandipandayoga.com/nos-tarifs-de-cours-yoga-a-villeurbanne/",
    },
    "Les Ailes Hatha Yoga": {
        "essai": "gratuit", "essai_note": "premier cours, sur réservation",
        "source": "https://les-ailes.fr/",
    },
    "Yoga Bellecour": {
        "trimestre": (11, 140),
        "essai": "gratuit", "essai_note": "sur réservation, selon les places",
        "source": "https://yoga-bellecour.com/horaires-tarifs/",
    },
    "Latitude Yoga": {
        "essai": "gratuit",
        "source": "https://www.latitudeyoga.com/tarifs/",
    },
    "L'Atelier du Yoga": {
        "trimestre": (11, 198),
        "decouverte": ("Pass découverte", None, None),
        "source": "https://atelier-du-yoga.fr/tarifs/detail-des-tarifs",
        "note": "adhésion annuelle en plus",
    },
    "Studio Arbol Flow": {
        "unite": 17, "carte": (10, 150), "annuel": 370,
        "essai": "gratuit",
        "source": "https://arbolflow.com/tarifs-studio/",
    },
    "Multifa": {
        "essai": "gratuit", "essai_note": "à réserver en ligne",
        "decouverte": ("Pass découverte", 33, 3),
        "reduit": "chèques-vacances Connect acceptés",
        "source": "https://multifa.fr/",
    },
    "O Yoga Studio": {
        "unite": 22, "carte": (10, 165),
        "essai": 15, "essai_note": "lors de la première visite",
        "decouverte": ("Pass découverte, valable 1 mois", 35, 3),
        "reduit": "-10 % pour les moins de 18 ans, étudiants et demandeurs d'emploi",
        "source": "https://www.oyogastudio.com/tarifs",
    },
    "École de Yoga de Mysore (Ashtanga)": {
        "unite": 22, "carte": (10, 190), "annuel": 570,
        "essai": "gratuit", "essai_note": "à réserver en ligne",
        "decouverte": ("Cycle d'accueil, 4 cours sur 5 semaines", 58, 4),
        "reduit": "tarif réduit sur toutes les formules",
        "source": "https://www.yoga-ashtanga.com/tarifs",
        "note": "tarifs affichés pour la saison 2025-2026",
    },
}
