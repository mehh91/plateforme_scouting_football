POSITION_GROUPS = {
    "Défenseurs centraux": [
        "Center Back",
        "Left Center Back",
        "Right Center Back",
    ],
    "Latéraux": [
        "Left Back",
        "Right Back",
    ],
    "Milieux défensifs": [
        "Defensive Midfield",
        "Left Defensive Midfield",
        "Right Defensive Midfield",
        "Center Defensive Midfield",
    ],
    "Milieux centraux": [
        "Center Midfield",
        "Left Center Midfield",
        "Right Center Midfield",
    ],
    "Milieux offensifs": [
        "Attacking Midfield",
        "Center Attacking Midfield",
        "Left Attacking Midfield",
        "Right Attacking Midfield",
    ],
    "Ailiers": [
        "Left Wing",
        "Right Wing",
        "Left Midfield",
        "Right Midfield",
    ],
    "Attaquants": [
        "Center Forward",
        "Left Center Forward",
        "Right Center Forward",
        "Striker",
    ],
    "Gardiens": [
        "Goalkeeper",
    ],
}

POSITION_TO_GROUP = {
    position: group_name
    for group_name, positions in POSITION_GROUPS.items()
    for position in positions
}

# Priorité métier pour choisir une position principale plus crédible
# en cas de multi-postes sur une même saison.
POSITION_PRIORITY = {
    "Left Wing": 100,
    "Right Wing": 100,
    "Center Forward": 95,
    "Left Center Forward": 95,
    "Right Center Forward": 95,
    "Striker": 95,
    "Left Attacking Midfield": 85,
    "Right Attacking Midfield": 85,
    "Center Attacking Midfield": 80,
    "Attacking Midfield": 80,
    "Left Midfield": 70,
    "Right Midfield": 70,
    "Center Midfield": 65,
    "Left Center Midfield": 65,
    "Right Center Midfield": 65,
    "Defensive Midfield": 55,
    "Center Defensive Midfield": 55,
    "Left Defensive Midfield": 55,
    "Right Defensive Midfield": 55,
    "Left Back": 40,
    "Right Back": 40,
    "Center Back": 30,
    "Left Center Back": 30,
    "Right Center Back": 30,
    "Goalkeeper": 10,
}


def assign_position_group(position: str | None) -> str | None:
    if position is None:
        return None
    return POSITION_TO_GROUP.get(position)
