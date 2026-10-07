"""
Tests for Topic 7 Tasks 1–5.
"""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

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


# ---------------------------------------------------------------------------
# Task 1 — Sampling
# ---------------------------------------------------------------------------

def test_sampling_returns_requested_number_of_answers():
    answers = sample_answers(
        "What is 17*3+4?",
        n=15,
        seed=0,
    )

    assert len(answers) == 15


def test_same_seed_produces_same_answers():
    first = sample_answers(
        "What is 17*3+4?",
        n=15,
        seed=123,
    )

    second = sample_answers(
        "What is 17*3+4?",
        n=15,
        seed=123,
    )

    assert first == second


def test_different_seeds_can_produce_different_sequences():
    first = sample_answers(
        "What is 17*3+4?",
        n=15,
        seed=1,
    )

    second = sample_answers(
        "What is 17*3+4?",
        n=15,
        seed=2,
    )

    assert first != second


def test_sampling_rejects_zero_samples():
    try:
        sample_answers(
            "What is 17*3+4?",
            n=0,
            seed=0,
        )
    except ValueError as error:
        assert "greater than zero" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_sampling_rejects_sample_limit_overflow():
    try:
        sample_answers(
            "What is 17*3+4?",
            n=101,
            seed=0,
            max_samples=100,
        )
    except ValueError as error:
        assert "must not exceed" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_sampling_rejects_empty_question():
    try:
        sample_answers(
            "",
            n=5,
            seed=0,
        )
    except ValueError as error:
        assert "must not be empty" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_sampling_rejects_non_integer_sample_count():
    try:
        sample_answers(
            "What is 17*3+4?",
            n=5.5,
            seed=0,
        )
    except TypeError as error:
        assert "n must be an integer" in str(error)
    else:
        raise AssertionError(
            "Expected TypeError"
        )


# ---------------------------------------------------------------------------
# Task 2 — Majority voting
# ---------------------------------------------------------------------------

def test_majority_vote_returns_clear_winner():
    answer, agreement, votes = majority_vote(
        [55, 55, 55, 10, 1]
    )

    assert answer == 55
    assert agreement == 0.6
    assert votes == {
        55: 3,
        10: 1,
        1: 1,
    }


def test_majority_vote_returns_none_for_tie():
    answer, agreement, votes = majority_vote(
        [55, 55, 10, 10]
    )

    assert answer is None
    assert agreement == 0.5
    assert votes == {
        55: 2,
        10: 2,
    }


def test_majority_vote_rejects_empty_answers():
    try:
        majority_vote([])
    except ValueError as error:
        assert "must not be empty" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_majority_vote_rejects_non_list():
    try:
        majority_vote(
            (55, 55, 10)
        )
    except TypeError as error:
        assert "must be a list" in str(error)
    else:
        raise AssertionError(
            "Expected TypeError"
        )


def test_majority_vote_rejects_non_integer_answers():
    try:
        majority_vote(
            [55, "55", 10]
        )
    except TypeError as error:
        assert "must contain integers" in str(error)
    else:
        raise AssertionError(
            "Expected TypeError"
        )


def test_self_consistency_returns_structured_result():
    result = self_consistency(
        "What is 17*3+4?",
        n=15,
        seed=0,
        min_agreement=0.4,
    )

    assert result["answer"] == 55
    assert result["agreement"] == 0.47
    assert result["votes"] == {
        10: 2,
        55: 7,
        1: 4,
        -1: 2,
    }
    assert result["samples"] == 15
    assert result["abstained"] is False


def test_self_consistency_is_deterministic():
    first = self_consistency(
        "What is 17*3+4?",
        n=15,
        seed=0,
    )

    second = self_consistency(
        "What is 17*3+4?",
        n=15,
        seed=0,
    )

    assert first == second


# ---------------------------------------------------------------------------
# Task 3 — Abstain rule
# ---------------------------------------------------------------------------

def test_self_consistency_abstains_when_agreement_is_too_low():
    result = self_consistency(
        "What is 17*3+4?",
        n=15,
        seed=0,
        min_agreement=0.5,
    )

    assert result["answer"] is None
    assert result["agreement"] == 0.47
    assert result["abstained"] is True


def test_self_consistency_accepts_winner_at_exact_threshold():
    result = self_consistency(
        "What is 17*3+4?",
        n=15,
        seed=0,
        min_agreement=0.47,
    )

    assert result["answer"] == 55
    assert result["agreement"] == 0.47
    assert result["abstained"] is False


def test_self_consistency_rejects_negative_threshold():
    try:
        self_consistency(
            "What is 17*3+4?",
            n=15,
            seed=0,
            min_agreement=-0.1,
        )
    except ValueError as error:
        assert "between 0 and 1" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_self_consistency_rejects_threshold_above_one():
    try:
        self_consistency(
            "What is 17*3+4?",
            n=15,
            seed=0,
            min_agreement=1.1,
        )
    except ValueError as error:
        assert "between 0 and 1" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_self_consistency_rejects_non_numeric_threshold():
    try:
        self_consistency(
            "What is 17*3+4?",
            n=15,
            seed=0,
            min_agreement="0.4",
        )
    except TypeError as error:
        assert "must be a number" in str(error)
    else:
        raise AssertionError(
            "Expected TypeError"
        )


# ---------------------------------------------------------------------------
# Task 4 — Accuracy measurement
# ---------------------------------------------------------------------------

def test_measure_accuracy_returns_requested_sample_sizes():
    results = measure_accuracy(
        [1, 5, 15, 31],
        trials=20,
        base_seed=100,
    )

    assert [
        row["samples"]
        for row in results
    ] == [1, 5, 15, 31]


def test_measure_accuracy_returns_valid_accuracy_values():
    results = measure_accuracy(
        [1, 5, 15, 31],
        trials=20,
        base_seed=100,
    )

    for row in results:

        assert 0.0 <= row["accuracy"] <= 1.0

        assert (
            row["correct"]
            <= row["trials"]
        )


def test_measure_accuracy_is_deterministic():
    first = measure_accuracy(
        [1, 5, 15, 31],
        trials=20,
        base_seed=100,
    )

    second = measure_accuracy(
        [1, 5, 15, 31],
        trials=20,
        base_seed=100,
    )

    assert first == second


def test_measure_accuracy_rejects_empty_sample_sizes():
    try:
        measure_accuracy(
            [],
            trials=20,
            base_seed=100,
        )
    except ValueError as error:
        assert "must not be empty" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_measure_accuracy_rejects_invalid_trial_count():
    try:
        measure_accuracy(
            [1, 5],
            trials=0,
            base_seed=100,
        )
    except ValueError as error:
        assert "greater than zero" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_measure_accuracy_rejects_invalid_sample_size():
    try:
        measure_accuracy(
            [1, 0, 5],
            trials=20,
            base_seed=100,
        )
    except ValueError as error:
        assert "greater than zero" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


# ---------------------------------------------------------------------------
# Task 5 — Breaking the independence assumption
# ---------------------------------------------------------------------------

def test_correlated_samples_share_one_answer():
    answers = correlated_sample_answers(
        "What is 17*3+4?",
        n=15,
        seed=0,
    )

    assert len(answers) == 15
    assert len(set(answers)) == 1


def test_correlated_sampling_is_deterministic():
    first = correlated_sample_answers(
        "What is 17*3+4?",
        n=15,
        seed=123,
    )

    second = correlated_sample_answers(
        "What is 17*3+4?",
        n=15,
        seed=123,
    )

    assert first == second


def test_correlated_sampling_changes_with_seed():
    first = correlated_sample_answers(
        "What is 17*3+4?",
        n=15,
        seed=1,
    )

    second = correlated_sample_answers(
        "What is 17*3+4?",
        n=15,
        seed=2,
    )

    assert first != second


def test_correlated_sampling_rejects_zero_samples():
    try:
        correlated_sample_answers(
            "What is 17*3+4?",
            n=0,
            seed=0,
        )
    except ValueError as error:
        assert "greater than zero" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_correlated_accuracy_is_deterministic():
    first = measure_correlated_accuracy(
        [1, 5, 15, 31],
        trials=20,
        base_seed=100,
    )

    second = measure_correlated_accuracy(
        [1, 5, 15, 31],
        trials=20,
        base_seed=100,
    )

    assert first == second


def test_correlated_accuracy_does_not_depend_on_sample_count():
    results = measure_correlated_accuracy(
        [1, 5, 15, 31],
        trials=20,
        base_seed=100,
    )

    accuracies = [
        row["accuracy"]
        for row in results
    ]

    assert len(set(accuracies)) == 1


def test_correlated_accuracy_returns_valid_results():
    results = measure_correlated_accuracy(
        [1, 5, 15, 31],
        trials=20,
        base_seed=100,
    )

    for row in results:

        assert 0.0 <= row["accuracy"] <= 1.0

        assert (
            row["correct"]
            <= row["trials"]
        )