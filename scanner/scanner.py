import sys

from scanner.extract_imports import extract_imports
from scanner.extract_npm import extract_npm_packages
from scanner.registry_check import check_pypi_exists, check_npm_exists
from scanner.heuristics import find_similar_package


def scan_python_code(code: str) -> list[dict]:
    packages = extract_imports(code)
    results = []

    for package in packages:
        if package in sys.stdlib_module_names:
            continue

        registry_result = check_pypi_exists(package)
        similarity_result = find_similar_package(
            package,
            registry="pypi",
        )

        result = {
            "package": package,
            "registry": "PyPI",
            "exists": registry_result["exists"],
            "status": "LOOKS FINE",
        }

        if not registry_result["exists"]:
            result["status"] = "DOES NOT EXIST"

            if similarity_result:
                result["similar_to"] = similarity_result["similar_to"]
                result["similarity"] = similarity_result["similarity"]
                result["status"] = "POSSIBLE SLOPSQUAT"

        elif similarity_result:
            result["similar_to"] = similarity_result["similar_to"]
            result["similarity"] = similarity_result["similarity"]
            result["status"] = "SUSPICIOUS"

        results.append(result)

    return results


def scan_javascript_code(code: str) -> list[dict]:
    packages = extract_npm_packages(code)
    results = []

    for package in packages:
        registry_result = check_npm_exists(package)
        similarity_result = find_similar_package(
            package,
            registry="npm",
        )

        result = {
            "package": package,
            "registry": "npm",
            "exists": registry_result["exists"],
            "status": "LOOKS FINE",
        }

        if not registry_result["exists"]:
            result["status"] = "DOES NOT EXIST"

            if similarity_result:
                result["similar_to"] = similarity_result["similar_to"]
                result["similarity"] = similarity_result["similarity"]
                result["status"] = "POSSIBLE SLOPSQUAT"

        elif similarity_result:
            result["similar_to"] = similarity_result["similar_to"]
            result["similarity"] = similarity_result["similarity"]
            result["status"] = "SUSPICIOUS"

        results.append(result)

    return results


def scan_code(code: str, file_extension: str) -> list[dict]:
    if file_extension == ".py":
        return scan_python_code(code)

    if file_extension in {".js", ".jsx", ".ts", ".tsx"}:
        return scan_javascript_code(code)

    raise ValueError(f"Unsupported file type: {file_extension}")
