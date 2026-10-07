"""Shared deterministic ranking behavior."""

from collections.abc import Iterable, Mapping

from .models import Candidate


def rank_candidates(
    scores: Mapping[str, float],
    eligible_track_ids: Iterable[str],
    k: int,
) -> list[Candidate]:
    """Return at most `k` unique eligible tracks ordered by score.

    Higher scores rank first. Ties are broken by ascending track ID so repeated
    runs are deterministic. Eligible tracks missing from `scores` receive 0.0.
    Duplicate IDs in `eligible_track_ids` are collapsed.
    """

    if k < 0:
        raise ValueError("k must be non-negative")

    unique_eligible = set(eligible_track_ids)
    if any(not track_id for track_id in unique_eligible):
        raise ValueError("eligible track IDs must be non-empty strings")

    ordered = sorted(
        unique_eligible,
        key=lambda track_id: (-float(scores.get(track_id, 0.0)), track_id),
    )
    return [
        Candidate(track_id=track_id, score=float(scores.get(track_id, 0.0)))
        for track_id in ordered[:k]
    ]

