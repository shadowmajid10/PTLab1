import json
from pathlib import Path

import pytest

from src.DataReader import DataReader
from src.JsonDataReader import JsonDataReader
from src.Types import DataType


@pytest.fixture
def json_path(tmp_path: Path) -> Path:
    return tmp_path / "students.json"


def test_inherits_from_data_reader() -> None:
    assert issubclass(JsonDataReader, DataReader)


def test_converts_multiple_students_with_cyrillic_names(
    json_path: Path,
) -> None:
    json_path.write_text(
        '{"Иван": {"математика": 0, "история": 100}, "Анна": {"химия": 80}}',
        encoding="utf-8",
    )
    assert JsonDataReader().read(str(json_path)) == {
        "Иван": [("математика", 0), ("история", 100)],
        "Анна": [("химия", 80)],
    }


@pytest.mark.parametrize("content, expected", [
    ("{}", {}),
    ('{"Иван": {}}', {"Иван": []}),
])
def test_reads_empty_objects(
    json_path: Path, content: str, expected: DataType,
) -> None:
    json_path.write_text(content, encoding="utf-8")
    assert JsonDataReader().read(str(json_path)) == expected


def test_repeated_reads_only_return_current_data(json_path: Path) -> None:
    reader = JsonDataReader()
    json_path.write_text('{"Alice": {"Math": 80}}', encoding="utf-8")
    first = reader.read(str(json_path))
    json_path.write_text('{"Bob": {"Art": 90}}', encoding="utf-8")
    assert reader.read(str(json_path)) == {"Bob": [("Art", 90)]}
    assert first == {"Alice": [("Math", 80)]}


def test_missing_file_raises_file_not_found(json_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        JsonDataReader().read(str(json_path))


def test_malformed_json_raises_decode_error(json_path: Path) -> None:
    json_path.write_text('{"Alice":', encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        JsonDataReader().read(str(json_path))


@pytest.mark.parametrize("value", [[], None, "Alice", 12])
def test_rejects_non_object_roots(json_path: Path, value: object) -> None:
    json_path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="mapping students to grades"):
        JsonDataReader().read(str(json_path))


@pytest.mark.parametrize("subjects", [[], None, "Math", 80])
def test_rejects_non_object_subjects(
    json_path: Path, subjects: object,
) -> None:
    json_path.write_text(json.dumps({"Alice": subjects}), encoding="utf-8")
    with pytest.raises(ValueError, match="JSON object for 'Alice'"):
        JsonDataReader().read(str(json_path))


@pytest.mark.parametrize("grade", [True, False, 80.0, "80", None, [], {}])
def test_rejects_non_integer_grades(json_path: Path, grade: object) -> None:
    content = json.dumps({"Alice": {"Math": grade}})
    json_path.write_text(content, encoding="utf-8")
    message = "integer grade for 'Alice' in 'Math'"
    with pytest.raises(ValueError, match=message):
        JsonDataReader().read(str(json_path))
