from scanner.extract_imports import extract_imports
from scanner.extract_npm import extract_npm_packages
from scanner.registry_check import check_pypi_exists, check_npm_exists
from scanner.heuristics import (
    find_similar_package,
    analyze_package_metadata,
    calculate_risk_score,
)
from scanner.package_names import is_node_builtin, is_python_stdlib, normalize_pypi_name

def scan_python_code(code: str) -> list[dict]:
    packages = extract_imports(code)
    results = []

    for package in packages:
        if is_python_stdlib(package):
            continue

        registry_package = normalize_pypi_name(package)
        registry_result = check_pypi_exists(registry_package)
        metadata_reasons = []

        if registry_result["exists"]:
            metadata_reasons = analyze_package_metadata(
                registry_result
            )

        similarity_result = find_similar_package(
            package,
            registry="pypi",
        )

        result = {
            "package": package,
            "registry_package": registry_package,
            "registry": "PyPI",
            "exists": registry_result["exists"],
            "status": "LOOKS FINE",
        }

        risk = calculate_risk_score(
            exists=registry_result["exists"],
            similarity_result=similarity_result,
            metadata_reasons=metadata_reasons,
        )

        result["risk_score"] = risk["risk_score"]
        result["risk_level"] = risk["risk_level"]
        result["risk_reasons"] = risk["risk_reasons"]

        if risk["risk_level"] == "HIGH":
            result["status"] = "HIGH RISK"
        elif risk["risk_level"] == "MEDIUM":
            result["status"] = "SUSPICIOUS"
        elif risk["risk_level"] == "LOW":
            result["status"] = "LOW RISK"
        else:
            result["status"] = "LOOKS FINE"

        if similarity_result:
            result["similar_to"] = similarity_result["similar_to"]
            result["similarity"] = similarity_result["similarity"]

        results.append(result)

    return results


def scan_javascript_code(code: str) -> list[dict]:
    packages = extract_npm_packages(code)
    results = []

    for package in packages:
        if is_node_builtin(package):
            continue

        registry_result = check_npm_exists(package)
        similarity_result = find_similar_package(
            package,
            registry="npm",
        )
        metadata_reasons = []

        result = {
            "package": package,
            "registry": "npm",
            "exists": registry_result["exists"],
        }

        risk = calculate_risk_score(
            exists=registry_result["exists"],
            similarity_result=similarity_result,
            metadata_reasons=metadata_reasons,
        )

        result["risk_score"] = risk["risk_score"]
        result["risk_level"] = risk["risk_level"]
        result["risk_reasons"] = risk["risk_reasons"]

        if risk["risk_level"] == "HIGH":
            result["status"] = "HIGH RISK"
        elif risk["risk_level"] == "MEDIUM":
            result["status"] = "SUSPICIOUS"
        elif risk["risk_level"] == "LOW":
            result["status"] = "LOW RISK"
        else:
            result["status"] = "LOOKS FINE"

        if similarity_result:
            result["similar_to"] = similarity_result["similar_to"]
            result["similarity"] = similarity_result["similarity"]

        results.append(result)

    return results


def scan_code(code: str, file_extension: str) -> list[dict]:
    if file_extension == ".py":
        return scan_python_code(code)

    if file_extension in {".js", ".jsx", ".ts", ".tsx"}:
        return scan_javascript_code(code)

    raise ValueError(f"Unsupported file type: {file_extension}")
