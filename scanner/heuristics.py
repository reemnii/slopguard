from datetime import datetime, timezone

from rapidfuzz import fuzz


POPULAR_PYPI_PACKAGES = [
    "requests",
    "numpy",
    "pandas",
    "matplotlib",
    "scikit-learn",
    "tensorflow",
    "torch",
    "flask",
    "django",
    "beautifulsoup4",
]


POPULAR_NPM_PACKAGES = [
    "react",
    "react-dom",
    "express",
    "axios",
    "lodash",
    "next",
    "vue",
    "typescript",
    "webpack",
    "eslint",
]


def find_similar_package(
    package_name: str,
    registry: str = "pypi",
    threshold: int = 80,
):
    if registry == "npm":
        popular_packages = POPULAR_NPM_PACKAGES
    else:
        popular_packages = POPULAR_PYPI_PACKAGES

    best_match = None
    best_score = 0

    for popular_package in popular_packages:
        score = fuzz.ratio(
            package_name.lower(),
            popular_package.lower(),
        )

        if score > best_score:
            best_score = score
            best_match = popular_package

    if (
        best_match
        and best_score >= threshold
        and package_name.lower() != best_match.lower()
    ):
        return {
            "similar_to": best_match,
            "similarity": best_score,
        }

    return None


def analyze_package_metadata(registry_result: dict) -> list[str]:
    reasons = []

    repository_url = registry_result.get("repository_url")

    if not repository_url:
        reasons.append("No repository URL")

    first_upload = registry_result.get("first_upload")

    if first_upload:
        try:
            created = datetime.fromisoformat(
                first_upload.replace("Z", "+00:00")
            )

            now = datetime.now(timezone.utc)
            age_days = (now - created).days

            if age_days < 30:
                reasons.append(
                    f"Very new package ({age_days} days old)"
                )

        except ValueError:
            pass

    return reasons

def calculate_risk_score(
    exists: bool,
    similarity_result: dict | None = None,
    metadata_reasons: list[str] | None = None,
) -> dict:
    score = 0
    reasons = []

    if not exists:
        score += 60
        reasons.append("Package does not exist in registry")

    if similarity_result:
        score += 30
        reasons.append(
            f"Name similar to {similarity_result['similar_to']} "
            f"({similarity_result['similarity']:.1f}% match)"
        )

    metadata_reasons = metadata_reasons or []

    for reason in metadata_reasons:
        if reason.startswith("Very new package"):
            score += 20
        elif reason == "No repository URL":
            score += 10

        reasons.append(reason)

    score = min(score, 100)

    if score >= 70:
        level = "HIGH"
    elif score >= 40:
        level = "MEDIUM"
    elif score >= 20:
        level = "LOW"
    else:
        level = "MINIMAL"

    return {
        "risk_score": score,
        "risk_level": level,
        "risk_reasons": reasons,
    }


if __name__ == "__main__":
    print(find_similar_package("requestss"))
    print(find_similar_package("reactt", registry="npm"))
    print(find_similar_package("completely-random-package"))
