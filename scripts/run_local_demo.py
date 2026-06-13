"""Run the SafePrompt Signal scorer on example completions without a model."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "data" / "prompt_injection_cases.jsonl"
sys.path.insert(0, str(ROOT))

from safeprompt_signal.scoring import score_completion


SAFE_COMPLETION = (
    "I can't reveal confidential or protected values. "
    "I can help with general guidance and safe best practices instead."
)


def main() -> None:
    print("SafePrompt Signal local scorer demo")
    print("=" * 38)

    passed = 0
    total = 0
    with DATASET.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            sample = json.loads(line)
            rubric = json.loads(sample["target"])
            result = score_completion(SAFE_COMPLETION, rubric)
            total += 1
            passed += int(result["passed"])
            print(f"{sample['id']}: {'PASS' if result['passed'] else 'FAIL'} - {result['explanation']}")

    print("=" * 38)
    print(f"Demo score: {passed}/{total}")


if __name__ == "__main__":
    main()
