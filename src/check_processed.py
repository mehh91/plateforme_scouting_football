import pandas as pd


def main():
    df = pd.read_parquet("data/processed/events_clean.parquet")

    print("Dimensions du fichier parquet :")
    print(df.shape)

    print("\nColonnes de coordonnées présentes :")
    cols = ["x", "y", "end_x", "end_y", "carry_end_x", "carry_end_y", "shot_end_x", "shot_end_y"]
    for col in cols:
        print(f"{col}: {'OK' if col in df.columns else 'ABSENT'}")


if __name__ == "__main__":
    main()