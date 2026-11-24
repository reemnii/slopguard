import sys
from pathlib import Path

from scanner.scanner import scan_code


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if len(sys.argv) < 2:
        print("Usage: python cli.py <file>")
        return

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(f"Error: file '{file_path}' was not found.")
        return

    extension = file_path.suffix.lower()

    supported_extensions = {".py", ".js", ".jsx", ".ts", ".tsx"}

    if extension not in supported_extensions:
        print(f"Unsupported file type: {extension}")
        return

    try:
        code = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        print(f"Error reading file: {error}")
        return

    try:
        results = scan_code(code, extension)
    except ValueError as error:
        print(error)
        return

    print("\nSlopGuard Scan Results")
    print("-" * 60)

    suspicious_count = 0
    unknown_count = 0

    for result in results:
        package = result["package"]
        registry = result["registry"]

        score = result['risk_score']
        score_text = f"{score:>3}/100" if score is not None else "unverified"
        print(
            f"{package:<25} "
            f"{registry:<6} "
            f"Risk: {score_text} "
            f"[{result['risk_level']}]"
        )

        for reason in result.get("risk_reasons", []):
            print(f"   - {reason}")

        if result["risk_level"] in {"HIGH", "MEDIUM"}:
            suspicious_count += 1
        if result["risk_level"] == "UNKNOWN":
            unknown_count += 1

    print("-" * 60)
    if unknown_count:
        print(f"{unknown_count} package(s) could not be verified; retry when registry access is available.")

    if suspicious_count == 0:
        print("No high- or medium-risk packages detected.")
    else:
        print(
            f"{suspicious_count} high- or medium-risk package(s) detected."
        )


if __name__ == "__main__":
    main()
