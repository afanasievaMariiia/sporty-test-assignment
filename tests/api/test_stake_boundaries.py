"""TC-002 — Stake boundary validation.

WHY THIS TEST AT THE API LAYER (not UI):

Stake min/max are *business rules* enforced by the server: anti-money-laundering
on the upper end, fee economics on the lower end. The UI is a convenience —
the API is the source of truth. If a UI bug silently allows €100.01, the
server rule still protects the business; if the *server* allows €100.01, every
client (web, mobile, partner) is exposed. Testing the contract directly is
also far cheaper and faster: six parametrized cases run in under a second,
versus minutes through a browser, so it's a natural fit for every CI run.

Note on test isolation: the live environment does not provide truly fresh
test accounts (only one assigned user-id is valid, and `/api/reset-balance`
is documented as possibly diverging from persisted state). To stay robust we
read the balance *before* each accepted bet and compare against the API's
returned `balance` field — so the test does not assume a fixed starting amount.
"""
from __future__ import annotations

import pytest

from framework.api.client import SELECTION_HOME, BettingApiClient


@pytest.fixture(scope="module")
def match_id(config) -> str:
    """Pick a match id once per module — keeps the test resilient to API data
    changes without coupling each parametrized case to a fetch."""
    with BettingApiClient(base_url=config.base_url, user_id=config.user_id) as client:
        matches = client.get_matches().body
    assert matches, "API returned no matches — cannot exercise place-bet"
    return matches[0]["id"]


@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.parametrize(
    "stake",
    [0.99, 100.01],
    ids=["just-below-min", "just-above-max"],
)
def test_stake_outside_bounds_is_rejected(
    api_client: BettingApiClient, match_id: str, stake: float
) -> None:
    """Stakes outside [1.00, 100.00] must be rejected with HTTP 422 and the
    documented error code. A rejection at any other status (200/400/500) means
    either the rule is broken or error handling is wrong."""
    response = api_client.place_bet(match_id, SELECTION_HOME, stake)

    assert response.status_code == 422, (
        f"Expected 422 for out-of-range stake {stake}, got {response.status_code}: {response.body}"
    )
    expected_code = "invalid_stake_min" if stake < 1 else "invalid_stake_max"
    assert response.body.get("error") == expected_code, (
        f"Expected error code {expected_code!r}, got {response.body!r}"
    )


@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.parametrize(
    "stake",
    [1.00, 1.01, 99.99, 100.00],
    ids=["min-boundary", "just-inside-min", "just-inside-max", "max-boundary"],
)
def test_stake_inside_bounds_is_accepted(
    reset_balance,
    api_client: BettingApiClient,
    match_id: str,
    stake: float,
) -> None:
    """Stakes in [1.00, 100.00] must succeed and deduct the stake from balance.

    We reset the balance before each case so a €100 bet doesn't starve a
    later run, and we compare the API's returned `balance` field against the
    pre-bet balance — both are server-authoritative, so this avoids any
    assumption about the actual starting amount.
    """
    balance_before = api_client.get_balance().body["balance"]

    response = api_client.place_bet(match_id, SELECTION_HOME, stake)

    assert response.status_code == 200, (
        f"Expected 200 for in-range stake {stake}, got {response.status_code}: {response.body}"
    )
    body = response.body
    assert body.get("message") == "Bet placed successfully"
    assert body.get("stake") == pytest.approx(stake), (
        f"Response stake {body.get('stake')} should match request stake {stake}"
    )
    assert body.get("balance") == pytest.approx(balance_before - stake, abs=0.01), (
        f"Balance should be reduced by exactly {stake} "
        f"(before={balance_before}, after={body.get('balance')})"
    )
