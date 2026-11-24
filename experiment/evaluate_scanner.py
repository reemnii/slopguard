"""Evaluate the scanner against labeled package cases."""

import json
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from scanner.scanner import scan_code


BASE_DIR = Path(__file__).resolve().parent


def main():
    cases = json.loads((BASE_DIR / "evaluation_cases.json").read_text(encoding="utf-8"))
    counts = {"tp": 0, "tn": 0, "fp": 0, "fn": 0}
    rows = []
    unverified = 0

    for case in cases:
        extension = ".js" if case["language"] == "javascript" else ".py"
        results = scan_code(case["code"], extension)
        if any(result["exists"] is None for result in results):
            unverified += 1
            rows.append({"name": case["name"], "expected": case["expected_hallucinated"], "predicted": None})
            continue
        # A package can exist and still be suspicious when its name closely
        # resembles a popular package, so evaluate the scanner's risk output
        # rather than existence alone.
        predicted = any(result.get("risk_score", 0) > 0 for result in results)
        expected = case["expected_hallucinated"]

        if predicted and expected:
            counts["tp"] += 1
        elif not predicted and not expected:
            counts["tn"] += 1
        elif predicted and not expected:
            counts["fp"] += 1
        else:
            counts["fn"] += 1
        rows.append({"name": case["name"], "expected": expected, "predicted": predicted})

    precision = counts["tp"] / (counts["tp"] + counts["fp"]) if counts["tp"] + counts["fp"] else 0
    recall = counts["tp"] / (counts["tp"] + counts["fn"]) if counts["tp"] + counts["fn"] else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0

    print(json.dumps({"counts": counts, "unverified": unverified, "precision": precision, "recall": recall, "f1": f1, "cases": rows}, indent=2))


if __name__ == "__main__":
    main()
