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


if __name__ == "__main__":
    print(find_similar_package("requestss"))
    print(find_similar_package("reactt", registry="npm"))
    print(find_similar_package("completely-random-package"))
