from src.Types import DataType, RatingType


class CalcRating:
    def __init__(self, data: DataType) -> None:
        self.data = data

    def calc(self) -> RatingType:
        ratings: RatingType = {}
        for student, grades in self.data.items():
            ratings[student] = (
                sum(score for _, score in grades) / len(grades)
                if grades else 0.0
            )
        return ratings
