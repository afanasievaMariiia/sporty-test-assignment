"""Thin requests-based client for the Sports Betting API.

Endpoints (see /api/docs Swagger spec):
    GET  /api/matches        list upcoming matches
    GET  /api/balance        current balance
    POST /api/place-bet      place a bet
    POST /api/reset-balance  reset the user's balance

All endpoints require the `x-user-id` header.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


# Selection values the API accepts.
SELECTION_HOME = "HOME"
SELECTION_DRAW = "DRAW"
SELECTION_AWAY = "AWAY"
SELECTIONS = (SELECTION_HOME, SELECTION_DRAW, SELECTION_AWAY)


@dataclass(frozen=True)
class ApiResponse:
    """Result of any API call — exposes both the parsed body and the status code.

    Tests assert on both: a 200 with the wrong body is still a failure, and a
    422 with the right error code is a pass for negative cases.
    """
    status_code: int
    body: Any

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 300


class BettingApiClient:
    def __init__(self, base_url: str, user_id: str, timeout: float = 10.0):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "x-user-id": user_id,
            "Accept": "application/json",
        })

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "BettingApiClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def _request(self, method: str, path: str, **kwargs: Any) -> ApiResponse:
        url = f"{self._base_url}{path}"
        response = self._session.request(method, url, timeout=self._timeout, **kwargs)
        try:
            body = response.json()
        except ValueError:
            body = response.text
        return ApiResponse(status_code=response.status_code, body=body)

    def get_matches(self) -> ApiResponse:
        return self._request("GET", "/api/matches")

    def get_balance(self) -> ApiResponse:
        return self._request("GET", "/api/balance")

    def reset_balance(self) -> ApiResponse:
        return self._request("POST", "/api/reset-balance")

    def place_bet(self, match_id: str, selection: str, stake: float) -> ApiResponse:
        payload = {"matchId": match_id, "selection": selection, "stake": stake}
        return self._request("POST", "/api/place-bet", json=payload)
