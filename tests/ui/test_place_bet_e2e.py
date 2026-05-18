"""TC-001 — Place single bet, end-to-end happy path.

WHY THIS TEST: this is the core revenue-generating user journey of the product.
If users cannot place a bet, nothing else matters. The flow touches every layer
visible to the user — match list, bet slip, balance, place-bet API, success
receipt — and a regression anywhere in that chain blocks the whole funnel.
That is why it is automated at the UI layer (the only layer that proves the
chain end-to-end) and why it is the only UI test we run on every commit.
"""
from __future__ import annotations

import pytest

from framework.api.client import BettingApiClient
from framework.ui.pages.bet_receipt import BetReceipt
from framework.ui.pages.bet_slip import BetSlip
from framework.ui.pages.header import Header
from framework.ui.pages.match_list_page import MatchListPage

STAKE = "5.00"
STAKE_VALUE = 5.00


@pytest.mark.ui
@pytest.mark.smoke
def test_place_bet_happy_path(
    reset_balance,
    api_client: BettingApiClient,
    match_list_page: MatchListPage,
    header: Header,
    bet_slip: BetSlip,
    bet_receipt: BetReceipt,
) -> None:
    # 1. Pick the first UPCOMING match — order matches the API contract
    #    ("home" team always listed first).
    match = match_list_page.first_upcoming_card()

    # 2. Snapshot the balance BEFORE we place the bet. We use the API rather
    #    than the UI here because the UI balance pill is what we want to
    #    *verify*, not rely on for our own baseline.
    balance_before = api_client.get_balance().body["balance"]

    # 3. Click the "1" (home win) odds button on that match.
    match_list_page.click_home_odds(match.match_id)
    bet_slip.wait_until_selection_visible()

    # 4. Bet slip must reflect the user's selection.
    assert bet_slip.teams_text() == f"{match.home_team} vs {match.away_team}", (
        "Bet slip team order should match the home/away convention from the match list"
    )
    assert "Home" in bet_slip.market_text(), (
        f"Expected 'Home' market label for the '1' selection, got: {bet_slip.market_text()!r}"
    )
    assert bet_slip.odds_value() == pytest.approx(match.odds_home), (
        "Bet slip odds must match the odds shown on the match card at click time"
    )

    # 5. Enter a €5 stake and verify potential payout = stake × odds.
    bet_slip.enter_stake(STAKE)
    expected_payout = round(STAKE_VALUE * match.odds_home, 2)
    assert bet_slip.potential_payout() == pytest.approx(expected_payout), (
        f"Potential payout should be stake × odds "
        f"({STAKE_VALUE} × {match.odds_home} = {expected_payout})"
    )
    assert bet_slip.is_place_bet_enabled(), "Place Bet should be enabled with a valid stake"

    # 6. Place the bet.
    bet_slip.click_place_bet()

    # 7. Receipt modal — must be internally consistent with what was shown.
    receipt = bet_receipt.snapshot()
    assert receipt.bet_id, "Bet receipt must include a non-empty bet id"
    assert receipt.match == f"{match.home_team} vs {match.away_team}", (
        f"Receipt match string must preserve home/away order, got: {receipt.match!r}"
    )
    assert receipt.stake == pytest.approx(STAKE_VALUE)
    assert receipt.odds == pytest.approx(match.odds_home)
    assert receipt.payout == pytest.approx(expected_payout), (
        f"Receipt payout must equal stake × odds ({expected_payout})"
    )
    assert receipt.placed_at, "Receipt must include a placement timestamp"

    # 8. Balance must be reduced by exactly the stake.
    balance_after = api_client.get_balance().body["balance"]
    assert balance_after == pytest.approx(balance_before - STAKE_VALUE, abs=0.01), (
        f"Balance should decrease by exactly €{STAKE_VALUE} "
        f"(before={balance_before}, after={balance_after})"
    )

    # 9. Closing the receipt clears the slip and returns to the match list.
    bet_receipt.close()
    assert bet_slip.is_empty(), "Closing the receipt should clear the active selection"
    ui_balance = header.balance()
    assert ui_balance == pytest.approx(balance_after, abs=0.01), (
        f"Header balance pill ({ui_balance}) should match API balance ({balance_after})"
    )
