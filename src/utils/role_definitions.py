ROLE_DEFINITIONS = {
    "progressive_midfielder": {
        "label": "Milieu progressif",
        "description": "Profil capable de faire avancer le ballon par la passe et la conduite tout en restant fiable dans la circulation.",
        "target_groups": ["Milieux centraux", "Milieux défensifs"],
        "weights": {
            "ball_progression": 0.40,
            "chance_creation": 0.25,
            "ball_security": 0.20,
            "defensive_activity": 0.15,
        },
    },
    "deep_lying_playmaker": {
        "label": "Regista",
        "description": "Organisateur bas qui dicte le rythme, sécurise la possession et alimente les zones avancées.",
        "target_groups": ["Milieux défensifs", "Milieux centraux"],
        "weights": {
            "ball_security": 0.35,
            "ball_progression": 0.35,
            "defensive_activity": 0.20,
            "chance_creation": 0.10,
        },
    },
    "ball_winning_midfielder": {
        "label": "Milieu récupérateur",
        "description": "Milieu d'impact axé sur la récupération, les duels et la couverture sans casser la circulation.",
        "target_groups": ["Milieux défensifs", "Milieux centraux"],
        "weights": {
            "defensive_activity": 0.45,
            "ball_security": 0.25,
            "ball_progression": 0.20,
            "chance_creation": 0.10,
        },
    },
    "advanced_playmaker": {
        "label": "Meneur avancé",
        "description": "Créateur entre les lignes avec capacité à alimenter le dernier tiers et à connecter les attaques.",
        "target_groups": ["Milieux offensifs", "Milieux centraux"],
        "weights": {
            "chance_creation": 0.40,
            "ball_progression": 0.25,
            "final_third_impact": 0.20,
            "ball_security": 0.15,
        },
    },
    "creative_winger": {
        "label": "Ailier créatif",
        "description": "Joueur de couloir qui crée des occasions et apporte de la valeur dans le dernier tiers.",
        "target_groups": ["Ailiers", "Milieux offensifs"],
        "weights": {
            "chance_creation": 0.40,
            "final_third_impact": 0.35,
            "ball_progression": 0.15,
            "ball_security": 0.10,
        },
    },
    "inside_forward": {
        "label": "Ailier intérieur",
        "description": "Profil offensif qui attaque la surface, menace le but et garde une capacité de création.",
        "target_groups": ["Ailiers", "Attaquants"],
        "weights": {
            "final_third_impact": 0.45,
            "chance_creation": 0.20,
            "ball_progression": 0.20,
            "ball_security": 0.15,
        },
    },
    "ball_playing_center_back": {
        "label": "Défenseur central relanceur",
        "description": "Central capable de casser des lignes à la relance tout en gardant un niveau défensif solide.",
        "target_groups": ["Défenseurs centraux"],
        "weights": {
            "ball_security": 0.35,
            "ball_progression": 0.30,
            "defensive_activity": 0.35,
        },
    },
    "defensive_center_back": {
        "label": "Défenseur central stoppeur",
        "description": "Profil prioritairement défensif, fort dans la protection de sa zone et les interventions.",
        "target_groups": ["Défenseurs centraux"],
        "weights": {
            "defensive_activity": 0.50,
            "ball_security": 0.30,
            "ball_progression": 0.20,
        },
    },
    "progressive_fullback": {
        "label": "Latéral progressif",
        "description": "Latéral capable de porter le ballon, d'alimenter le dernier tiers et de contribuer offensivement.",
        "target_groups": ["Latéraux"],
        "weights": {
            "ball_progression": 0.40,
            "final_third_impact": 0.25,
            "chance_creation": 0.20,
            "defensive_activity": 0.15,
        },
    },
    "penalty_box_forward": {
        "label": "Avant-centre de surface",
        "description": "Finisseur qui vit dans la surface et maximise l'impact direct dans le dernier tiers.",
        "target_groups": ["Attaquants"],
        "weights": {
            "final_third_impact": 0.55,
            "chance_creation": 0.15,
            "ball_progression": 0.20,
            "ball_security": 0.10,
        },
    },
}


ROLE_LABELS = {
    f"{role_name}_score": role_definition["label"]
    for role_name, role_definition in ROLE_DEFINITIONS.items()
}


ROLE_DESCRIPTIONS = {
    f"{role_name}_score": role_definition["description"]
    for role_name, role_definition in ROLE_DEFINITIONS.items()
}


ROLE_TARGET_GROUPS = {
    f"{role_name}_score": role_definition["target_groups"]
    for role_name, role_definition in ROLE_DEFINITIONS.items()
}
