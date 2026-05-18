# Bug Reports

## BUG-001 — Account balance does not update after successful bet placement

Severity: Critical

Reproduction Steps:

1. Log in as a user with the default starting balance €125.50.
2. Select an upcoming match, click "1" odds (e.g., 2.50).
3. Enter stake 10.00 and click "Place Bet".
4. Wait for the success receipt, then close it.
5. Observe the balance in the header.

Expected vs Actual:

- Expected: balance shows €115.50 (€125.50 − €10.00).
- Actual: balance still shows €125.50. Refreshing the page corrects it to €115.50.

Business Impact: Users see stale balances, may attempt bets they can't afford, and lose trust in the platform's financial accuracy.

Evidence: Network HAR shows the place-bet response returns the updated balance, but the UI header continues to render the pre-bet value until a manual page refresh.

---

## BUG-002 — Odds filter does not apply: match list remains unfiltered

Severity: High

Reproduction Steps:

1. Navigate to the match list (containing matches with odds across a wide range).
2. Open the odds filter.
3. Set Min = 2.00, Max = 5.00 and Apply.
4. Observe the match list.

Expected vs Actual:

- Expected: only matches with at least one odds value in [2.00, 5.00] are displayed.
- Actual: full unfiltered list remains; matches with odds 1.00 and 10.00 are still shown. No error message.

Business Impact: Users cannot narrow matches to their preferred odds range, harming bet discovery and reducing placement volume.

Evidence: Screenshots of filter inputs (Min=2.00, Max=5.00) and match list before/after Apply (identical). Network tab note: filter request either not fired or response ignored.

---

## BUG-003 — Potential payout on success receipt differs from bet slip

Severity: Critical

Reproduction Steps:

1. Select a match with "1" odds = 2.50 and enter stake 10.00.
2. Note the bet-slip potential payout: €25.00.
3. Click "Place Bet" and wait for the success receipt.
4. Read the "Potential Payout" field on the receipt.

Expected vs Actual:

- Expected: €25.00 (stake × odds = 10.00 × 2.50).
- Actual: €15.00 — receipt shows profit only (stake × odds − stake) instead of total return. Confirmed across multiple stake/odds combinations.

Business Impact: Customers see conflicting payout figures at the point of transaction, triggering support tickets, financial disputes, and regulatory complaint risk.

Evidence: Side-by-side screenshots of bet slip (€25.00) and receipt (€15.00) for the same bet. Repeats with stake €20.00 @ 1.50 (slip €30.00, receipt €10.00). Recommend verifying backend stored payout to rule out settlement bug.
