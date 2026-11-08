# AsOf — Historical SQL Evaluation

AsOf checks whether an AI model can write SQL that calculates a report using **only the information available at a specified past time**.

This project is an evaluation tool. Its output is a pass/fail result and an explanation of which test cases a SQL answer got wrong. It runs locally using Python and SQLite.

## Why this project exists

Business data changes. A sale can arrive late, its amount can be corrected, a record can be deleted, and a refund can be added later. A query may run successfully but still calculate a historically incorrect total.

AsOf makes these errors measurable. It gives a model a reporting task, runs the SQL it produces, and compares the result with verified reference answers. Analysts can use this approach to assess whether generated SQL follows the supplied business rules.

## A simple example

Amounts below are integer cents. Times are simplified integer seconds.

| Order | Event happened at | Data became available at | Amount |
|---|---:|---:|---:|
| 1 | 50 | 60 | 1,000 |
| 2 | 80 | 150 | 500 |

For a report with cutoff **100**, only order 1 was available. The correct total is **1,000**.

A query that looks only at when events happened returns **1,500**, because both event times are before 100. It incorrectly uses information that became available later.

For cutoff **200**, both orders are available, so **1,500** is correct.

AsOf detects this difference. Its harder tasks also cover corrections, deletions, historical customer categories, and refunds.

## How it works

```text
Task instructions + database schema + example data
                       |
                       v
                AI produces SQL
                       |
                       v
       Run SQL on synthetic SQLite datasets
                       |
                       v
 Compare results with independent Python answers
                       |
                       v
       PASS / FAIL + saved results and errors
```

Each task has 35 test datasets. A response passes a task only when every dataset passes. Different correct SQL approaches and different result-row orders are accepted. Missing rows, extra duplicate rows, wrong totals, and invalid SQL are detected.

The reference SQL is also checked against a separately implemented Python calculation. Small examples have explicit expected answers. The tests include deliberately wrong queries to verify that the grader catches mistakes.

## What it evaluates

| Task ID | What the SQL must handle |
|---|---|
| `01_visibility` | Event time versus information-availability time |
| `02_corrections` | The latest correction available at each cutoff |
| `03_deletions` | Deleted and subsequently reinstated records |
| `04_segments` | Customer category history and its corrections |
| `05_refunds` | Refund histories without double-counting sales |
| `06_composition` | All these rules together |

Four tables support the tasks: `requests` specifies the customer and reporting window; `sales` stores sale revisions; `segments` stores customer-category history; `refunds` stores refund revisions.

The full rules are included in every task prompt. These are synthetic, explicitly defined reporting rules, not a claim of compliance with accounting standards.

## Requirements

- **Python 3.11 or later**, with SQLite 3.35 or later. The checker displays both versions.
- Windows, macOS, or Linux.
- No third-party Python packages or separate database server.
- No API key or internet connection for the demonstration and local checks.

If Python is missing, obtain it from the [official Python downloads page](https://www.python.org/downloads/). Reopen your terminal after installing it.

## Run it on Windows

### 1. Extract the ZIP

Right-click `AsOf_SQL_Eval.zip` and choose **Extract All**. Open the extracted `asof_eval` folder. You should see `demo.py`, `check_project.py`, `run_eval.py`, and this README.

The ZIP is an archive, not an executable. Run the Python files after extraction. The README is a text document; open it in a text editor or a Markdown viewer.

### 2. Open a terminal in the project folder

In File Explorer, click the address bar, type `cmd`, and press **Enter**. This opens Command Prompt in the correct folder.

Check Python:

```text
python --version
```

If that fails, try `py -3 --version`. If this works, replace `python` with `py -3` in the following commands. On macOS/Linux, use `python3` if needed.

### 3. See what the project does

```text
python demo.py
```

The demonstration shows the two orders above and compares a correct query with a prepared incorrect query:

```text
Request | Expected | Correct SQL | Incorrect SQL
      1 |     1000 |        1000 |          1500
      2 |     1500 |        1500 |          1500
      3 |        0 |           0 |             0

Correct SQL: PASS
Incorrect SQL: FAIL (expected - it ignores when the data became available)

DEMO VERIFIED
```

Request 3 is a customer with no sales. The incorrect query's failure is intentional: it demonstrates the type of mistake the evaluator detects.

Open `results/demo.txt` to read the explanation again. `results/demo.json` contains the data, both SQL queries, and their outputs. These queries are prepared examples, not actual model responses.

### 4. Check the complete project

```text
python check_project.py
```

Expected output includes:

```text
PASS - Automated tests
PASS - Reference answers and deliberately wrong queries
PASS - Known-correct SQL accepted
PASS - Deliberately wrong SQL rejected

ALL CHECKS PASSED - the evaluator is working on the tested cases.
```

This runs 26 automated tests, validates 210 reference datasets across six tasks, checks seven deliberately flawed implementations, and demonstrates acceptance and rejection of SQL answers. Details are saved in `results/quick_check.json` and `results/local_validation.json`.

These checks establish that the software behaves correctly on the tested cases. They do not prove that every possible grader bug is absent or that an AI model will fail the benchmark.

## Evaluate an actual AI answer without an API

1. Run `python run_eval.py export` to create the task prompts.
2. Open `model_inputs/01_visibility.txt` and copy the entire prompt.
3. Give it to a **fresh model conversation**. Do not upload the ZIP or show the model reference answers or grading code.
4. Save the complete, unedited response as `answer_01.txt` beside `run_eval.py`. In Notepad, choose **All files** and UTF-8 so it is not saved as `answer_01.txt.txt`.
5. Run this command, replacing the quoted model label with its actual displayed name:

```text
python run_eval.py grade --task 01_visibility --response answer_01.txt --model "ACTUAL MODEL NAME" --trial 1 --out runs/model_a/01_visibility_1.json
```

`PASS (graded)` means that response passed all 35 datasets for this task. `FAIL` means it failed at least one check or violated the declared response format. Open the saved JSON to inspect the expected and actual results or execution errors.

A model's FAIL is not automatically a project malfunction. Inspect the failed case and confirm whether the model answer or the grader is wrong. Preserve the original response rather than silently correcting it.

For repeatability, use fresh conversations and record three trials for each of the six tasks: **18 responses per model**. Change task IDs, trial numbers, input filenames, and output filenames accordingly. Keep the model settings consistent. More detailed recording guidance is in `docs/MANUAL_MODEL_RUNS.md`.

Create the combined report:

```text
python run_eval.py summarize --runs runs --trials 3 --out results/model_summary
```

Open `results/model_summary.md` for the readable report. Incomplete runs are marked incomplete. The JSON summary is available alongside it.

## Optional automated model calls

`run_openrouter.py` can collect responses through OpenRouter if you later obtain an API key. It is separate from the offline checks and may incur charges. Set `OPENROUTER_API_KEY` locally, check current model IDs and pricing, and configure your account's credit limit before use.

```text
python run_openrouter.py --model PROVIDER/MODEL_ID --tasks 01_visibility --trials 1 --out runs/api_pilot --allow-network
```

Replace `PROVIDER/MODEL_ID` with an actual supported ID. Never include a real key in this project or ZIP. This connector has been tested with a simulated response, not a live API request.

## Main files

| File or folder | Purpose |
|---|---|
| `demo.py` | Explain the concept using a small working example |
| `check_project.py` | Run all offline project checks |
| `run_eval.py` | Export prompts, validate, grade, and summarize |
| `asof/` | Task definitions, data generators, reference logic, and grader |
| `tasks/` and `model_inputs/` | Task specifications and model prompts |
| `reference/` | Known-correct SQL, for review only |
| `examples/` | Sample inputs and reviewer-only expected results |
| `tests/` | Automated checks of the evaluation software |
| `results/` | Demonstration, validation, and generated summaries |
| `runs/` | Actual model trial records, created when you grade responses |
| `RESEARCH.md` and `PROVENANCE.md` | Background sources and AI-assistance disclosure |

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` is not recognized | Try `py -3` on Windows, or install/configure Python |
| Version/setup error | Use Python 3.11+; check the displayed SQLite version |
| Cannot find `demo.py` or `check_project.py` | Extract the updated ZIP and open its `asof_eval` folder |
| No module named `asof` | Keep the extracted folders together; do not move only the scripts |
| Cannot find `answer_01.txt` | Save it next to `run_eval.py`; check its actual extension |
| Output already exists | Use a new trial number and output filename to preserve prior results |
| SQL format error | Inspect the saved answer; prompts request plain SQL or one SQL code block |
| Offline checker fails | Read `results/quick_check.json` and the terminal error before trusting scores |

## Current scope and status

The demonstration and local validation are implemented and tested. **No real external AI model has been evaluated in this package yet.** Actual performance claims require saved model responses and review of their results.

This is a small, related set of synthetic SQLite tasks. It measures single-response SQL generation under the supplied rules. It does not measure all SQL ability, production readiness, or a complete autonomous analyst. The assistant drafted the implementation and references; participant review is still required.

Its solution is a reproducible way to **detect and explain historical-reporting errors in generated SQL**. It does not automatically repair those queries or guarantee that a particular AI model will fail.
