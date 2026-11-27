import json

from src.DataReader import DataReader
from src.Types import DataType


class JsonDataReader(DataReader):
    def read(self, path: str) -> DataType:
        with open(path, encoding="utf-8") as source:
            students = json.load(source)

        if not isinstance(students, dict):
            raise ValueError(
                "Expected a JSON object mapping students to grades."
            )

        data: DataType = {}
        for student, subjects in students.items():
            if not isinstance(subjects, dict):
                raise ValueError(f"Expected a JSON object for {student!r}.")

            grades: list[tuple[str, int]] = []
            for subject, grade in subjects.items():
                if type(grade) is not int:
                    raise ValueError(
                        f"Expected an integer grade for {student!r} "
                        f"in {subject!r}."
                    )
                grades.append((subject, grade))
            data[student] = grades

        return data
