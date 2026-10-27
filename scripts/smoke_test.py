"""
Veritas Post-Deployment Smoke Test Script (PRD §6 F6-AC3).
Verifies live health, examples, review lifecycle, BibTeX, Markdown, and graph endpoints.
"""
import os
import sys
import time
import httpx

API_BASE = os.getenv("API_URL", "http://localhost:8000/api")


def run_smoke_tests():
    print(f"\n=======================================================")
    print(f"  Veritas Post-Deployment Smoke Testing Suite")
    print(f"  Target: {API_BASE}")
    print(f"=======================================================\n")

    endpoints = [
        ("GET", f"{API_BASE}/health", 200),
        ("GET", f"{API_BASE}/examples", 200),
        ("GET", f"{API_BASE}/papers/search?query=transformer+attention&limit=3", 200),
    ]

    all_passed = True

    with httpx.Client(timeout=10.0) as client:
        # Check static endpoints
        for method, url, expected_status in endpoints:
            try:
                resp = client.request(method, url)
                if resp.status_code == expected_status:
                    print(f"[PASS] {method:4} {url} -> {resp.status_code}")
                else:
                    print(f"[FAIL] {method:4} {url} -> {resp.status_code} (Expected {expected_status})")
                    all_passed = False
            except Exception as e:
                print(f"[FAIL] {method:4} {url} -> Connection error: {e}")
                all_passed = False

        # Create live review and test review sub-resources
        try:
            print("\n[INFO] Testing dynamic review creation and sub-resource exports...")
            create_resp = client.post(f"{API_BASE}/reviews", json={"query": "quantum error correction"})
            if create_resp.status_code in (200, 201):
                review_id = create_resp.json()["id"]
                print(f"[PASS] POST {API_BASE}/reviews -> Created {review_id}")

                sub_endpoints = [
                    (f"{API_BASE}/reviews/{review_id}", 200),
                    (f"{API_BASE}/reviews/{review_id}/bibtex", 200),
                    (f"{API_BASE}/reviews/{review_id}/markdown", 200),
                    (f"{API_BASE}/reviews/{review_id}/graph", 200),
                ]
                for url, exp_status in sub_endpoints:
                    sub_resp = client.get(url)
                    if sub_resp.status_code == exp_status:
                        print(f"[PASS] GET  {url} -> {sub_resp.status_code}")
                    else:
                        print(f"[FAIL] GET  {url} -> {sub_resp.status_code} (Expected {exp_status})")
                        all_passed = False
            else:
                print(f"[FAIL] POST {API_BASE}/reviews -> {create_resp.status_code}")
                all_passed = False
        except Exception as e:
            print(f"[FAIL] Dynamic review creation failed: {e}")
            all_passed = False

    print("\n-------------------------------------------------------")
    if all_passed:
        print("[SUCCESS] All smoke tests passed successfully!")
        sys.exit(0)
    else:
        print("[FAILED] One or more smoke tests failed.")
        sys.exit(1)


if __name__ == "__main__":
    run_smoke_tests()
