"""
Topic 7: Implement Self Consistency in Code.

Tasks implemented:

Task 1:
    Deterministic seeded sampling.

Task 2:
    Majority voting with agreement measurement and
    explicit tie handling.

Task 3:
    Minimum-agreement abstain rule.

Task 4:
    Accuracy measurement for different sample sizes.

Task 5:
    Demonstration of the independence assumption using
    correlated samples.

The implementation is local and deterministic.
No external APIs or credentials are required.
"""

from __future__ import annotations

import random
from collections import Counter


DEFAULT_SAMPLE_LIMIT = 100


def noisy_reasoner(
    question: str,
    rng: random.Random,
) -> int:
    """
    Return a mock reasoning answer.

    The reference problem is:

        What is 17 * 3 + 4?

    Correct answer:

        55

    The mock reasoner is correct approximately 70% of
    the time and otherwise returns one of several plausible
    incorrect answers.
    """

    if not isinstance(question, str):
        raise TypeError(
            "question must be a string"
        )

    if not question.strip():
        raise ValueError(
            "question must not be empty"
        )

    true_answer = 17 * 3 + 4

    if rng.random() < 0.70:
        return true_answer

    return rng.choice(
        [-4, -1, 1, 10]
    )


def sample_answers(
    question: str,
    n: int = 15,
    seed: int = 0,
    *,
    max_samples: int = DEFAULT_SAMPLE_LIMIT,
) -> list[int]:
    """
    Sample multiple independent reasoning answers.

    The supplied seed makes the result reproducible.
    """

    if not isinstance(question, str):
        raise TypeError(
            "question must be a string"
        )

    if not question.strip():
        raise ValueError(
            "question must not be empty"
        )

    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError(
            "n must be an integer"
        )

    if not isinstance(seed, int) or isinstance(seed, bool):
        raise TypeError(
            "seed must be an integer"
        )

    if not isinstance(
        max_samples,
        int,
    ) or isinstance(
        max_samples,
        bool,
    ):
        raise TypeError(
            "max_samples must be an integer"
        )

    if max_samples <= 0:
        raise ValueError(
            "max_samples must be greater than zero"
        )

    if n <= 0:
        raise ValueError(
            "n must be greater than zero"
        )

    if n > max_samples:
        raise ValueError(
            f"n must not exceed max_samples "
            f"({max_samples})"
        )

    rng = random.Random(seed)

    answers = [
        noisy_reasoner(
            question,
            rng,
        )
        for _ in range(n)
    ]

    return answers


def majority_vote(
    answers: list[int],
) -> tuple[int | None, float, dict[int, int]]:
    """
    Calculate the majority answer and agreement ratio.

    A clear winner is returned only when exactly one answer
    has the highest vote count.

    If multiple answers share the highest vote count,
    the result is considered a tie and the answer is None.
    """

    if not isinstance(answers, list):
        raise TypeError(
            "answers must be a list"
        )

    if not answers:
        raise ValueError(
            "answers must not be empty"
        )

    if not all(
        isinstance(answer, int)
        and not isinstance(answer, bool)
        for answer in answers
    ):
        raise TypeError(
            "answers must contain integers"
        )

    votes = Counter(answers)

    highest_count = max(
        votes.values()
    )

    winners = [
        answer
        for answer, count in votes.items()
        if count == highest_count
    ]

    agreement = (
        highest_count / len(answers)
    )

    if len(winners) != 1:
        return (
            None,
            round(agreement, 2),
            dict(votes),
        )

    return (
        winners[0],
        round(agreement, 2),
        dict(votes),
    )


def self_consistency(
    question: str,
    n: int = 15,
    seed: int = 0,
    min_agreement: float = 0.4,
) -> dict:
    """
    Run seeded sampling followed by majority voting.

    If agreement is below min_agreement, the function
    abstains by returning answer=None.
    """

    if not isinstance(
        min_agreement,
        (int, float),
    ) or isinstance(
        min_agreement,
        bool,
    ):
        raise TypeError(
            "min_agreement must be a number"
        )

    if not 0 <= min_agreement <= 1:
        raise ValueError(
            "min_agreement must be between 0 and 1"
        )

    answers = sample_answers(
        question,
        n=n,
        seed=seed,
    )

    answer, agreement, votes = majority_vote(
        answers
    )

    if (
        answer is not None
        and agreement < min_agreement
    ):
        answer = None

    return {
        "answer": answer,
        "agreement": agreement,
        "votes": votes,
        "samples": n,
        "abstained": answer is None,
    }


def measure_accuracy(
    sample_sizes: list[int],
    trials: int = 200,
    base_seed: int = 1000,
) -> list[dict]:
    """
    Measure self-consistency accuracy for several sample sizes.

    The abstain rule is disabled during measurement by using
    min_agreement=0.0.
    """

    if not isinstance(sample_sizes, list):
        raise TypeError(
            "sample_sizes must be a list"
        )

    if not sample_sizes:
        raise ValueError(
            "sample_sizes must not be empty"
        )

    if not all(
        isinstance(size, int)
        and not isinstance(size, bool)
        for size in sample_sizes
    ):
        raise TypeError(
            "sample_sizes must contain integers"
        )

    if not all(
        size > 0
        for size in sample_sizes
    ):
        raise ValueError(
            "sample sizes must be greater than zero"
        )

    if not isinstance(
        trials,
        int,
    ) or isinstance(
        trials,
        bool,
    ):
        raise TypeError(
            "trials must be an integer"
        )

    if trials <= 0:
        raise ValueError(
            "trials must be greater than zero"
        )

    if not isinstance(
        base_seed,
        int,
    ) or isinstance(
        base_seed,
        bool,
    ):
        raise TypeError(
            "base_seed must be an integer"
        )

    results = []

    question = "What is 17*3+4?"
    expected_answer = 55

    for sample_size in sample_sizes:

        correct = 0

        for trial in range(trials):

            seed = (
                base_seed
                + trial
            )

            result = self_consistency(
                question,
                n=sample_size,
                seed=seed,
                min_agreement=0.0,
            )

            if result["answer"] == expected_answer:
                correct += 1

        accuracy = (
            correct / trials
        )

        results.append(
            {
                "samples": sample_size,
                "correct": correct,
                "trials": trials,
                "accuracy": round(
                    accuracy,
                    4,
                ),
            }
        )

    return results


def correlated_sample_answers(
    question: str,
    n: int = 15,
    seed: int = 0,
    *,
    max_samples: int = DEFAULT_SAMPLE_LIMIT,
) -> list[int]:
    """
    Generate correlated samples that share one latent decision.

    Instead of making an independent correctness decision for
    every sample, one correctness decision is made once and
    reused by every sample.

    This intentionally breaks the independence assumption.

    If the shared decision is correct, all samples return 55.

    If the shared decision is incorrect, all samples return
    the same incorrect answer.

    Therefore increasing n does not provide independent
    evidence and cannot correct a shared systematic error.
    """

    if not isinstance(question, str):
        raise TypeError(
            "question must be a string"
        )

    if not question.strip():
        raise ValueError(
            "question must not be empty"
        )

    if not isinstance(
        n,
        int,
    ) or isinstance(
        n,
        bool,
    ):
        raise TypeError(
            "n must be an integer"
        )

    if not isinstance(
        seed,
        int,
    ) or isinstance(
        seed,
        bool,
    ):
        raise TypeError(
            "seed must be an integer"
        )

    if not isinstance(
        max_samples,
        int,
    ) or isinstance(
        max_samples,
        bool,
    ):
        raise TypeError(
            "max_samples must be an integer"
        )

    if max_samples <= 0:
        raise ValueError(
            "max_samples must be greater than zero"
        )

    if n <= 0:
        raise ValueError(
            "n must be greater than zero"
        )

    if n > max_samples:
        raise ValueError(
            f"n must not exceed max_samples "
            f"({max_samples})"
        )

    rng = random.Random(seed)

    shared_correct = (
        rng.random() < 0.70
    )

    if shared_correct:
        shared_answer = 55
    else:
        shared_answer = rng.choice(
            [-4, -1, 1, 10]
        )

    return [
        shared_answer
        for _ in range(n)
    ]


def measure_correlated_accuracy(
    sample_sizes: list[int],
    trials: int = 200,
    base_seed: int = 1000,
) -> list[dict]:
    """
    Measure accuracy when samples are correlated.

    The same evaluation setup used by measure_accuracy() is
    retained, but the samples within each trial share a single
    latent correctness decision.
    """

    if not isinstance(
        sample_sizes,
        list,
    ):
        raise TypeError(
            "sample_sizes must be a list"
        )

    if not sample_sizes:
        raise ValueError(
            "sample_sizes must not be empty"
        )

    if not all(
        isinstance(size, int)
        and not isinstance(size, bool)
        for size in sample_sizes
    ):
        raise TypeError(
            "sample_sizes must contain integers"
        )

    if not all(
        size > 0
        for size in sample_sizes
    ):
        raise ValueError(
            "sample sizes must be greater than zero"
        )

    if not isinstance(
        trials,
        int,
    ) or isinstance(
        trials,
        bool,
    ):
        raise TypeError(
            "trials must be an integer"
        )

    if trials <= 0:
        raise ValueError(
            "trials must be greater than zero"
        )

    if not isinstance(
        base_seed,
        int,
    ) or isinstance(
        base_seed,
        bool,
    ):
        raise TypeError(
            "base_seed must be an integer"
        )

    results = []

    question = "What is 17*3+4?"
    expected_answer = 55

    for sample_size in sample_sizes:

        correct = 0

        for trial in range(trials):

            seed = (
                base_seed
                + trial
            )

            answers = correlated_sample_answers(
                question,
                n=sample_size,
                seed=seed,
            )

            answer, _, _ = majority_vote(
                answers
            )

            if answer == expected_answer:
                correct += 1

        accuracy = (
            correct / trials
        )

        results.append(
            {
                "samples": sample_size,
                "correct": correct,
                "trials": trials,
                "accuracy": round(
                    accuracy,
                    4,
                ),
            }
        )

    return results


def main() -> None:
    """Run a deterministic Task 5 demonstration."""

    question = "What is 17*3+4?"

    result = self_consistency(
        question,
        n=15,
        seed=0,
    )

    print(
        "Topic 7 — Self Consistency"
    )
    print("=" * 50)

    print(
        f"question: {question}"
    )

    print(
        f"self-consistency result: {result}"
    )

    print()
    print(
        "Independent accuracy measurement"
    )
    print("-" * 50)

    independent_results = measure_accuracy(
        [1, 5, 15, 31],
        trials=200,
        base_seed=1000,
    )

    for row in independent_results:

        print(
            f"n={row['samples']:>2} | "
            f"accuracy={row['accuracy']:.4f} | "
            f"correct={row['correct']}/"
            f"{row['trials']}"
        )

    print()
    print(
        "Correlated accuracy measurement"
    )
    print("-" * 50)

    correlated_results = (
        measure_correlated_accuracy(
            [1, 5, 15, 31],
            trials=200,
            base_seed=1000,
        )
    )

    for row in correlated_results:

        print(
            f"n={row['samples']:>2} | "
            f"accuracy={row['accuracy']:.4f} | "
            f"correct={row['correct']}/"
            f"{row['trials']}"
        )


if __name__ == "__main__":
    main()