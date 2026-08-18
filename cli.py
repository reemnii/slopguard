import sys
from pathlib import Path

from scanner.scanner import scan_code


def main():
    if len(sys.argv) < 2:
        print("Usage: python cli.py <file>")
        return

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(f"Error: file '{file_path}' was not found.")
        return

    extension = file_path.suffix.lower()

    supported_extensions = {
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
    }

    if extension not in supported_extensions:
        print(f"Unsupported file type: {extension}")
        return

    try:
        code = file_path.read_text(encoding="utf-8")
    except OSError as error:
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

    for result in results:
        package = result["package"]
        registry = result["registry"]

        if result["status"] == "LOOKS FINE":
            print(f"✓ {package:<25} {registry:<6} LOOKS FINE")

        elif result["status"] == "SUSPICIOUS":
            print(
                f"⚠ {package:<25} {registry:<6} SUSPICIOUS "
                f"(similar to {result['similar_to']}, "
                f"{result['similarity']:.1f}% match)"
            )
            suspicious_count += 1

        elif result["status"] == "POSSIBLE SLOPSQUAT":
            print(
                f"🚨 {package:<25} {registry:<6} POSSIBLE SLOPSQUAT "
                f"(similar to {result['similar_to']}, "
                f"{result['similarity']:.1f}% match)"
            )
            suspicious_count += 1

        elif result["status"] == "DOES NOT EXIST":
            print(
                f"✗ {package:<25} {registry:<6} DOES NOT EXIST"
            )
            suspicious_count += 1

    print("-" * 60)

    if suspicious_count == 0:
        print("No potentially suspicious packages detected.")
    else:
        print(
            f"{suspicious_count} potentially suspicious package(s) detected."
        )


if __name__ == "__main__":
    main()
