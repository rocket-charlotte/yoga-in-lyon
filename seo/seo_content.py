# -*- coding: utf-8 -*-
"""Textes éditoriaux de Yoga In Lyon (quartiers + styles).

Modifie librement ces textes : le script seo_build.py les réinjecte à chaque
passage. Le HTML simple (<p>, <strong>, <a>) est autorisé.
"""

# Clé = valeur "arr" des données (ex. "Lyon 4e"), valeur = paragraphes HTML.
QUARTIERS = {
    "Lyon 1er": """
<p>Entre les pentes de la Croix-Rousse et la place des Terreaux, le 1er arrondissement est l'un des quartiers les plus vivants de Lyon pour pratiquer le yoga. Ici, les studios sont souvent nichés dans des immeubles de canuts aux grandes fenêtres et aux plafonds hauts : des salles lumineuses, à taille humaine, où l'on vient avant ou après le travail.</p>
<p>On y trouve une offre variée, du Hatha accessible aux débutants jusqu'au Vinyasa plus dynamique, avec plusieurs cours le midi pour celles et ceux qui travaillent sur la Presqu'île. Le quartier se rejoint facilement en métro (lignes A et C, stations Hôtel de Ville et Croix-Paquet) ou à pied depuis les quais de Saône.</p>
""",
    "Lyon 2e": """
<p>Le 2e arrondissement couvre le cœur de la Presqu'île, de Cordeliers à Ainay en passant par Bellecour. C'est le quartier idéal pour caler une séance de yoga entre deux rendez-vous, le midi ou en sortant du bureau : tout est accessible en métro (lignes A et D, stations Bellecour, Cordeliers et Ampère).</p>
<p>Les studios du secteur misent plutôt sur la tradition : Hatha yoga, petits groupes et professeurs qui suivent leurs élèves sur la durée. Le quartier d'Ainay, plus calme, accueille aussi des écoles spécialisées, dont une dédiée à l'Ashtanga.</p>
""",
    "Lyon 3e": """
<p>Autour des Halles Paul Bocuse, de Part-Dieu et de Garibaldi, le 3e arrondissement attire une population active qui cherche des cours efficaces, à des horaires faciles à caser. Les studios y proposent beaucoup de créneaux le midi et en soirée, avec une offre plus sportive : Vinyasa, Ashtanga, et même du hot yoga.</p>
<p>Pratique si vous travaillez à Part-Dieu ou arrivez en train : la gare, le métro B et les nombreuses lignes de tram mettent le quartier à quelques minutes de partout dans Lyon.</p>
""",
    "Lyon 4e": """
<p>Le plateau de la Croix-Rousse a gardé son esprit de village, et ça se ressent dans ses studios de yoga : des lieux intimistes, des groupes réduits et des professeurs bien ancrés dans le quartier. C'est l'un des secteurs les plus riches de Lyon en écoles de tradition, avec notamment un centre entièrement consacré à la méthode Iyengar.</p>
<p>Vous y trouverez aussi bien du Hatha et du Kundalini que des formats plus récents mêlant Vinyasa, yoga doux et Pilates. Le quartier se rejoint en métro C (station Croix-Rousse) ou par les bus qui montent les pentes.</p>
""",
    "Lyon 5e": """
<p>Entre le Vieux Lyon, Saint-Paul et les quais de Saône, le 5e arrondissement offre un cadre unique pour pratiquer : façades Renaissance, colline de Fourvière en arrière-plan et rives de Saône à deux pas. L'offre de cours y est plus restreinte qu'ailleurs, mais elle est souvent tenue par des professeurs indépendants attentifs au suivi de chacun.</p>
<p>Le quartier se rejoint en métro D (station Vieux Lyon) ou en longeant les quais à pied depuis la Presqu'île.</p>
""",
    "Lyon 6e": """
<p>Entre le parc de la Tête d'Or, les Brotteaux et Foch, le 6e arrondissement concentre une grande partie des studios de yoga lyonnais. C'est le quartier où l'offre est la plus large : Hatha, Vinyasa, Ashtanga, Yin, Kundalini et méditation, du petit matin jusqu'en fin de soirée, et souvent le week-end.</p>
<p>Idéal pour enchaîner une séance avec une balade au parc. Le quartier est desservi par le métro A (stations Foch et Masséna) et le métro B (station Brotteaux).</p>
""",
    "Lyon 7e": """
<p>Jean Macé, Saxe-Gambetta, la Guillotière : le 7e arrondissement est un quartier jeune et étudiant, et ses studios le reflètent. On y trouve des lieux chaleureux qui proposent beaucoup de cours, y compris très tôt le matin pour la pratique Ashtanga en style Mysore, et des formats doux ou solidaires à prix accessibles.</p>
<p>Le quartier est très bien desservi : métro B et D (stations Jean Macé et Saxe-Gambetta), tram T2 et gare de Jean Macé.</p>
""",
    "Lyon 8e": """
<p>Autour de Monplaisir et de Laënnec, le 8e arrondissement est un quartier résidentiel et familial, à l'écart de l'agitation du centre. Les cours y sont souvent plus calmes, avec des groupes à taille humaine et des formats adaptés à tous les niveaux, du yoga doux à l'Ashtanga en style Mysore.</p>
<p>Le quartier se rejoint en métro D (stations Monplaisir-Lumière et Grange Blanche) ou en tram T2.</p>
""",
    "Lyon 9e": """
<p>Vaise et les bords de Saône du 9e arrondissement offrent une alternative tranquille aux quartiers du centre. L'offre de yoga y est plus discrète, mais c'est un bon choix si vous habitez ou travaillez dans le nord-ouest de Lyon et cherchez un cours régulier sans traverser la ville.</p>
<p>Le quartier est desservi par le métro D (station Gare de Vaise) et par de nombreuses lignes de bus.</p>
""",
    "Villeurbanne": """
<p>Juste à l'est de Lyon, Villeurbanne a sa propre vie de quartier autour des Gratte-Ciel, de Charpennes et du campus de la Doua. Les studios y proposent un planning fourni, avec de nombreux cours de Hatha yoga en journée et en soirée, des séances douces et de la méditation.</p>
<p>Le secteur des Gratte-Ciel se rejoint en quelques minutes depuis la Part-Dieu par le métro A (station Gratte-Ciel).</p>
""",
}

# Clé = valeur "type_simple" des données.
# slug = nom du fichier généré (sans .html), titre = H1, intro = HTML.
STYLES = {
    "Hatha Yoga": {
        "slug": "hatha-yoga-lyon",
        "titre": "Cours de Hatha yoga à Lyon",
        "intro": """
<p>Le Hatha yoga est la forme de yoga la plus répandue, et souvent la meilleure porte d'entrée pour débuter. Une séance alterne postures tenues quelques respirations, travail du souffle et relaxation finale. Le rythme est posé, ce qui laisse le temps de comprendre l'alignement de chaque posture.</p>
<p>À Lyon, c'est aussi le style le plus enseigné : vous trouverez des cours de Hatha dans presque tous les arrondissements, à tous les moments de la journée, du cours « en douceur » au niveau avancé.</p>
""",
    },
    "Yoga Vinyasa": {
        "slug": "vinyasa-yoga-lyon",
        "titre": "Cours de Vinyasa yoga à Lyon",
        "intro": """
<p>Le Vinyasa enchaîne les postures de façon fluide, en synchronisant chaque mouvement avec la respiration. Les séances sont plus dynamiques et plus cardio que le Hatha, et changent d'une fois sur l'autre selon le professeur. On parle aussi de « flow ».</p>
<p>C'est l'un des styles les plus demandés à Lyon, avec beaucoup de cours le midi et en soirée, notamment dans le 3e, le 6e et le 7e arrondissement. Certains studios proposent aussi des versions chauffées ou sonores.</p>
""",
    },
    "Yin Yoga": {
        "slug": "yin-yoga-lyon",
        "titre": "Cours de Yin yoga et yoga doux à Lyon",
        "intro": """
<p>Le Yin yoga se pratique au sol, avec des postures tenues longtemps (souvent 3 à 5 minutes) pour relâcher en profondeur les tissus et calmer le système nerveux. Nous regroupons ici aussi les cours de yoga doux et de mobilité : des séances lentes, accessibles à tous, idéales en fin de journée.</p>
<p>À Lyon, beaucoup de studios programment leurs cours de Yin le soir et le dimanche, parfois accompagnés de bols chantants ou d'un voyage sonore.</p>
""",
    },
    "Ashtanga": {
        "slug": "ashtanga-yoga-lyon",
        "titre": "Cours d'Ashtanga yoga à Lyon",
        "intro": """
<p>L'Ashtanga suit une série de postures fixe, toujours dans le même ordre, pratiquée sur un rythme soutenu. On le pratique soit en cours guidé (« led class »), soit en style Mysore, où chacun avance à son rythme sous l'œil du professeur, souvent tôt le matin.</p>
<p>C'est un yoga exigeant mais très structuré, apprécié de ceux qui aiment progresser de façon régulière. Plusieurs studios lyonnais proposent des cours adaptés aux débutants (« premières séries », « Ashtanga adapté »).</p>
""",
    },
    "Yoga Iyengar": {
        "slug": "yoga-iyengar-lyon",
        "titre": "Cours de yoga Iyengar à Lyon",
        "intro": """
<p>La méthode Iyengar met l'accent sur la précision de l'alignement. Les postures sont travaillées en détail, avec des accessoires (briques, sangles, chaises, bolsters) qui permettent à chacun de les adapter à son corps, quel que soit son âge ou sa souplesse.</p>
<p>Les cours sont organisés par niveaux et suivent une progression sur l'année. À Lyon, la Croix-Rousse accueille un centre entièrement dédié à cette méthode, avec des cours pour débutants comme pour les séniors.</p>
""",
    },
    "Yoga Kundalini": {
        "slug": "kundalini-yoga-lyon",
        "titre": "Cours de Kundalini yoga à Lyon",
        "intro": """
<p>Le Kundalini yoga combine mouvements répétés, exercices de respiration, chants (mantras) et méditation. Les séances suivent des séquences précises appelées « kriyas », chacune avec une intention particulière : énergie, concentration, apaisement.</p>
<p>C'est un yoga moins centré sur la posture que sur l'énergie et l'état intérieur. Les cours sont moins nombreux à Lyon que pour d'autres styles : notre planning vous aide à les repérer.</p>
""",
    },
    "Pranayama & Nidra": {
        "slug": "meditation-yoga-nidra-lyon",
        "titre": "Méditation, pranayama et yoga Nidra à Lyon",
        "intro": """
<p>Ces cours se concentrent sur le souffle et l'esprit plutôt que sur les postures. Le pranayama regroupe les techniques de respiration du yoga ; le yoga Nidra est une relaxation guidée profonde, pratiquée allongé, souvent décrite comme un « sommeil conscient ».</p>
<p>Ce sont d'excellents compléments à une pratique posturale, ou une première approche du yoga si vous cherchez avant tout à mieux dormir et à réduire le stress.</p>
""",
    },
    "Renfo & Pilates": {
        "slug": "yoga-pilates-renforcement-lyon",
        "titre": "Yoga, Pilates et renforcement à Lyon",
        "intro": """
<p>De plus en plus de studios lyonnais proposent des cours hybrides qui mêlent yoga, Pilates et renforcement musculaire : travail de la sangle abdominale (« core »), souplesse, mobilité et gainage.</p>
<p>Ces formats conviennent bien aux sportifs et à celles et ceux qui veulent un yoga plus physique, ou compléter une pratique de course ou de musculation.</p>
""",
    },
    "Hot Yoga": {
        "slug": "hot-yoga-lyon",
        "titre": "Cours de Hot yoga à Lyon",
        "intro": """
<p>Le hot yoga se pratique dans une salle chauffée, généralement autour de 35 à 40 °C. La chaleur favorise la souplesse et rend la séance plus intense ; on transpire beaucoup, donc on pense à bien s'hydrater et à apporter une serviette.</p>
<p>Le hot yoga est déconseillé en cas de grossesse ou de problème cardiaque : demandez l'avis de votre médecin en cas de doute. À Lyon, l'offre est concentrée dans quelques studios équipés, avec des séances de 60 ou 90 minutes.</p>
""",
    },
}


# ---------------------------------------------------------------------------
# Pages thématiques (recherches à fort potentiel). Le filtre est défini dans
# seo_build.py (COLLECTION_FILTERS) avec la même clé.
COLLECTIONS = {
    "debutant": {
        "slug": "yoga-debutant-lyon",
        "titre": "Yoga pour débutants à Lyon",
        "court": "Yoga débutant",
        "intro": """
<p>Vous n'avez jamais fait de yoga, ou vous reprenez après une longue pause ? Bonne nouvelle : à Lyon, de nombreux studios proposent des cours pensés pour démarrer en douceur. Nous avons sélectionné ici les cours de niveau 1, les cours « tous niveaux », les bases du yoga et les séances douces.</p>
<p>Pour un premier cours, privilégiez le Hatha ou un cours doux : le rythme est lent et le professeur prend le temps d'expliquer chaque posture. Arrivez 10 minutes en avance pour signaler que vous débutez, et n'hésitez pas à demander si le studio propose un cours d'essai.</p>
""",
    },
    "prenatal": {
        "slug": "yoga-prenatal-lyon",
        "titre": "Yoga prénatal à Lyon",
        "court": "Yoga prénatal",
        "intro": """
<p>Le yoga prénatal adapte la pratique à la grossesse : postures stables, travail du souffle, mobilité du bassin et relaxation. Il aide à soulager les tensions du dos, à mieux dormir et à se préparer à l'accouchement, dans un groupe de futures mamans.</p>
<p>Les cours ci-dessous sont spécifiquement dédiés aux femmes enceintes. Demandez toujours l'accord de votre sage-femme ou de votre médecin avant de commencer, et prévenez le professeur de votre terme.</p>
""",
    },
    "seniors": {
        "slug": "yoga-seniors-lyon",
        "titre": "Yoga séniors et yoga adapté à Lyon",
        "court": "Yoga séniors",
        "intro": """
<p>Le yoga se pratique à tout âge, à condition d'être bien accompagné. Les cours réunis ici sont pensés pour les séniors ou adaptés aux limitations physiques : yoga sur chaise, activité physique adaptée, cours séniors et yoga « adapté ».</p>
<p>Ils travaillent l'équilibre, la mobilité des articulations et la respiration, sans postures risquées. La méthode Iyengar, avec ses accessoires, est particulièrement appréciée pour pratiquer en sécurité.</p>
""",
    },
    "midi": {
        "slug": "yoga-midi-lyon",
        "titre": "Cours de yoga le midi à Lyon",
        "court": "Yoga le midi",
        "intro": """
<p>Une heure de yoga à la pause déjeuner, c'est le meilleur moyen de couper la journée et de revenir au bureau détendu. À Lyon, beaucoup de studios proposent des cours entre 12h et 14h, d'une durée de 45 minutes à 1h15.</p>
<p>Les quartiers d'affaires sont les mieux servis : Part-Dieu, Brotteaux, Presqu'île et Croix-Rousse. Voici tous les cours du midi, jour par jour, pour trouver celui qui tombe près de votre travail.</p>
""",
    },
    "weekend": {
        "slug": "yoga-week-end-lyon",
        "titre": "Cours de yoga le week-end à Lyon",
        "court": "Yoga le week-end",
        "intro": """
<p>Le samedi matin ou le dimanche soir, c'est souvent le seul moment où l'on a vraiment le temps. Plusieurs studios lyonnais ouvrent le week-end, avec des cours plus longs, des formats doux pour bien finir la semaine ou des séances dynamiques pour bien la commencer.</p>
<p>Voici tous les cours du samedi et du dimanche à Lyon et Villeurbanne.</p>
""",
    },
    "croix-rousse": {
        "slug": "yoga-croix-rousse",
        "titre": "Yoga à la Croix-Rousse",
        "court": "Yoga Croix-Rousse",
        "intro": """
<p>Des pentes du 1er arrondissement jusqu'au plateau du 4e, la Croix-Rousse est le quartier de Lyon qui compte le plus de studios de yoga. Anciens ateliers de canuts, salles intimistes, écoles de tradition : on y pratique dans des lieux qui ont du caractère, souvent en petits groupes.</p>
<p>L'offre y est très variée : Hatha, Iyengar, Kundalini, Vinyasa, Yin et méditation. Le quartier se rejoint en métro C (Croix-Paquet, Croix-Rousse, Hénon) ou à pied depuis les Terreaux.</p>
""",
    },
    "part-dieu": {
        "slug": "yoga-part-dieu",
        "titre": "Yoga à Part-Dieu",
        "court": "Yoga Part-Dieu",
        "intro": """
<p>Autour de la gare et du centre d'affaires de Part-Dieu, les studios s'adressent surtout aux actifs : cours le midi, en soirée et tôt le matin, avec une offre plutôt dynamique (Vinyasa, Ashtanga, hot yoga) mais aussi des séances de Yin pour décompresser.</p>
<p>Pratique si vous travaillez dans le quartier ou arrivez en train : tout est à quelques minutes à pied de la gare, des Halles Paul Bocuse ou du métro B.</p>
""",
    },
}

# Textes de la page Studios (cible : « studio yoga Lyon »).
STUDIOS_GUIDE = """
<h2>Comment choisir son studio de yoga à Lyon ?</h2>
<p>Lyon compte des dizaines de lieux où pratiquer le yoga, du grand studio qui propose une trentaine de cours par semaine à la petite salle de quartier tenue par un seul professeur. Pour bien choisir, trois critères comptent plus que les autres.</p>
<p><strong>La proximité.</strong> Le meilleur studio est celui où vous irez vraiment. Choisissez-le près de chez vous ou de votre travail : un cours à 10 minutes à pied, c'est un cours qu'on ne rate pas. Nos pages par quartier vous aident à repérer les studios autour de vous.</p>
<p><strong>Le style.</strong> Hatha pour débuter et travailler en douceur, Vinyasa pour un yoga dynamique, Yin pour récupérer, Iyengar pour la précision, Ashtanga pour une pratique structurée et exigeante. Chaque studio a sa spécialité : regardez les styles enseignés avant de vous inscrire.</p>
<p><strong>Les horaires.</strong> Certains studios concentrent leurs cours le soir, d'autres ouvrent dès 7h ou le dimanche. Notre planning recense tous les créneaux de la semaine, studio par studio, pour trouver celui qui colle à votre emploi du temps.</p>
"""


# ---------------------------------------------------------------------------
# Guides (rubrique éditoriale). « kind » choisit le gabarit dans seo_build.py.
GUIDES = [
    {
        "slug": "guide-yoga-lyon-en-chiffres",
        "kind": "chiffres",
        "titre": "Le yoga à Lyon en chiffres",
        "court": "Le yoga à Lyon en chiffres",
        "publie": "2026-10-21",
        "chapo": "Combien de cours de yoga chaque semaine à Lyon, dans quels quartiers, à quelle heure et dans quels styles ? Nous avons compté, studio par studio.",
    },
    {
        "slug": "guide-choisir-style-yoga",
        "kind": "styles",
        "titre": "Quel style de yoga choisir ? Le guide pour bien débuter à Lyon",
        "court": "Quel style de yoga choisir ?",
        "desc": "Hatha, Vinyasa, Yin, Iyengar, Ashtanga : comment choisir son style de yoga selon ses envies, et où pratiquer chaque style à Lyon.",
        "publie": "2026-10-21",
        "chapo": "Hatha, Vinyasa, Yin, Iyengar, Ashtanga… Les noms se ressemblent, les cours beaucoup moins. Voici comment choisir selon ce que vous cherchez, et où pratiquer chaque style à Lyon.",
    },
]

# Comparatif du guide « Quel style choisir ». Clé = style des données.
STYLE_GUIDE = {
    "Hatha Yoga": ("Posé", "Débutants, tous âges, envie de bases solides",
                   "Postures tenues plusieurs respirations, explications détaillées, relaxation finale."),
    "Yoga Iyengar": ("Lent et précis", "Débutants, dos fragile, séniors, perfectionnistes",
                     "Alignement très détaillé, accessoires pour adapter chaque posture, progression par niveaux."),
    "Yin Yoga": ("Très doux", "Stress, récupération sportive, fin de journée",
                 "Postures au sol tenues 3 à 5 minutes, relâchement profond."),
    "Pranayama & Nidra": ("Immobile", "Sommeil, stress, curiosité pour la méditation",
                          "Respiration, relaxation guidée allongée, méditation."),
    "Yoga Vinyasa": ("Dynamique", "Sportifs, envie de bouger et de transpirer",
                     "Enchaînements fluides calés sur le souffle, séances variées."),
    "Ashtanga": ("Soutenu", "Pratiquants réguliers, goût de la discipline",
                 "Série de postures fixe, toujours dans le même ordre, souvent tôt le matin."),
    "Yoga Kundalini": ("Variable", "Énergie, méditation, approche plus spirituelle",
                       "Mouvements répétés, respiration, mantras, méditation."),
    "Renfo & Pilates": ("Dynamique", "Gainage, renforcement, complément d'un sport",
                        "Yoga mêlé de Pilates et de renforcement musculaire."),
    "Hot Yoga": ("Intense", "Pratiquants en bonne santé qui aiment l'effort",
                 "Salle chauffée vers 35 à 40 °C ; déconseillé en cas de grossesse ou de problème cardiaque."),
}

STYLE_GUIDE_CHOIX = """
<h2>Choisir selon ce que vous cherchez</h2>
<p><strong>Vous débutez.</strong> Commencez par un cours de Hatha ou un cours « tous niveaux » : le rythme laisse le temps de comprendre chaque posture. L'Iyengar est aussi un excellent départ si vous aimez qu'on vous explique tout en détail.</p>
<p><strong>Vous voulez vous détendre et mieux dormir.</strong> Le Yin yoga et le yoga Nidra sont faits pour ça. Un cours en fin de journée ou le dimanche soir donne souvent les meilleurs résultats.</p>
<p><strong>Vous voulez transpirer.</strong> Le Vinyasa, l'Ashtanga et le hot yoga sont les plus physiques. Si vous débutez, cherchez les cours « niveau 1 », « bases » ou « tous niveaux ».</p>
<p><strong>Vous avez mal au dos ou vous reprenez une activité.</strong> Privilégiez les cours d'Iyengar, de yoga doux ou de yoga adapté, prévenez le professeur, et demandez l'avis de votre médecin si vous avez un doute.</p>
<p><strong>Vous êtes enceinte.</strong> Optez pour un cours de yoga prénatal plutôt qu'un cours classique, avec l'accord de votre sage-femme ou de votre médecin.</p>
<p>Dans tous les cas, le bon cours est surtout celui qui tombe au bon endroit et au bon moment : un cours à côté de chez vous, c'est un cours que vous ne raterez pas.</p>
"""
