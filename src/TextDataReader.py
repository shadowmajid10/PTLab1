from src.DataReader import DataReader
from src.Types import DataType


class TextDataReader(DataReader):
    def read(self, path: str) -> DataType:
        data: DataType = {}
        grades: list[tuple[str, int]] | None = None

        with open(path, encoding="utf-8") as source:
            for line in source:
                content = line.strip()
                if not content:
                    continue

                if not line[0].isspace():
                    grades = data.setdefault(content, [])
                    continue

                if grades is None:
                    raise ValueError("A grade must follow a student name.")

                subject, score = content.split(":", 1)
                grades.append((subject.strip(), int(score)))

        return data
