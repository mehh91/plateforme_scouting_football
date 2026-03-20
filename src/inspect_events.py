from src.local_data import load_local_events


def inspect_events():
    events = load_local_events()

    print("Dimensions du DataFrame events :")
    print(events.shape)

    print("\nColonnes principales recherchées :")
    columns_to_check = [
        "id",
        "index",
        "period",
        "timestamp",
        "minute",
        "second",
        "type",
        "team",
        "player",
        "player_id",
        "location",
        "pass_end_location",
        "carry_end_location",
        "shot_end_location",
        "pass_outcome",
        "shot_outcome",
        "shot_statsbomb_xg",
        "pass_recipient",
        "possession",
        "possession_team",
        "play_pattern"
    ]

    for col in columns_to_check:
        print(f"{col}: {'OK' if col in events.columns else 'ABSENT'}")

    print("\nAperçu des colonnes clés :")
    existing_cols = [col for col in columns_to_check if col in events.columns]
    print(events[existing_cols].head(10))

    print("\nTypes d'actions présents dans le match :")
    if "type" in events.columns:
        print(events["type"].value_counts().head(20))

    print("\nÉquipes présentes :")
    if "team" in events.columns:
        print(events["team"].dropna().unique())

    print("\nExemple de joueurs présents :")
    if "player" in events.columns:
        print(events["player"].dropna().unique()[:15])


if __name__ == "__main__":
    inspect_events()