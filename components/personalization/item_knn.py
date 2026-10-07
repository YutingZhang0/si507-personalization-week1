"""Small item-based collaborative-filtering implementation."""

from collections import Counter, defaultdict
from collections.abc import Iterable
from math import sqrt

from .models import Candidate, Interaction
from .ranking import rank_candidates


class ItemKNNRecommender:
    """Recommend items with listener-overlap similar to a user's history.

    Similarity is binary cosine similarity over listener sets. Candidate scores
    sum similarities to all distinct items in the target listener's history.
    Unknown listeners fall back to global popularity. Repeat items are excluded
    by default but may be enabled explicitly.
    """

    def __init__(self, neighbor_count: int = 20, allow_repeats: bool = False) -> None:
        if neighbor_count <= 0:
            raise ValueError("neighbor_count must be positive")
        self.neighbor_count = neighbor_count
        self.allow_repeats = allow_repeats
        self._user_items: dict[str, set[str]] = defaultdict(set)
        self._item_users: dict[str, set[str]] = defaultdict(set)
        self._play_counts: Counter[str] = Counter()
        self._initialized = False

    def initialize(self, interactions: Iterable[Interaction]) -> None:
        """Replace indexes with the supplied history."""

        self._user_items = defaultdict(set)
        self._item_users = defaultdict(set)
        self._play_counts = Counter()
        self._apply(interactions)
        self._initialized = True

    def get_candidates(
        self,
        listener_id: str,
        available_track_ids: Iterable[str],
        k: int,
    ) -> list[Candidate]:
        """Return eligible item-kNN candidates without mutating model state."""

        self._require_initialized()
        if not listener_id:
            raise ValueError("listener_id must be non-empty")
        if k < 0:
            raise ValueError("k must be non-negative")

        available = set(available_track_ids)
        listened = self._user_items.get(listener_id, set())
        if not self.allow_repeats:
            available.difference_update(listened)

        if not listened:
            return rank_candidates(self._play_counts, available, k)

        scores: Counter[str] = Counter()
        for source_track in listened:
            neighbors = []
            for candidate_track in available:
                if candidate_track == source_track:
                    continue
                similarity = self._cosine_similarity(source_track, candidate_track)
                if similarity > 0:
                    neighbors.append((candidate_track, similarity))

            neighbors.sort(key=lambda pair: (-pair[1], pair[0]))
            for candidate_track, similarity in neighbors[: self.neighbor_count]:
                scores[candidate_track] += similarity

        # Zero-similarity tracks remain valid opportunities and give predictable
        # short-list behavior when fewer than k positive-score items exist.
        return rank_candidates(scores, available, k)

    def update_history(self, interactions: Iterable[Interaction]) -> None:
        """Update indexes immediately for subsequent recommendation calls."""

        self._require_initialized()
        self._apply(interactions)

    def _apply(self, interactions: Iterable[Interaction]) -> None:
        for event in interactions:
            self._play_counts[event.track_id] += 1
            self._user_items[event.listener_id].add(event.track_id)
            self._item_users[event.track_id].add(event.listener_id)

    def _cosine_similarity(self, left_track: str, right_track: str) -> float:
        left_users = self._item_users.get(left_track, set())
        right_users = self._item_users.get(right_track, set())
        if not left_users or not right_users:
            return 0.0
        overlap = len(left_users & right_users)
        return overlap / sqrt(len(left_users) * len(right_users))

    def _require_initialized(self) -> None:
        if not self._initialized:
            raise RuntimeError("initialize must be called before using the model")

