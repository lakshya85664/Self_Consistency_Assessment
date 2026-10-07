"""
Topic 7 — Self Consistency
Evidence Generator

Creates deterministic JSON evidence for Tasks 1–5
and records the complete pytest result.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
EVIDENCE_DIR = PROJECT_ROOT / "evidence"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from self_consistency import (
    correlated_sample_answers,
    majority_vote,
    measure_accuracy,
    measure_correlated_accuracy,
    sample_answers,
    self_consistency,
)


QUESTION = "What is 17*3+4?"


def write_json(filename: str, data: dict) -> None:
    path = EVIDENCE_DIR / filename

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=2,
        )


def generate_task_1_evidence() -> None:
    answers = sample_answers(
        QUESTION,
        n=15,
        seed=0,
    )

    write_json(
        "sampling_trace.json",
        {
            "task": 1,
            "title": "Implement Sampling",
            "question": QUESTION,
            "samples": 15,
            "seed": 0,
            "answers": answers,
            "deterministic": True,
        },
    )


def generate_task_2_evidence() -> None:
    answers = sample_answers(
        QUESTION,
        n=15,
        seed=0,
    )

    answer, agreement, votes = majority_vote(
        answers
    )

    write_json(
        "voting_result.json",
        {
            "task": 2,
            "title": "Implement Majority Voting",
            "question": QUESTION,
            "samples": 15,
            "answer": answer,
            "agreement": agreement,
            "votes": {
                str(key): value
                for key, value in votes.items()
            },
            "abstained": answer is None,
        },
    )


def generate_task_3_evidence() -> None:
    low_threshold = self_consistency(
        QUESTION,
        n=15,
        seed=0,
        min_agreement=0.50,
    )

    exact_threshold = self_consistency(
        QUESTION,
        n=15,
        seed=0,
        min_agreement=0.47,
    )

    write_json(
        "abstain_cases.json",
        {
            "task": 3,
            "title": "Add an Abstain Rule",
            "question": QUESTION,
            "below_threshold": low_threshold,
            "exact_threshold": exact_threshold,
        },
    )


def generate_task_4_evidence() -> None:
    results = measure_accuracy(
        [1, 5, 15, 31],
        trials=200,
        base_seed=1000,
    )

    write_json(
        "accuracy_results.json",
        {
            "task": 4,
            "title": "Measure Accuracy for Different Sample Sizes",
            "method": "independent_samples",
            "results": results,
        },
    )


def generate_task_5_evidence() -> None:
    independent = measure_accuracy(
        [1, 5, 15, 31],
        trials=200,
        base_seed=1000,
    )

    correlated = measure_correlated_accuracy(
        [1, 5, 15, 31],
        trials=200,
        base_seed=1000,
    )

    correlated_samples = correlated_sample_answers(
        QUESTION,
        n=15,
        seed=0,
    )

    write_json(
        "correlation_results.json",
        {
            "task": 5,
            "title": "Break the Independence Assumption",
            "question": QUESTION,
            "correlated_sample_example": correlated_samples,
            "independent_results": independent,
            "correlated_results": correlated,
            "interpretation": (
                "Independent samples provide additional evidence as "
                "sample size increases. Correlated samples share one "
                "latent correctness decision, so increasing the sample "
                "count does not improve accuracy."
            ),
        },
    )


def generate_test_summary() -> None:
    command = [
        sys.executable,
        "-m",
        "pytest",
        "tests\\test_self_consistency.py",
        "-q",
    ]

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    write_json(
        "test_summary.json",
        {
            "test_file": "tests/test_self_consistency.py",
            "command": "python -m pytest tests\\test_self_consistency.py -q",
            "return_code": result.returncode,
            "status": (
                "PASS"
                if result.returncode == 0
                else "FAIL"
            ),
            "stdout": result.stdout,
            "stderr": result.stderr,
        },
    )


def main() -> None:
    EVIDENCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    generate_task_1_evidence()
    generate_task_2_evidence()
    generate_task_3_evidence()
    generate_task_4_evidence()
    generate_task_5_evidence()
    generate_test_summary()

    print("=" * 60)
    print("Topic 7 — Evidence Generation")
    print("=" * 60)
    print()
    print("Evidence generated successfully.")
    print()

    for path in sorted(
        EVIDENCE_DIR.glob("*.json")
    ):
        print(
            f"[OK] {path.name}"
        )


if __name__ == "__main__":
    main()