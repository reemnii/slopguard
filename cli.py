import sys

from scanner.scanner import scan_code


def main():
    if len(sys.argv) < 2:
        print("Usage: python cli.py <python_file>")
        return

    file_path = sys.argv[1]

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            code = file.read()
    except FileNotFoundError:
        print(f"Error: file '{file_path}' was not found.")
        return
    except OSError as error:
        print(f"Error reading file: {error}")
        return

    results = scan_code(code)

    print("\nSlopGuard Scan Results")
    print("-" * 40)

    suspicious_count = 0

    for result in results:
        package = result["package"]

        if result["status"] == "LOOKS FINE":
            print(f"✓ {package:<20} LOOKS FINE")

        elif result["status"] == "SUSPICIOUS":
            print(
                f"⚠ {package:<20} SUSPICIOUS "
                f"(similar to {result['similar_to']}, "
                f"{result['similarity']:.1f}% match)"
            )
            suspicious_count += 1

        elif result["status"] == "DOES NOT EXIST":
            print(f"✗ {package:<20} DOES NOT EXIST")
            suspicious_count += 1

    print("-" * 40)

    if suspicious_count == 0:
        print("No potentially hallucinated packages detected.")
    else:
        print(
            f"{suspicious_count} potentially hallucinated package(s) detected."
        )


if __name__ == "__main__":
    main()
