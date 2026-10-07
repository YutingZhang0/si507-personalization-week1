import unittest

from components.personalization import (
    Interaction,
    ItemKNNRecommender,
    PopularityRecommender,
    rank_candidates,
)


def event(listener_id: str, track_id: str, minute: int) -> Interaction:
    return Interaction(listener_id, track_id, f"2026-09-01T10:{minute:02d}:00Z")


TINY_HISTORY = [
    event("user_1", "track_a", 0),
    event("user_1", "track_b", 1),
    event("user_2", "track_a", 2),
    event("user_2", "track_b", 3),
    event("user_2", "track_d", 4),
    event("user_3", "track_a", 5),
    event("user_3", "track_c", 6),
    event("user_3", "track_d", 7),
    event("user_4", "track_b", 8),
    event("user_4", "track_c", 9),
    event("user_4", "track_e", 10),
]


class RankingTests(unittest.TestCase):
    def test_ranking_is_unique_eligible_and_deterministic(self) -> None:
        result = rank_candidates(
            {"track_a": 2, "track_b": 2, "hidden": 99},
            ["track_b", "track_a", "track_b", "track_c"],
            3,
        )
        self.assertEqual(
            [candidate.track_id for candidate in result],
            ["track_a", "track_b", "track_c"],
        )

    def test_negative_k_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            rank_candidates({}, [], -1)


class PopularityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model = PopularityRecommender()
        self.model.initialize(TINY_HISTORY)

    def test_popularity_top_k(self) -> None:
        result = self.model.get_candidates(
            "new_user", ["track_a", "track_b", "track_c", "track_d"], 3
        )
        self.assertEqual(
            [candidate.track_id for candidate in result],
            ["track_a", "track_b", "track_c"],
        )

    def test_unavailable_tracks_are_never_returned(self) -> None:
        result = self.model.get_candidates("user_1", ["track_d"], 5)
        self.assertEqual([candidate.track_id for candidate in result], ["track_d"])

    def test_query_does_not_mutate_state(self) -> None:
        before = self.model.get_candidates("user_1", ["track_a", "track_b"], 2)
        self.model.get_candidates("someone_else", ["track_b"], 1)
        after = self.model.get_candidates("user_1", ["track_a", "track_b"], 2)
        self.assertEqual(before, after)

    def test_history_update_becomes_visible(self) -> None:
        self.model.update_history([event("user_5", "track_e", 20)] * 5)
        result = self.model.get_candidates("user_1", ["track_a", "track_e"], 1)
        self.assertEqual(result[0].track_id, "track_e")


class ItemKNNTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model = ItemKNNRecommender(neighbor_count=3)
        self.model.initialize(TINY_HISTORY)

    def test_hand_computable_recommendation(self) -> None:
        result = self.model.get_candidates(
            "user_1",
            ["track_a", "track_b", "track_c", "track_d", "track_e"],
            2,
        )
        self.assertEqual(
            [candidate.track_id for candidate in result],
            ["track_d", "track_c"],
        )
        self.assertGreater(result[0].score, result[1].score)

    def test_repeat_items_are_excluded_by_default(self) -> None:
        result = self.model.get_candidates(
            "user_1", ["track_a", "track_b", "track_d"], 3
        )
        self.assertEqual([candidate.track_id for candidate in result], ["track_d"])

    def test_unknown_listener_uses_popularity_fallback(self) -> None:
        result = self.model.get_candidates(
            "new_user", ["track_a", "track_b", "track_c"], 2
        )
        self.assertEqual(
            [candidate.track_id for candidate in result],
            ["track_a", "track_b"],
        )

    def test_query_does_not_mutate_state(self) -> None:
        before = self.model.get_candidates("user_1", ["track_c", "track_d"], 2)
        self.model.get_candidates("user_2", ["track_c", "track_e"], 2)
        after = self.model.get_candidates("user_1", ["track_c", "track_d"], 2)
        self.assertEqual(before, after)

    def test_update_changes_similarity_index(self) -> None:
        before = self.model.get_candidates("user_1", ["track_c", "track_e"], 2)
        self.model.update_history(
            [event("user_1", "track_c", 30), event("user_2", "track_e", 31)]
        )
        after = self.model.get_candidates("user_1", ["track_c", "track_e"], 2)
        self.assertNotEqual(before, after)


if __name__ == "__main__":
    unittest.main()
