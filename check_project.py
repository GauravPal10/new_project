"""One-command offline check. Does not contact AI providers or require an API key."""
import json
import platform
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def main():
    print("AsOf project check - offline, no API key needed", flush=True)
    print(f"Python {platform.python_version()} | SQLite {sqlite3.sqlite_version}", flush=True)
    if sys.version_info < (3, 11) or sqlite3.sqlite_version_info < (3, 35, 0):
        print("SETUP REQUIRED: use Python 3.11+ with SQLite 3.35+.")
        return 1
    report = {"kind": "offline_project_check_NOT_model_results", "checks": [], "external_model_calls": 0}
    commands = [
        ("Automated tests", ["-m", "unittest", "discover", "-s", "tests", "-v"]),
        ("Reference answers and deliberately wrong queries", ["run_eval.py", "validate"]),
    ]
    for label, args in commands:
        try:
            run = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True,
                                 text=True, encoding="utf-8", timeout=120)
            passed = run.returncode == 0
            details = run.stdout + run.stderr
        except subprocess.TimeoutExpired:
            passed, details = False, "Command exceeded 120 seconds."
        report["checks"].append({"name": label, "passed": passed, "details": details})
        print(f"{'PASS' if passed else 'FAIL'} - {label}", flush=True)
        if not passed:
            print(details)
            break
    if all(check["passed"] for check in report["checks"]):
        from asof.grader import grade
        task = "01_visibility"
        known_correct = (ROOT / "reference" / (task + ".sql")).read_text(encoding="utf-8")
        correct = grade(task, known_correct)
        wrong = grade(task, "SELECT request_id, 0 AS total_cents FROM requests")
        for label, passed in [("Known-correct SQL accepted", correct["passed"]),
                              ("Deliberately wrong SQL rejected", not wrong["passed"])]:
            report["checks"].append({"name": label, "passed": passed})
            print(f"{'PASS' if passed else 'FAIL'} - {label}", flush=True)
    report["passed"] = len(report["checks"]) == 4 and all(c["passed"] for c in report["checks"])
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "quick_check.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("\nALL CHECKS PASSED - the evaluator is working on the tested cases." if report["passed"] else "\nCHECK FAILED - read results/quick_check.json for details.")
    print("This checks the project software. Real AI model performance still needs separate trials.")
    return 0 if report["passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
