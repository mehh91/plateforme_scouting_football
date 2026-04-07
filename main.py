import argparse

from src.features.football_dimensions import run_pipeline as run_dimensions_pipeline
from src.features.player_match_features import run_pipeline as run_player_match_pipeline
from src.features.player_season_enriched import run_pipeline as run_enrichment_pipeline
from src.features.player_season_features import run_pipeline as run_player_season_pipeline
from src.features.position_group_percentiles import run_pipeline as run_group_percentiles_pipeline
from src.features.role_scoring import run_pipeline as run_role_scoring_pipeline
from src.modeling.player_similarity import run_pipeline as run_similarity_pipeline


PIPELINE_STEPS = [
    ("player_match", run_player_match_pipeline),
    ("player_season", run_player_season_pipeline),
    ("season_enriched", run_enrichment_pipeline),
    ("football_dimensions", run_dimensions_pipeline),
    ("role_scores", run_role_scoring_pipeline),
    ("group_percentiles", run_group_percentiles_pipeline),
    ("player_similarity", run_similarity_pipeline),
]


def run_pipeline(stage: str) -> None:
    run_selected = stage == "all"

    for step_name, step_fn in PIPELINE_STEPS:
        if step_name == stage:
            run_selected = True

        if run_selected:
            print(f"\n=== Running step: {step_name} ===")
            step_fn()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="European Football Data & Scouting Platform"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    pipeline_parser = subparsers.add_parser("pipeline", help="Run data pipelines")
    pipeline_parser.add_argument(
        "--stage",
        choices=["all"] + [step_name for step_name, _ in PIPELINE_STEPS],
        default="all",
        help="Run the full pipeline or start from a specific stage",
    )

    app_parser = subparsers.add_parser("app", help="Run the Dash application")
    app_parser.add_argument("--host", default="127.0.0.1")
    app_parser.add_argument("--port", type=int, default=8050)
    app_parser.add_argument("--debug", action="store_true")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "pipeline":
        run_pipeline(args.stage)
        return

    if args.command == "app":
        from app.main import app

        app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
