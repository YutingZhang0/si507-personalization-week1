# Proposed gatekeeper contract - Team 3 Personalization

Status: **proposal for discussion; not yet accepted by Teams 4-6**

Owners and consumers:

- Producer: Team 3 Personalization
- Shared ranking consumer: Team 4 Editorial Programming
- Candidate consumers: Team 5 Audience Modeling and Team 6 Simulation Infrastructure

## Proposed behaviors

1. A recommender returns at most `k` unique candidates drawn only from the
   supplied `available_track_ids`.
2. Candidates are ordered by descending recommender score. Ties are broken by
   ascending track ID for deterministic replays.
3. Candidate scores are ranking evidence, not listener choice probabilities.
   The recommender does not select the final play or rejection.
4. `get_candidates` does not modify recommender or listener state.
5. New observations enter only through `update_history`; in this proposal they
   become visible to the next request. Simulation Infrastructure must confirm
   whether it calls updates at the end of each global step or on another
   documented schedule.

## Proposed request

```python
get_candidates(
    listener_id: str,
    available_track_ids: Iterable[str],
    k: int,
) -> list[Candidate]
```

- `listener_id`: stable, non-empty listener identifier.
- `available_track_ids`: tracks eligible at the start of the request. The
  recommender may not return any other track.
- `k`: maximum number of candidates requested; must be non-negative.

## Proposed response

```python
@dataclass(frozen=True)
class Candidate:
    track_id: str
    score: float
```

- The list is ordered and contains no duplicate track IDs.
- Fewer than `k` candidates are valid when fewer than `k` eligible tracks
  remain after applying the repeat policy.
- Scores are not required to sum to one and are not comparable between
  different algorithms.

## Initialization and history updates

```python
initialize(interactions: Iterable[Interaction]) -> None
update_history(interactions: Iterable[Interaction]) -> None
```

`Interaction` contains `listener_id`, `track_id`, and an ISO-8601 UTC timestamp.
Each row is one completed play. Repeated rows count as repeated plays for
popularity. Item-kNN similarity uses binary listener-item membership in this
proposal, so repeated plays do not add additional similarity weight.

The current implementation uses immediate visibility after `update_history`.
For a frozen experiment, the engine should not call `update_history` until the
declared refresh point. A later revision may expose an explicit buffered update
or refresh operation if Team 6 needs it.

## Current policies

- Popularity score: number of supplied play events for the track.
- Item similarity: cosine similarity over the sets of listeners who played the
  two tracks.
- Personalized score: sum of similarities between the candidate and distinct
  tracks in the listener's history.
- Repeat policy: exclude already-listened tracks by default.
- Cold-start listener: fall back to global popularity.
- Cold-start item: eligible but receives zero similarity until observations
  connect it to other items.
- Unknown eligible track: allowed with score zero.
- Missing catalog item: not returned unless it appears in
  `available_track_ids`; missing does not mean a known zero-play item.

## Errors

- Calling a recommender before `initialize`: `RuntimeError`.
- Empty listener ID, empty track ID, or empty timestamp: `ValueError`.
- Negative `k`: `ValueError`.
- `k == 0`: empty list.

## State ownership

The recommender owns only its indexes and counts. It must not inspect private
simulated preferences, choose a play, mutate listener state, or write to the
event log. Team 5 owns listener choice. Team 6 coordinates step timing, applies
global updates, and records exposures and events.

## Tiny consumer check

From `personalization_week1_delivery/` run:

```text
python demo.py
```

Expected result:

```text
Popularity: ['track_a', 'track_b', 'track_c']
Item-kNN for user_1: ['track_d', 'track_c']
```

Each consumer should reply with its department prefix, the command it ran, and
the actual result or a reproducible failure.

## Decisions requested from Teams 4-6

1. Is a `Candidate` object acceptable, or must the boundary use dictionaries,
   tuples, or track IDs only?
2. Should model name/version be returned with every response or recorded by the
   engine beside the exposure event?
3. Does the engine require a `step_id` or request timestamp?
4. At what exact point in a simulation step do history updates become visible?
5. Should repeat-item policy be passed per request or fixed in configuration?
6. Should zero-score candidates be returned when fewer than `k` positive-score
   candidates exist?
7. Are unknown listener IDs valid cold-start requests or errors?
8. Does Editorial Programming need `rank_candidates` to accept metadata in
   addition to numeric scores?
