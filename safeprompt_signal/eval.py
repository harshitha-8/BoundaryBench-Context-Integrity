"""Inspect task for BoundaryBench Context Integrity."""

from __future__ import annotations

import json
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import FieldSpec, json_dataset
from inspect_ai.scorer import CORRECT, INCORRECT, Score, Target, accuracy, scorer, stderr
from inspect_ai.solver import TaskState, generate

from safeprompt_signal.scoring import score_completion


DATASET_PATH = Path(__file__).resolve().parent.parent / "data" / "context_boundary_cases.jsonl"


@scorer(metrics=[accuracy(), stderr()])
def prompt_injection_safety():
    """Grade whether a completion preserves the context boundary."""

    async def score(state: TaskState, target: Target) -> Score:
        rubric = json.loads(target.text)
        result = score_completion(state.output.completion, rubric)
        return Score(
            value=CORRECT if result["passed"] else INCORRECT,
            answer=state.output.completion,
            explanation=result["explanation"],
            metadata=result,
        )

    return score


@task
def safeprompt_signal():
    """Evaluate context-boundary integrity on synthetic canary prompts."""

    return Task(
        dataset=json_dataset(
            str(DATASET_PATH),
            FieldSpec(
                input="input",
                target="target",
                id="id",
                metadata=["attack_type", "risk_area", "difficulty"],
            ),
        ),
        solver=generate(),
        scorer=prompt_injection_safety(),
    )
