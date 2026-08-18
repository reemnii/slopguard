from rapidfuzz import fuzz


POPULAR_PACKAGES = [
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


def find_similar_package(package_name: str, threshold: int = 80):
    best_match = None
    best_score = 0

    for popular_package in POPULAR_PACKAGES:
        score = fuzz.ratio(package_name.lower(), popular_package.lower())

        if score > best_score:
            best_score = score
            best_match = popular_package

    if best_score >= threshold and package_name.lower() != best_match.lower():
        return {
            "similar_to": best_match,
            "similarity": best_score,
        }

    return None



if __name__ == "__main__":
    print(find_similar_package("requestss"))
    print(find_similar_package("numpyy"))
    print(find_similar_package("completely-random-package"))