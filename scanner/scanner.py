import sys

from scanner.extract_imports import extract_imports
from scanner.registry_check import check_pypi_exists
from scanner.heuristics import find_similar_package


def scan_code(code: str) -> list[dict]:
    packages = extract_imports(code)
    results = []

    for package in packages:
        if package in sys.stdlib_module_names:
            continue

        registry_result = check_pypi_exists(package)
        similarity_result = find_similar_package(package)

        result = {
            "package": package,
            "exists": registry_result["exists"],
            "status": "LOOKS FINE",
        }

        if not registry_result["exists"]:
            result["status"] = "DOES NOT EXIST"

        if similarity_result:
            result["similar_to"] = similarity_result["similar_to"]
            result["similarity"] = similarity_result["similarity"]

            if registry_result["exists"]:
                result["status"] = "SUSPICIOUS"

        results.append(result)

    return results