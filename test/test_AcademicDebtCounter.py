from copy import deepcopy

import pytest

from src.AcademicDebtCounter import AcademicDebtCounter
from src.Types import DataType


@pytest.fixture
def mixed_grades() -> DataType:
    return {
        "Alice": [("Math", 85), ("History", 60)],
        "Bob": [("Math", 61), ("History", 100)],
        "Charlie": [("Math", 40), ("History", 50)],
        "Dana": [],
    }


def test_empty_input_returns_zero() -> None:
    assert AcademicDebtCounter({}).count() == 0


def test_student_without_subjects_is_not_counted() -> None:
    assert AcademicDebtCounter({"Alice": []}).count() == 0


def test_all_passing_students_returns_zero() -> None:
    data = {
        "Alice": [("Math", 80), ("History", 90)],
        "Bob": [("Art", 75)],
    }
    assert AcademicDebtCounter(data).count() == 0


@pytest.mark.parametrize(
    "grade, expected", [(0, 1), (60, 1), (61, 0), (100, 0)]
)
def test_single_subject_grade(grade: int, expected: int) -> None:
    data = {"Alice": [("Math", grade)]}
    assert AcademicDebtCounter(data).count() == expected


def test_one_failed_subject_counts_the_student() -> None:
    data = {"Alice": [("Math", 85), ("History", 60), ("Art", 90)]}
    assert AcademicDebtCounter(data).count() == 1


def test_multiple_failed_subjects_count_the_student_once() -> None:
    data = {"Alice": [("Math", 40), ("History", 50)]}
    assert AcademicDebtCounter(data).count() == 1


def test_counts_multiple_students_with_debt() -> None:
    data = {"Alice": [("Math", 40)], "Bob": [("Art", 50)]}
    assert AcademicDebtCounter(data).count() == 2


def test_only_students_with_debt_are_counted(mixed_grades: DataType) -> None:
    assert AcademicDebtCounter(mixed_grades).count() == 2


def test_repeated_calls_return_the_same_count(mixed_grades: DataType) -> None:
    counter = AcademicDebtCounter(mixed_grades)
    assert counter.count() == 2
    assert counter.count() == 2


def test_count_preserves_input_data(mixed_grades: DataType) -> None:
    original_grades = deepcopy(mixed_grades)
    AcademicDebtCounter(mixed_grades).count()
    assert mixed_grades == original_grades
