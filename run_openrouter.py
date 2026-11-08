"""Optional, user-initiated paid/free model calls. Never used by offline validation."""
import argparse
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from asof.cli import prompt, save_trial, write_json
from asof.spec import TASKS

def main():
    p = argparse.ArgumentParser(description="Optional OpenRouter runner; may incur charges.")
    p.add_argument("--model", required=True, help="Exact provider/model ID you have checked")
    p.add_argument("--tasks", nargs="+", choices=TASKS, default=list(TASKS))
    p.add_argument("--trials", type=int, default=3)
    p.add_argument("--max-tokens", type=int, default=6000)
    p.add_argument("--temperature", type=float, default=None)
    p.add_argument("--out", default="runs/openrouter")
    p.add_argument("--allow-network", action="store_true", help="Explicitly initiate requests that may cost money")
    a = p.parse_args()
    if not 1 <= a.trials <= 10 or not 1 <= a.max_tokens <= 16000: p.error("Invalid trial/token limit")
    if not a.allow_network: p.error("No requests sent. Review prices and set a provider credit limit, then pass --allow-network.")
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key: p.error("Set OPENROUTER_API_KEY locally. Never put it in the submission.")
    folder = Path(a.out); folder.mkdir(parents=True, exist_ok=True)
    settings = {"temperature": a.temperature, "max_tokens": a.max_tokens, "tools": "none", "provider": "OpenRouter"}
    for task in a.tasks:
        for trial in range(1, a.trials + 1):
            output = folder / f"{task}_trial_{trial}.json"
            if output.exists(): p.error(f"Refusing to overwrite {output}; use a new run directory.")
            payload = {"model": a.model, "messages": [{"role": "user", "content": prompt(task)}], "max_tokens": a.max_tokens}
            if a.temperature is not None: payload["temperature"] = a.temperature
            request = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
                data=json.dumps(payload).encode(), headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
            start = time.perf_counter()
            try:
                with urllib.request.urlopen(request, timeout=180) as response:
                    body = json.load(response)
                choice = body["choices"][0]
                raw = choice["message"].get("content") or ""
                if not isinstance(raw, str): raise ValueError("Non-text response")
            except (urllib.error.URLError, KeyError, ValueError, IndexError) as exc:
                write_json(output.with_suffix(".error.json"), {"kind": "api_error_NOT_model_failure", "task": task,
                    "trial": trial, "model": a.model, "error_type": type(exc).__name__})
                raise SystemExit("API failed; stopped without retrying. Inspect your provider account. No credentials logged.")
            metadata = {"source": "OpenRouter API", "reported_model": body.get("model"), "provider": body.get("provider"),
                "response_id": body.get("id"), "usage": body.get("usage"), "finish_reason": choice.get("finish_reason"),
                "seconds_model": round(time.perf_counter()-start, 4)}
            # Preserve available output; do not manufacture or request hidden chain-of-thought.
            result = save_trial(task, raw, a.model, trial, settings, output, metadata)
            print(task, trial, "PASS" if result["passed"] else "FAIL", metadata["finish_reason"])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
