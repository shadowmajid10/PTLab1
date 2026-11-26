import argparse
import sys

from src.CalcRating import CalcRating
from src.TextDataReader import TextDataReader


def get_path_from_arguments() -> str:
    parser = argparse.ArgumentParser(description="Calculate student ratings.")
    parser.add_argument(
        "-p", required=True, help="Path to the student data file"
    )
    return parser.parse_args().p


def main() -> None:
    path = get_path_from_arguments()
    data = TextDataReader().read(path)
    ratings = CalcRating(data).calc()
    for student, rating in ratings.items():
        print(f"{student}: {rating:.2f}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
