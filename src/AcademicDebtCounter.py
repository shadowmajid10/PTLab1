from src.Types import DataType


class AcademicDebtCounter:
    def __init__(self, data: DataType) -> None:
        self.data = data

    def count(self) -> int:
        return sum(
            1 for grades in self.data.values()
            if any(grade < 61 for _, grade in grades)
        )
