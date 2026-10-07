"""Required global popularity top-k recommender."""

from collections import Counter
from collections.abc import Iterable

from .models import Candidate, Interaction
from .ranking import rank_candidates


class PopularityRecommender:
    """Rank eligible tracks by observed play count."""

    def __init__(self) -> None:
        self._play_counts: Counter[str] = Counter()
        self._initialized = False

    def initialize(self, interactions: Iterable[Interaction]) -> None:
        """Replace model state with counts from `interactions`."""

        self._play_counts = Counter(event.track_id for event in interactions)
        self._initialized = True

    def get_candidates(
        self,
        listener_id: str,
        available_track_ids: Iterable[str],
        k: int,
    ) -> list[Candidate]:
        """Return global popularity candidates without mutating model state."""

        self._require_initialized()
        if not listener_id:
            raise ValueError("listener_id must be non-empty")
        return rank_candidates(self._play_counts, available_track_ids, k)

    def update_history(self, interactions: Iterable[Interaction]) -> None:
        """Make new plays visible to subsequent calls immediately."""

        self._require_initialized()
        self._play_counts.update(event.track_id for event in interactions)

    def _require_initialized(self) -> None:
        if not self._initialized:
            raise RuntimeError("initialize must be called before using the model")

