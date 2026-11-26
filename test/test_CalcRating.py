import pytest

from src.CalcRating import CalcRating
from src.Types import DataType


@pytest.fixture
def student_grades() -> DataType:
    return {
        "Alice": [("Math", 80), ("History", 85)],
        "Bob": [("Math", 100), ("History", 90), ("Art", 61)],
    }


def test_initialization_stores_student_grades(
    student_grades: DataType,
) -> None:
    assert CalcRating(student_grades).data == student_grades


def test_calculates_averages_for_multiple_students(
    student_grades: DataType,
) -> None:
    assert CalcRating(student_grades).calc() == pytest.approx(
        {"Alice": 82.5, "Bob": 251 / 3}
    )


@pytest.mark.parametrize("score", [0, 73, 100])
def test_single_subject_rating_equals_score(score: int) -> None:
    assert CalcRating({"Alice": [("Math", score)]}).calc() == pytest.approx(
        {"Alice": float(score)}
    )


def test_averages_minimum_and_maximum_grades() -> None:
    calculator = CalcRating({"Alice": [("Math", 0), ("History", 100)]})
    assert calculator.calc() == pytest.approx({"Alice": 50.0})


def test_empty_input_returns_empty_ratings() -> None:
    assert CalcRating({}).calc() == {}


def test_student_without_grades_receives_zero() -> None:
    assert CalcRating({"Alice": []}).calc() == pytest.approx({"Alice": 0.0})


def test_repeated_calculations_do_not_accumulate_ratings(
    student_grades: DataType,
) -> None:
    calculator = CalcRating(student_grades)
    expected = pytest.approx({"Alice": 82.5, "Bob": 251 / 3})
    assert calculator.calc() == expected
    assert calculator.calc() == expected
