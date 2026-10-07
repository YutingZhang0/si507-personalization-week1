"""Small shared value objects for the proposed recommender contract."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Interaction:
    """One observed or simulated play supplied to the recommender.

    `timestamp` is an ISO-8601 string. The Week 1 implementations count events
    but do not otherwise use time. Keeping the field now prevents the fixture
    from hiding the time convention needed by later history-window work.
    """

    listener_id: str
    track_id: str
    timestamp: str

    def __post_init__(self) -> None:
        if not self.listener_id:
            raise ValueError("listener_id must be non-empty")
        if not self.track_id:
            raise ValueError("track_id must be non-empty")
        if not self.timestamp:
            raise ValueError("timestamp must be non-empty")


@dataclass(frozen=True)
class Candidate:
    """A ranked opportunity produced by a recommender.

    `score` is meaningful only within one recommender call. It is not a
    probability that a listener will play the track.
    """

    track_id: str
    score: float

