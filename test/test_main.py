import subprocess
import sys
from pathlib import Path

import pytest

from src.main import get_path_from_arguments, main


@pytest.fixture
def sample_data(tmp_path: Path) -> Path:
    path = tmp_path / "student grades.txt"
    path.write_text(
        "Иван Иванов\n    математика:80\n    история:85\n"
        "Анна Смирнова\n    литература:91\n",
        encoding="utf-8",
    )
    return path


def test_parses_input_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["main", "-p", "student grades.txt"])
    assert get_path_from_arguments() == "student grades.txt"


def test_missing_required_path_exits(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "argv", ["main"])
    with pytest.raises(SystemExit) as error:
        get_path_from_arguments()
    assert error.value.code == 2
    assert "-p" in capsys.readouterr().err


@pytest.mark.parametrize("arguments", [["-p"], ["-p", "data.txt", "--bad"]])
def test_invalid_arguments_exit(
    monkeypatch: pytest.MonkeyPatch, arguments: list[str],
) -> None:
    monkeypatch.setattr(sys, "argv", ["main", *arguments])
    with pytest.raises(SystemExit) as error:
        get_path_from_arguments()
    assert error.value.code == 2


def test_main_prints_cyrillic_ratings_to_two_decimal_places(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
    sample_data: Path,
) -> None:
    monkeypatch.setattr(sys, "argv", ["main", "-p", str(sample_data)])
    main()
    captured = capsys.readouterr()
    assert captured.out == (
        "Иван Иванов: 82.50\nАнна Смирнова: 91.00\n"
        "Количество студентов с академическими задолженностями: 0\n"
    )
    assert captured.err == ""


def test_module_execution_writes_utf8_to_captured_output(
    sample_data: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PYTHONIOENCODING", "ascii")
    result = subprocess.run(
        [sys.executable, "-m", "src.main", "-p", str(sample_data)],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        encoding="utf-8",
        check=True,
    )
    assert result.stdout == (
        "Иван Иванов: 82.50\nАнна Смирнова: 91.00\n"
        "Количество студентов с академическими задолженностями: 0\n"
    )
    assert result.stderr == ""


@pytest.mark.parametrize("extension", [".json", ".JSON"])
def test_module_reads_json_input(tmp_path: Path, extension: str) -> None:
    path = tmp_path / f"students{extension}"
    path.write_text('{"Иван": {"математика": 80}}', encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "src.main", "-p", str(path)],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        encoding="utf-8",
        check=True,
    )
    assert result.stdout == (
        "Иван: 80.00\n"
        "Количество студентов с академическими задолженностями: 0\n"
    )
    assert result.stderr == ""


def test_sample_txt_and_json_produce_equivalent_ratings(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    data_dir = Path(__file__).resolve().parents[1] / "data"
    txt_path = data_dir / "data.txt"
    json_path = data_dir / "data.json"
    monkeypatch.setattr(sys, "argv", ["main", "-p", str(txt_path)])
    main()
    txt_output = capsys.readouterr().out
    monkeypatch.setattr(sys, "argv", ["main", "-p", str(json_path)])
    main()
    txt_lines = txt_output.splitlines()
    assert len(txt_lines) == 5
    assert txt_lines[-1] == (
        "Количество студентов с академическими задолженностями: 0"
    )
    assert capsys.readouterr().out == txt_output


@pytest.mark.parametrize("path", ["data.csv", "grades"])
def test_unsupported_extension_exits_with_message(
    monkeypatch: pytest.MonkeyPatch, path: str,
) -> None:
    monkeypatch.setattr(sys, "argv", ["main", "-p", path])
    with pytest.raises(SystemExit, match="Unsupported file extension"):
        main()


def test_main_prints_cyrillic_debt_summary_after_ratings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "students.txt"
    path.write_text(
        "Анна\n    математика:40\n    история:50\nИван\n    литература:61\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(sys, "argv", ["main", "-p", str(path)])
    main()
    captured = capsys.readouterr()
    assert captured.out == (
        "Анна: 45.00\nИван: 61.00\n"
        "Количество студентов с академическими задолженностями: 1\n"
    )
    assert captured.err == ""


def test_main_prints_zero_debt_count_without_failing_grades(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "students.json"
    path.write_text(
        '{"Иван": {"математика": 61}, "Анна": {}}', encoding="utf-8"
    )
    monkeypatch.setattr(sys, "argv", ["main", "-p", str(path)])
    main()
    captured = capsys.readouterr()
    assert captured.out == (
        "Иван: 61.00\nАнна: 0.00\n"
        "Количество студентов с академическими задолженностями: 0\n"
    )
    assert captured.err == ""


def test_demo_txt_and_json_report_the_same_debt_count(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    data_dir = Path(__file__).resolve().parents[1] / "data"
    txt_path = data_dir / "academic_debt.txt"
    json_path = data_dir / "academic_debt.json"
    monkeypatch.setattr(sys, "argv", ["main", "-p", str(txt_path)])
    main()
    txt_summary = capsys.readouterr().out.splitlines()[-1]
    monkeypatch.setattr(sys, "argv", ["main", "-p", str(json_path)])
    main()
    json_summary = capsys.readouterr().out.splitlines()[-1]
    assert txt_summary == (
        "Количество студентов с академическими задолженностями: 2"
    )
    assert json_summary == txt_summary
