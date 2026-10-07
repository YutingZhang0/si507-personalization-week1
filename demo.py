"""Executable Week 1 consumer example."""

import csv
from pathlib import Path

from components.personalization import (
    Interaction,
    ItemKNNRecommender,
    PopularityRecommender,
)


def load_fixture() -> list[Interaction]:
    fixture_path = Path(__file__).parent / "fixtures" / "tiny_history.csv"
    with fixture_path.open(newline="", encoding="utf-8") as stream:
        return [Interaction(**row) for row in csv.DictReader(stream)]


def main() -> None:
    history = load_fixture()
    catalog = ["track_a", "track_b", "track_c", "track_d", "track_e"]

    popularity = PopularityRecommender()
    popularity.initialize(history)
    popular = popularity.get_candidates("new_user", catalog, 3)

    item_knn = ItemKNNRecommender(neighbor_count=3)
    item_knn.initialize(history)
    personalized = item_knn.get_candidates("user_1", catalog, 2)

    print("Popularity:", [candidate.track_id for candidate in popular])
    print("Item-kNN for user_1:", [candidate.track_id for candidate in personalized])


if __name__ == "__main__":
    main()

