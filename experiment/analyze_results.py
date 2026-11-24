import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
RESULTS_FILE = BASE_DIR / "results.csv"
RESPONSES_FILE = BASE_DIR / "responses.json"


def analyze():
    with open(RESPONSES_FILE, "r", encoding="utf-8") as file:
        responses = json.load(file)

    if not responses:
        print("No responses found.")
        return

    response_columns = ["prompt_id", "category", "difficulty", "language", "model"]
    response_df = pd.DataFrame(responses)[response_columns].drop_duplicates()

    if RESULTS_FILE.exists() and RESULTS_FILE.stat().st_size > 0:
        df = pd.read_csv(RESULTS_FILE)
    else:
        df = pd.DataFrame()

    if not df.empty:
        if df["hallucinated"].isna().any():
            raise ValueError("Some registry checks were unverified. Rerun those checks before calculating hallucination rates.")
        df["hallucinated"] = (
            df["hallucinated"].astype(str).str.lower().map({"true": True, "false": False})
        ).fillna(False)

        result_generations = (
            df.groupby(["model", "prompt_id"])
            .agg(
                has_hallucination=("hallucinated", "max"),
                package_count=("package", "count"),
            )
            .reset_index()
        )
    else:
        result_generations = pd.DataFrame(
            columns=["model", "prompt_id", "has_hallucination", "package_count"]
        )

    # Use responses.json as the denominator so zero-package generations remain
    # part of the experiment.
    generations = response_df.merge(
        result_generations,
        on=["model", "prompt_id"],
        how="left",
    )
    generations["has_hallucination"] = generations["has_hallucination"].fillna(False).astype(bool)
    generations["package_count"] = generations["package_count"].fillna(0).astype(int)

    total_packages = len(df)
    hallucinated_packages = int(df["hallucinated"].sum()) if not df.empty else 0
    generations_with_hallucination = int(generations["has_hallucination"].sum())
    total_generations = len(generations)

    print("\nSlopGuard Experiment Analysis")
    print("=" * 60)
    print(f"Total generations: {total_generations}")
    print(f"Total packages detected: {total_packages}")
    print(f"Hallucinated packages: {hallucinated_packages}")
    print(
        f"Package hallucination rate: "
        f"{hallucinated_packages / total_packages * 100 if total_packages else 0:.2f}%"
    )
    print(f"Generations with >= 1 hallucinated package: {generations_with_hallucination}")
    print(
        f"Generation hallucination rate: "
        f"{generations_with_hallucination / total_generations * 100 if total_generations else 0:.2f}%"
    )

    print("\nBy model")
    print("-" * 60)
    model_analysis = (
        generations.groupby("model")
        .agg(
            generations=("prompt_id", "count"),
            hallucinated_generations=("has_hallucination", "sum"),
        )
        .reset_index()
    )
    model_analysis["hallucination_rate"] = (
        model_analysis["hallucinated_generations"] / model_analysis["generations"] * 100
    )
    print(model_analysis.to_string(index=False))

    print("\nBy category")
    print("-" * 60)
    category_analysis = (
        generations.groupby("category")
        .agg(
            generations=("prompt_id", "count"),
            hallucinated_generations=("has_hallucination", "sum"),
        )
        .reset_index()
    )
    category_analysis["hallucination_rate"] = (
        category_analysis["hallucinated_generations"] / category_analysis["generations"] * 100
    )
    print(category_analysis.to_string(index=False))

    print("\nBy difficulty")
    print("-" * 60)
    difficulty_analysis = (
        generations.groupby("difficulty")
        .agg(
            generations=("prompt_id", "count"),
            hallucinated_generations=("has_hallucination", "sum"),
        )
        .reset_index()
    )
    difficulty_analysis["hallucination_rate"] = (
        difficulty_analysis["hallucinated_generations"]
        / difficulty_analysis["generations"]
        * 100
    )
    print(difficulty_analysis.to_string(index=False))

    if not df.empty:
        print("\nRisk levels")
        print("-" * 60)
        print(df["risk_level"].value_counts().to_string())

        hallucinations = df[df["hallucinated"]]
        if not hallucinations.empty:
            print("\nHallucinated packages")
            print("-" * 60)
            columns = [
                "prompt_id", "model", "category", "difficulty", "package",
                "registry", "risk_score",
            ]
            existing_columns = [column for column in columns if column in hallucinations.columns]
            print(hallucinations[existing_columns].to_string(index=False))


if __name__ == "__main__":
    analyze()
