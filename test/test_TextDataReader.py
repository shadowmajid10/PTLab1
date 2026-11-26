from collections.abc import Callable
from pathlib import Path

import pytest

from src.TextDataReader import TextDataReader


@pytest.fixture
def reader() -> TextDataReader:
    return TextDataReader()


@pytest.fixture
def write_data(tmp_path: Path) -> Callable[[str, str], str]:
    def write(filename: str, content: str) -> str:
        path = tmp_path / filename
        path.write_text(content, encoding="utf-8")
        return str(path)

    return write


def test_reads_multiple_students_and_integer_scores(
    reader: TextDataReader, write_data: Callable[[str, str], str],
) -> None:
    path = write_data(
        "students.txt", "Alice Smith\n    Math:80\n    Art:90\n"
        "Bob Jones\n\tHistory:100\n",
    )
    data = reader.read(path)
    assert data == {
        "Alice Smith": [("Math", 80), ("Art", 90)],
        "Bob Jones": [("History", 100)],
    }
    assert all(
        isinstance(score, int) for grades in data.values()
        for _, score in grades
    )


def test_reads_cyrillic_names_and_subjects(
    reader: TextDataReader, write_data: Callable[[str, str], str],
) -> None:
    path = write_data("students.txt", "Иван Иванов\n    математика:80\n")
    assert reader.read(path) == {"Иван Иванов": [("математика", 80)]}


def test_ignores_blank_and_whitespace_only_lines(
    reader: TextDataReader, write_data: Callable[[str, str], str],
) -> None:
    path = write_data("students.txt", "\nAlice\n \t\n    Math:80\n\n")
    assert reader.read(path) == {"Alice": [("Math", 80)]}


def test_reads_one_student(
    reader: TextDataReader, write_data: Callable[[str, str], str],
) -> None:
    path = write_data("students.txt", "Alice\n    Math:80\n    Art:95\n")
    assert reader.read(path) == {"Alice": [("Math", 80), ("Art", 95)]}


def test_empty_file_returns_empty_data(
    reader: TextDataReader, write_data: Callable[[str, str], str],
) -> None:
    assert reader.read(write_data("empty.txt", "")) == {}


def test_missing_file_raises_file_not_found(
    reader: TextDataReader, tmp_path: Path,
) -> None:
    with pytest.raises(FileNotFoundError):
        reader.read(str(tmp_path / "missing.txt"))


def test_repeated_reads_use_only_the_current_file(
    reader: TextDataReader, write_data: Callable[[str, str], str],
) -> None:
    first_path = write_data("first.txt", "Alice\n    Math:80\n")
    second_path = write_data("second.txt", "Bob\n    Art:95\n")

    first_data = reader.read(first_path)
    assert reader.read(second_path) == {"Bob": [("Art", 95)]}
    assert first_data == {"Alice": [("Math", 80)]}
