"""Bet receipt — the success modal shown after a bet is placed."""
from __future__ import annotations

from dataclasses import dataclass

from selenium.webdriver.common.by import By

from .base_page import BasePage


@dataclass(frozen=True)
class ReceiptSnapshot:
    bet_id: str
    match: str
    stake: float
    odds: float
    payout: float
    placed_at: str


class BetReceipt(BasePage):
    MODAL = (By.ID, "modal-success")
    BET_ID = (By.ID, "modal-success-bet-id")
    MATCH = (By.ID, "modal-success-match")
    STAKE = (By.ID, "modal-success-stake")
    ODDS = (By.ID, "modal-success-odds")
    PAYOUT = (By.ID, "modal-success-payout")
    PLACED_AT = (By.ID, "modal-success-placed-at")
    CLOSE_BUTTON = (By.ID, "modal-success-close")

    def wait_until_visible(self) -> None:
        self.find_visible(self.MODAL)

    def snapshot(self) -> ReceiptSnapshot:
        self.wait_until_visible()
        return ReceiptSnapshot(
            bet_id=self.text_of(self.BET_ID),
            match=self.text_of(self.MATCH),
            stake=self.parse_euro(self.text_of(self.STAKE)),
            odds=self.parse_euro(self.text_of(self.ODDS)),
            payout=self.parse_euro(self.text_of(self.PAYOUT)),
            placed_at=self.text_of(self.PLACED_AT),
        )

    def close(self) -> None:
        self.find_clickable(self.CLOSE_BUTTON).click()
        self.wait_until_gone(self.MODAL)
