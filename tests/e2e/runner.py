#!/usr/bin/env python3
"""
Master E2E Test Runner for Project Veritas.
Supports --all, --tier 1, --tier 2, --tier 3, --tier 4.
Generates colorized pass/fail summaries, timing reports, and proper exit codes.
"""

import argparse
import os
import sys
import time
import subprocess
from typing import Dict, List, Tuple

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Tiers configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TIERS: Dict[int, Dict[str, str]] = {
    1: {
        "name": "Tier 1: Feature Coverage (F0-F6)",
        "path": os.path.join(BASE_DIR, "tier1_features"),
        "expected_min": 35
    },
    2: {
        "name": "Tier 2: Boundary & Corner Cases",
        "path": os.path.join(BASE_DIR, "tier2_boundaries"),
        "expected_min": 35
    },
    3: {
        "name": "Tier 3: Pairwise Combinations",
        "path": os.path.join(BASE_DIR, "tier3_pairwise"),
        "expected_min": 15
    },
    4: {
        "name": "Tier 4: Real-World Research Workloads",
        "path": os.path.join(BASE_DIR, "tier4_real_world"),
        "expected_min": 5
    }
}


def print_banner():
    banner = f"""
{CYAN}{BOLD}================================================================================
                    PROJECT VERITAS -- E2E TEST RUNNER
================================================================================{RESET}
Opaque-box, requirement-driven verification across all 4 testing tiers.
    """
    print(banner)


def run_tier(tier_num: int, verbose: bool = False) -> Tuple[int, float, int, str]:
    """
    Runs tests for a given tier using pytest.
    Returns: (exit_code, duration_seconds, test_count, output_str)
    """
    tier_info = TIERS[tier_num]
    tier_path = tier_info["path"]
    tier_name = tier_info["name"]

    if not os.path.exists(tier_path):
        return (1, 0.0, 0, f"Directory does not exist: {tier_path}")

    print(f"\n{BLUE}{BOLD}>>> Running {tier_name}...{RESET}")
    start_time = time.time()

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        tier_path,
        "-q" if not verbose else "-v",
        "--tb=short"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(BASE_DIR)))
    duration = time.time() - start_time

    output = result.stdout + "\n" + result.stderr

    # Parse count of passed tests if possible
    passed_count = 0
    for line in output.split("\n"):
        if "passed" in line:
            import re
            m = re.search(r"(\d+)\s+passed", line)
            if m:
                passed_count = int(m.group(1))

    return (result.returncode, duration, passed_count, output)


def print_summary_table(results: Dict[int, Tuple[int, float, int]]):
    print(f"\n{CYAN}{BOLD}================================================================================{RESET}")
    print(f"{BOLD}{'Tier':<4} | {'Tier Name':<40} | {'Tests':<7} | {'Time (s)':<9} | {'Status':<10}{RESET}")
    print(f"{CYAN}--------------------------------------------------------------------------------{RESET}")

    total_tests = 0
    total_time = 0.0
    all_passed = True

    for tier_num in sorted(results.keys()):
        code, duration, count = results[tier_num]
        name = TIERS[tier_num]["name"]
        total_tests += count
        total_time += duration

        if code == 0:
            status_str = f"{GREEN}PASS{RESET}"
        else:
            status_str = f"{RED}FAIL{RESET}"
            all_passed = False

        print(f"{tier_num:<4} | {name:<40} | {count:<7} | {duration:<9.2f} | {status_str:<10}")

    print(f"{CYAN}--------------------------------------------------------------------------------{RESET}")
    overall = f"{GREEN}{BOLD}PASS (100%){RESET}" if all_passed else f"{RED}{BOLD}FAIL{RESET}"
    print(f"{BOLD}{'ALL':<4} | {'Total Across Selected Tiers':<40} | {total_tests:<7} | {total_time:<9.2f} | {overall}{RESET}")
    print(f"{CYAN}{BOLD}================================================================================{RESET}\n")

    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Veritas Master E2E Test Runner")
    parser.add_argument("--all", action="store_true", help="Run all 4 testing tiers")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3, 4], help="Run a specific tier (1, 2, 3, or 4)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose pytest output")

    args = parser.parse_args()

    if not args.all and args.tier is None:
        # Default to running all if no flag provided
        args.all = True

    print_banner()

    tiers_to_run = [1, 2, 3, 4] if args.all else [args.tier]
    results: Dict[int, Tuple[int, float, int]] = {}
    failed_outputs: List[Tuple[int, str]] = []

    for t in tiers_to_run:
        code, duration, count, output = run_tier(t, verbose=args.verbose)
        results[t] = (code, duration, count)
        if code != 0:
            failed_outputs.append((t, output))
        else:
            print(f"{GREEN}[PASS] {TIERS[t]['name']} completed successfully ({count} tests in {duration:.2f}s){RESET}")

    if failed_outputs:
        print(f"\n{RED}{BOLD}Failures Summary:{RESET}")
        for t, out in failed_outputs:
            print(f"\n{RED}--- [Tier {t}] Output ---{RESET}")
            print(out)

    all_passed = print_summary_table(results)

    if all_passed:
        print(f"{GREEN}{BOLD}E2E Test Suite verification PASSED. All requirement criteria satisfied.{RESET}\n")
        sys.exit(0)
    else:
        print(f"{RED}{BOLD}E2E Test Suite verification FAILED. See details above.{RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
