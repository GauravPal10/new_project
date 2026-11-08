"""Explain historical visibility using a tiny, automatically checked example."""
import json
from pathlib import Path
from asof.data import example
from asof.grader import execute
from asof.oracle import solve
from asof.reference import query

ROOT = Path(__file__).resolve().parent

def main():
    task = "01_visibility"
    dataset = example(task)
    correct_sql = query(task)
    incorrect_sql = """SELECT q.request_id, COALESCE(SUM(s.amount_cents), 0) AS total_cents
FROM requests q
LEFT JOIN sales s ON s.customer_id = q.customer_id
 AND s.event_ts BETWEEN q.window_start AND q.cutoff
GROUP BY q.request_id"""
    expected = solve(task, dataset)
    correct = sorted(execute(correct_sql, dataset))
    incorrect = sorted(execute(incorrect_sql, dataset))
    passed = (expected == [(1, 1000), (2, 1500), (3, 0)] and correct == expected
              and incorrect == [(1, 1500), (2, 1500), (3, 0)])
    lines = [
        "ASOF DEMO: Can a report use information that arrived later?",
        "", "All amounts are cents. Times are simplified integer seconds.",
        "", "Order | Customer | Event time | Available time | Amount",
        "    1 |        1 |         50 |             60 |   1000",
        "    2 |        1 |         80 |            150 |    500",
        "", "Request 1: customer 1, cutoff 100. Order 2 was not available yet.",
        "Request 2: customer 1, cutoff 200. Both orders were available.",
        "Request 3: customer 2, cutoff 200. This customer has no sales.",
        "", "Request | Expected | Correct SQL | Incorrect SQL",
    ]
    for exp, good, bad in zip(expected, correct, incorrect):
        lines.append(f"{exp[0]:7} | {exp[1]:8} | {good[1]:11} | {bad[1]:13}")
    lines += ["", "Correct SQL: PASS" if correct == expected else "Correct SQL: UNEXPECTED FAILURE",
              "Incorrect SQL: FAIL (expected - it ignores when the data became available)",
              "", "The incorrect query reports 1500 instead of 1000 at cutoff 100.",
              "It counts a 500-cent order that was not available until time 150.",
              "", "The missing condition in the incorrect query is: s.known_ts <= q.cutoff",
              "", "DEMO VERIFIED" if passed else "DEMO CHECK FAILED",
              "These are prepared example queries, not actual AI model responses.",
              "Open results/demo.json for the input data, both SQL queries, and results."]
    report = {"kind": "prepared_demo_NOT_model_results", "verified": passed, "task": task,
              "data": dataset, "expected": expected, "correct_sql": correct_sql,
              "correct_result": correct, "incorrect_sql": incorrect_sql,
              "incorrect_result": incorrect, "external_model_calls": 0}
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "demo.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (ROOT / "results" / "demo.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0 if passed else 1

if __name__ == "__main__":
    raise SystemExit(main())
