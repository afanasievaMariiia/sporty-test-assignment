# Strategy & Recommendations

## Why these two tests, and why these layers

**TC-001 — Place a single bet (UI, E2E).** This is the only test that proves the
*full* revenue chain end-to-end: match list → bet slip → place-bet API → balance
update → success receipt. Any one of those links can break in a way the others
cannot see (the receipt can render wrong values even when the API is correct;
the balance can go stale even when the bet succeeded — see
[`bug-reports.md`](./bug-reports.md) BUG-001 and BUG-003 for both classes
in the wild). A browser-driven test is the only layer where the whole chain is
observable as a user observes it, and that is what makes it worth the cost.
We run exactly one such test — the happy path — because UI tests are
expensive and flaky relative to what they assert. Everything else, we push down.

**TC-002 — Stake boundaries (API).** Stake min/max are *server-enforced*
business rules. Putting them in the UI would be a category mistake: the UI is
a convenience for the user, but the API is the source of truth that protects
the business (anti-money-laundering at the top, fee economics at the bottom).
If the UI silently allowed €100.01, the API would still reject it; if the
*API* allowed it, every client (web, mobile, partner) would leak. Testing at
the API layer is also ~30× faster, trivially parametrizable, and far less
flaky. Six parametrized cases (0.99, 1.00, 1.01, 99.99, 100.00, 100.01) run
in under a second.

## Why the other scenarios stay manual (for now)

- **TC-003 — Stake precision (3+ decimal places).** Largely an input-mask
  test. Cheap to automate later, but lower marginal value than the two we
  picked, and the spec is ambiguous on the *exact* behaviour (input-level
  block vs. on-blur rejection vs. on-submit rejection). Worth one round of
  spec clarification before encoding expected values into assertions —
  otherwise the test flaps every time the UX shifts which "rejection" point
  is enforced.
- **TC-004 — Place-bet failure recovery (Rebet / Close).** Requires the
  ability to inject a placement failure (transient 500 or network drop). The
  live environment has no test hook, mock server, or proxy in place to do
  this; the infrastructure cost (record-and-replay proxy, WireMock-style
  stub, or backend feature flag) exceeds the cost of doing the manual run.
  This is the *first* test to automate the moment failure-injection becomes
  available, because it guards the single most damaging class of bug in a
  financial flow (double-charge on retry).
- **TC-006 — Odds filter validation.** Manual QA already confirmed the
  filter does not apply at all (BUG-002). Until the feature works, automating
  its edge cases is premature — we would be locking in the wrong expected
  behaviour. Re-evaluate the moment BUG-002 is fixed.

## Top recommendations to scale

1. **Make the test data layer controllable.** Today the entire suite shares a
   single `candidate-X0qwCNvZr4` account, and `/api/reset-balance` does not
   actually restore €125.50 — the swagger even documents the discrepancy as a
   feature ("response payload may differ from persisted balance"). Two
   concrete fixes that compound: (a) per-test user-id minting (cheap on the
   server, restores isolation between runs and between developers), (b) make
   `reset-balance` honour its own contract. Without these, anything that
   depends on a known starting balance either flakes, or has to encode
   "read-then-compare-against-returned" gymnastics like TC-002 does today.

2. **Wire the suite into CI on GitHub Actions.** Two jobs per PR:
   `pytest -m api` on every push (fast, reliable, gates the merge),
   `pytest -m ui` on a separate job with up-to-2 retries and a
   screenshot-on-failure artefact. Add a nightly cron that runs the full
   suite against staging and posts a Slack notification on failure. The
   current marker scheme (`api`, `ui`, `smoke`) is already designed for this
   — it is a config exercise, not a refactor.

3. **Adopt a thin API contract layer.** The app already publishes an OpenAPI
   spec at `/api/docs`. Generate a typed client from it and run it as a
   schema-validation pass in CI, so request/response shapes cannot drift
   silently. This catches the same class of issue that today only surfaces
   through the UI run.

*Lower priority but worth flagging once the above are in place: visual
regression snapshots on the receipt modal, accessibility checks (`axe-core`)
on the match list, and a small set of stake-formatting fuzz cases —
`1`, `1.0`, `1.000`, scientific notation — to back-fill TC-003 once the
spec is clarified.*
