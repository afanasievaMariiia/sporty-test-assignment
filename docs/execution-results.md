# Execution Results

**Run date:** 2026-05-18 &nbsp; **App URL:** https://qae-assignment-tau.vercel.app &nbsp;
**User id:** `candidate-X0qwCNvZr4`

Defects found are documented in [`bug-reports.md`](./bug-reports.md).

## Automated test run

```
$ pytest -v
============================= test session starts ==============================
collected 7 items

tests/api/test_stake_boundaries.py::test_stake_outside_bounds_is_rejected[just-below-min]   PASSED
tests/api/test_stake_boundaries.py::test_stake_outside_bounds_is_rejected[just-above-max]   PASSED
tests/api/test_stake_boundaries.py::test_stake_inside_bounds_is_accepted[min-boundary]      PASSED
tests/api/test_stake_boundaries.py::test_stake_inside_bounds_is_accepted[just-inside-min]   PASSED
tests/api/test_stake_boundaries.py::test_stake_inside_bounds_is_accepted[just-inside-max]   PASSED
tests/api/test_stake_boundaries.py::test_stake_inside_bounds_is_accepted[max-boundary]      PASSED
tests/ui/test_place_bet_e2e.py::test_place_bet_happy_path                                   FAILED
========================= 1 failed, 6 passed in 17.20s =========================
```

## Summary

| Test | Layer | Cases | Result |
|---|---|---|---|
| TC-002 — stake boundary validation | API | 6 parametrized | **PASS** (6/6) |
| TC-001 — place single bet, happy path | UI (E2E) | 1 | **FAIL** — exposes BUG-003 (receipt payout) |

The UI failure is not a framework issue — the assertion is correct and the
application is misbehaving. See [`bug-reports.md`](./bug-reports.md) for the
defect record.
