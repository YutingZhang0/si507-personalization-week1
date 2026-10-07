# Team 3 Personalization - Week 1 delivery

This folder is a runnable Week 1 proposal for the SI 507 music-market project.
It is intentionally dependency-free and can be copied into the shared repository.

## Included

- `PopularityRecommender`: required popularity top-k implementation.
- `rank_candidates`: shared deterministic ranking utility for Editorial Programming.
- `ItemKNNRecommender`: a small working item-kNN implementation. It can be used as
  the Week 1 wiring implementation, but it must still be reviewed against the
  class's agreed definition before it is reported as the final item-kNN result.
- A tiny, hand-checkable listening-history fixture.
- A proposed gatekeeper contract for Teams 4-6.
- Unit tests covering ranking, eligibility, duplicates, cold start, state
  mutation, updates, and a hand-computable similarity example.
- A demo command that consumers can run without network access.

## Run the consumer example

From this directory:

```text
python demo.py
```

Expected output:

```text
Popularity: ['track_a', 'track_b', 'track_c']
Item-kNN for user_1: ['track_d', 'track_c']
```

## Run the checks

```text
python -m unittest discover -s tests -v
```

All tests should report `ok`.

## Proposed public interface

Both recommenders expose the same three operations:

```python
model.initialize(interactions)
model.get_candidates(listener_id, available_track_ids, k)
model.update_history(interactions)
```

`get_candidates` returns an ordered list of `Candidate` values. Each candidate
contains a `track_id` and a recommender score. The recommender score is not a
listener choice probability.

See `contracts/gatekeeper_contract_proposal.md` for meanings, failure behavior,
time conventions, open decisions, and consumer acceptance checks.

## Important status note

This package is a proposal, not evidence that Teams 4-6 have accepted the
contract. Before merging, the team should copy or adapt the proposal into the
shared repository, open a cross-team issue, and record the consumers' actual
results.
