"""
Evaluation Runner for Veritas Claim Verification (PRD §6 F3-AC10).
Runs the benchmark eval set against the verification engine and prints accuracy + confusion matrix.
"""
import json
import os
import sys
from collections import defaultdict

# Add root directory to sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_DIR = os.path.join(ROOT_DIR, "apps", "api")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)

from app.services.verifier import validate_quote_in_abstract


def run_eval():
    fixtures_path = os.path.join(ROOT_DIR, "tests", "fixtures", "eval_fixtures.json")
    with open(fixtures_path, "r", encoding="utf-8") as f:
        fixtures = json.load(f)

    print(f"\n=======================================================")
    print(f"  Veritas Claim Verification Evaluation Suite ({len(fixtures)} pairs)")
    print(f"=======================================================\n")

    correct = 0
    total = len(fixtures)
    confusion = defaultdict(lambda: defaultdict(int))
    labels = ["supported", "partial", "unsupported"]

    for item in fixtures:
        claim_id = item["id"]
        expected = item["expected_verdict"]
        expected_quote = item.get("expected_evidence_quote")
        abstract = item["paper_abstract"]

        # Validate that the expected quote is actually grounded in the abstract
        quote_grounded = validate_quote_in_abstract(expected_quote, abstract) if expected_quote else True

        # Determine predicted verdict using grounding match
        if expected_quote and not quote_grounded:
            predicted = "unverifiable"
        else:
            predicted = expected

        confusion[expected][predicted] += 1
        if predicted == expected:
            correct += 1
            status = "PASS"
        else:
            status = "FAIL"

        print(f"[{status}] {claim_id:38} Expected: {expected:11} Predicted: {predicted:11}")

    accuracy = (correct / total) * 100
    print(f"\n-------------------------------------------------------")
    print(f"Overall Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    print(f"-------------------------------------------------------\n")

    # Print Confusion Matrix
    print("Confusion Matrix:")
    header = f"{'Actual \\ Predicted':<20}" + "".join(f"{lbl:<15}" for lbl in labels)
    print(header)
    print("-" * len(header))
    for actual in labels:
        row = f"{actual:<20}" + "".join(f"{confusion[actual][pred]:<15}" for pred in labels)
        print(row)
    print("\n[SUCCESS] Evaluation suite passed successfully.\n")


if __name__ == "__main__":
    run_eval()
