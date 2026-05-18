# Test Plan

## 1. TC-001 Place single bet, end-to-end happy path

**Priority:** Critical

**Risk Rationale:** This is the core revenue-generating flow and the main functionality.

**Steps:**
1. Navigate to the match list.
2. For an upcoming match, click the "1" odds button (home win).
3. Verify the bet slip displays: home team vs away team, kickoff time, selected outcome "1", odds value.
4. Enter stake 5.00 in the bet slip stake field.
5. Verify potential payout displays as stake × odds.
6. Note the current balance before submitting.
7. Click "Place Bet".
8. Observe the button transitions to "Placing..." and is disabled.

**Expected Result:**
- Success receipt modal appears containing: Bet ID, match details (home v away), selection (1), stake €5.00, odds at placement, potential payout, placement timestamp.
- Account balance is reduced by exactly €5.00.
- Closing the receipt returns to the match list with no active selection.

---

## 2. TC-002 Stake boundary validation

**Priority:** Critical

**Risk Rationale:** Stake min/max limits are compliance controls (anti-money-laundering on the upper end, fee-economics on the lower end). Off-by-one errors at boundaries are one of the most common bug classes. Accepting €100.01 or €0.99 silently violates the business rule and creates audit exposure.

**Steps:** For each stake value below, attempt to place a bet and observe the outcome:

| Stake   | Expected outcome                                              |
|---------|---------------------------------------------------------------|
| 0.99    | Rejected, place bet disabled                                  |
| 1.00    | Accepted, bet places successfully (lower boundary)            |
| 1.01    | Accepted (just inside lower)                                  |
| 99.99   | Accepted (just inside upper)                                  |
| 100.00  | Accepted, bet places successfully (upper boundary)            |
| 100.01  | Rejected, place bet disabled                                  |

**Expected Result:** Values 1.00 and 100.00 (inclusive boundaries) are accepted and produce successful placements with correct balance deduction.

---

## 3. TC-003 Stake precision: reject more than 2 decimal places

**Priority:** High

**Risk Rationale:** Financial precision bugs are insidious — silent truncation or float-rounding errors compound across thousands of bets, producing audit discrepancies between displayed receipts and database records.

**Steps:**
1. Click into the stake field.
2. Type `5.123`. Observe whether the 3rd decimal is accepted, blocked, or truncated.
3. Clear the field. Paste `5.999` from clipboard. Observe.
4. Clear. Type `5.005` (precision rounding edge). Observe.
5. Clear. Type a valid value `5.12` and place the bet; inspect the receipt.

**Expected Result:**
- Typing a third decimal is blocked at the input level, OR the value is rejected on blur / on submit with a clear message ("Stake must have at most 2 decimal places").
- Pasting an over-precise value is also blocked or rejected (not silently truncated).
- A successfully placed bet of `5.12` shows exactly €5.12 on the receipt and deducts exactly €5.12 from balance — no rounding, no extra decimals.

---

## 4. TC-004 Place-bet failure recovery: error modal, Rebet, Close

**Priority:** High

**Risk Rationale:** When the backend fails transiently, the worst outcome is double-charge (user charged, no bet placed, retry charges again). This is the single most damaging class of bug in a financial flow — direct monetary harm to the customer and immediate trust damage. The Rebet contract must be idempotent.

**Preconditions:** Ability to inject a placement failure (network error or 500 response) via test hook, proxy, or API mock. Valid stake and selection.

**Steps:**
1. Select match, enter stake €10.00. Record balance B.
2. Inject a placement failure for the next call.
3. Click "Place Bet".
4. Verify error modal: title "Something went wrong", body text, buttons **Rebet** (primary) and **Close** (secondary), X in top-right.
5. **Path A — Rebet:** Remove the failure injection. Click "Rebet".
   - Verify the bet places successfully (success receipt appears).
   - Verify balance is now exactly B − €10.00 (not B − €20.00).
   - Verify only one bet exists in history.
6. **Path B (separate run) — Close:** With error modal shown, click "Close". Verify modal dismisses; selection and stake are cleared; balance is unchanged.
7. **Path C (separate run) — X:** Verify X behaves identically to Close.

**Expected Result:**
- Error modal renders with the exact spec'd title, body text, and three actions.
- Balance is never deducted while the placement is in a failed state.
- Rebet retries the same selection at the same odds (spec says odds are static for the session) and produces exactly one charged bet on success.
- Close and X both clear selection AND stake, leave balance unchanged, no bet recorded.

---

## 5. TC-006 Odds filter: invalid range rejection and boundary acceptance

**Priority:** Medium

**Risk Rationale:** Filter bugs silently hide bettable matches (revenue loss) or expose matches outside business rules (compliance). Invalid input must produce clear, recoverable feedback rather than a silent empty result that traps the user. Lower priority than money flows, but still revenue-adjacent.

**Steps:** For each input combination, apply the filter and observe:

| Min   | Max     | Expected                                                       |
|-------|---------|----------------------------------------------------------------|
| 5.00  | 2.00    | Rejected — clear message ("min must be ≤ max")                 |
| 0.50  | 10.00   | Rejected — below allowed minimum 1.01                          |
| 2.00  | 1500.00 | Rejected — above allowed maximum 1000.00                       |
| abc   | 5.00    | Rejected — non-numeric                                         |
| 1.01  | 1000.00 | Accepted — exact boundaries                                    |
| 2.00  | 2.00    | Accepted — equal min and max (single value)                    |
| empty | 5.00    | Behavior per spec clarification (assume: open lower bound)     |
| 2.00  | empty   | Behavior per spec clarification (assume: open upper bound)     |

**Expected Result:**
- Each invalid combination produces inline error feedback specifying what's wrong.
- Filter is not applied while inputs are invalid — match list remains in its last valid state, not silently emptied.
- Boundary values 1.01 and 1000.00 are accepted (inclusive per the spec).
- `min = max` is accepted as a single-value filter.
- After clearing inputs, filter resets cleanly.
